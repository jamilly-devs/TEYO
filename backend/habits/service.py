"""Serviço de Hábitos — registro de log com idempotência por dia (DT-2) e
disparo do gancho de domínio `on_habit_logged` (FASE 10).

Não commita: quem originou a ação (router / tool) é dono da transação
(regra FASE 8). Recebe o `Habit` já validado pelo chamador (o router
levanta 404, a tool levanta ToolNotFoundError) — este módulo não conhece
`tools.errors` nem `HTTPException`.
"""

from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from core import domain_events
from core.day_window import day_bounds
from db.models.habit import Habit, HabitLog
from db.models.user import User


def _user_local_now(user: User) -> datetime:
    """"Agora" no fuso do usuário, como `datetime` ingênuo — mesmo
    referencial que `core.day_window` usa para "hoje" e que o resto do
    sistema usa para `due_date`/`start_at` (ACCEPTANCE_CRITERIA.md:
    horário no fuso do usuário, sem conversão para UTC).

    Sem isto, `completed_at` seria gravado em UTC e comparado contra a
    janela local de `day_bounds`: entre ~21:00 e 23:59 de fusos negativos
    (ex.: São Paulo, UTC-3) o timestamp cai no dia seguinte e a 2ª chamada
    do mesmo dia local não é detectada como duplicada (DT-2).
    """
    return datetime.now(ZoneInfo(user.timezone)).replace(tzinfo=None)


def log_habit(
    db: Session, user_id: int, habit: Habit, now: Optional[datetime] = None
) -> dict[str, Any]:
    """Registra a conclusão do hábito no dia. Idempotente por dia LOCAL do
    usuário (DT-2), independente da hora UTC em que roda: `completed_at` e
    a janela de `day_bounds` ficam no mesmo referencial. A 2ª chamada no
    mesmo dia local devolve o log existente, sem novo `habit_log`, sem
    novo evento de gamificação, sem novo XP.

    `now` explícito (testes) já é tratado como estando no fuso do usuário,
    mesma convenção de `core.day_window`.

    Retorna `{"log": HabitLog, "created": bool}`.
    """
    user = db.get(User, user_id)
    when = now if now is not None else _user_local_now(user)
    day_start, day_end = day_bounds(user, now=when)

    existing = (
        db.query(HabitLog)
        .filter(
            HabitLog.habit_id == habit.id,
            HabitLog.completed_at >= day_start,
            HabitLog.completed_at <= day_end,
        )
        .first()
    )
    if existing is not None:
        return {"log": existing, "created": False}

    log = HabitLog(
        habit_id=habit.id,
        user_id=user_id,
        completed_at=when,
        # DT-14: forma descrita em DATABASE.md para uso futuro do Motor de
        # Padrões — hora/dia da semana no fuso do usuário. O pattern_engine
        # NÃO é tocado nesta fase.
        context={"hour": when.hour, "weekday": when.weekday()},
    )
    db.add(log)
    db.flush()
    domain_events.on_habit_logged(db, user_id, log)
    return {"log": log, "created": True}
