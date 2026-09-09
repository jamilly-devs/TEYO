"""Motor de gamificação — aplica XP, recomputa nível, avalia conquistas.

Consome os ganchos de domínio da FASE 8 (via `gamification.subscribers`).
Nenhuma função aqui dá `commit`/`rollback`: quem originou a ação (tool,
endpoint, `core.task_completion`) é dono da transação — regra da FASE 8,
mantida. Usa `db.flush()` só para tornar as escritas visíveis às consultas
seguintes dentro da mesma transação.

Eventos derivados (`level_up`, `achievement_unlocked`) são emitidos pelo
despachante de `core.domain_events` para o mascote reagir já com o
nível/conquista persistidos.
"""

from collections import Counter
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from core import domain_events
from core.effort import is_high_effort_task
from db.models.achievement import Achievement
from db.models.gamification import GamificationEvent, GamificationState
from db.models.pomodoro import PomodoroSession
from db.models.task import Task
from gamification import config
from gamification.streak import current_streak, weekly_pomodoro_hours

TASK_COMPLETED = "task_completed"
TASK_COMPLETED_HIGH_EFFORT = "task_completed_high_effort"
POMODORO_COMPLETED = "pomodoro_completed"
HABIT_LOGGED = "habit_logged"
ACHIEVEMENT_UNLOCKED = "achievement_unlocked"


def _get_or_create_state(db: Session, user_id: int) -> GamificationState:
    state = db.get(GamificationState, user_id)
    if state is None:
        state = GamificationState(user_id=user_id, xp_total=0, level=1)
        db.add(state)
        db.flush()
    return state


def award_xp(
    db: Session,
    user_id: int,
    event_type: str,
    xp: int,
    *,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    now: Optional[datetime] = None,
) -> None:
    """Grava um `gamification_events` e soma o XP no `gamification_state`.
    Se o nível cruzar um limiar, emite `level_up`."""
    when = now or datetime.utcnow()
    db.add(
        GamificationEvent(
            user_id=user_id,
            event_type=event_type,
            xp_delta=xp,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            created_at=when,
        )
    )
    state = _get_or_create_state(db, user_id)
    before_level = state.level
    state.xp_total += xp
    state.level = config.level_for_xp(state.xp_total)
    state.updated_at = datetime.utcnow()
    db.flush()

    if state.level > before_level:
        domain_events.emit(
            domain_events.LEVEL_UP,
            db=db,
            user_id=user_id,
            from_level=before_level,
            to_level=state.level,
        )


def apply_task_completed(
    db: Session, user_id: int, task: Task, now: Optional[datetime] = None
) -> None:
    award_xp(
        db,
        user_id,
        TASK_COMPLETED,
        config.XP_TASK_COMPLETED,
        related_entity_type="task",
        related_entity_id=task.id,
        now=now,
    )
    if is_high_effort_task(task):
        award_xp(
            db,
            user_id,
            TASK_COMPLETED_HIGH_EFFORT,
            config.XP_TASK_HIGH_EFFORT_BONUS,
            related_entity_type="task",
            related_entity_id=task.id,
            now=now,
        )
    evaluate_achievements(db, user_id, now=now)


def apply_pomodoro_completed(
    db: Session, user_id: int, session: PomodoroSession, now: Optional[datetime] = None
) -> None:
    award_xp(
        db,
        user_id,
        POMODORO_COMPLETED,
        config.XP_POMODORO_COMPLETED,
        related_entity_type="pomodoro_session",
        related_entity_id=session.id,
        now=now,
    )
    evaluate_achievements(db, user_id, now=now)


def apply_habit_logged(
    db: Session,
    user_id: int,
    habit_log_id: Optional[int] = None,
    now: Optional[datetime] = None,
) -> None:
    """FASE 10 — reutiliza `config.XP_HABIT_LOGGED` e o `event_type`
    `habit_logged` já preparados na FASE 9. Nenhuma regra de XP nova. A
    idempotência por dia é do serviço de Hábitos (o hook só dispara quando
    um log NOVO é criado)."""
    award_xp(
        db,
        user_id,
        HABIT_LOGGED,
        config.XP_HABIT_LOGGED,
        related_entity_type="habit_log",
        related_entity_id=habit_log_id,
        now=now,
    )
    evaluate_achievements(db, user_id, now=now)


def _achieved(
    db: Session, user_id: int, spec: config.AchievementSpec, now: Optional[datetime]
) -> bool:
    if spec.metric == "streak":
        return current_streak(db, user_id, now=now) >= spec.threshold
    if spec.metric == "event_total":
        count = (
            db.query(GamificationEvent)
            .filter_by(user_id=user_id, event_type=spec.event_type)
            .count()
        )
        return count >= spec.threshold
    if spec.metric == "focus_day":
        rows = (
            db.query(GamificationEvent.created_at)
            .filter_by(user_id=user_id, event_type=TASK_COMPLETED_HIGH_EFFORT)
            .all()
        )
        by_day = Counter(row[0].date() for row in rows)
        return any(count >= spec.threshold for count in by_day.values())
    if spec.metric == "weekly_pomodoro_hours":
        return weekly_pomodoro_hours(db, user_id, now=now) >= spec.threshold
    return False


def evaluate_achievements(
    db: Session, user_id: int, now: Optional[datetime] = None
) -> list[str]:
    """Desbloqueia as conquistas cujo critério já foi atingido. Idempotente
    — `achievements` tem `UNIQUE(user_id, code)` e as já desbloqueadas são
    ignoradas. Devolve os códigos recém-desbloqueados."""
    unlocked = {
        row.code for row in db.query(Achievement).filter_by(user_id=user_id).all()
    }
    newly: list[str] = []
    for spec in config.ACHIEVEMENTS:
        if spec.code in unlocked:
            continue
        if not _achieved(db, user_id, spec, now):
            continue
        db.add(
            Achievement(
                user_id=user_id, code=spec.code, unlocked_at=now or datetime.utcnow()
            )
        )
        db.flush()
        newly.append(spec.code)
        award_xp(
            db,
            user_id,
            ACHIEVEMENT_UNLOCKED,
            config.XP_ACHIEVEMENT_UNLOCKED,
            related_entity_type="achievement",
            related_entity_id=None,
            now=now,
        )
        domain_events.emit(
            domain_events.ACHIEVEMENT_UNLOCKED, db=db, user_id=user_id, code=spec.code
        )
    return newly
