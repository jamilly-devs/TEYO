"""Integração Hábitos ↔ Gamificação/Mascote (FASE 10).

`log_habit` dispara `on_habit_logged`; a gamificação reutiliza
`XP_HABIT_LOGGED` e o `event_type` `habit_logged` já preparados na FASE 9
— nenhuma regra de XP nova, nenhuma lógica de gamificação em tools/router.
O streak GLOBAL da FASE 9 não é alterado (só passa a haver eventos reais).
"""

from db.models.gamification import GamificationEvent, GamificationState
from db.models.habit import Habit
from gamification import config
from mascot import engine as mascot_engine
from tools.habits import log_habit


def _habit(db, user_id) -> Habit:
    habit = Habit(user_id=user_id, title="ler", frequency_target=3)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def test_first_log_of_day_awards_habit_xp(db_session, user_id):
    habit = _habit(db_session, user_id)

    log_habit(db_session, user_id, {"habit_id": habit.id})

    state = db_session.get(GamificationState, user_id)
    assert state.xp_total == config.XP_HABIT_LOGGED
    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="habit_logged")
        .count()
        == 1
    )


def test_second_log_same_day_does_not_award_again(db_session, user_id):
    habit = _habit(db_session, user_id)

    log_habit(db_session, user_id, {"habit_id": habit.id})
    log_habit(db_session, user_id, {"habit_id": habit.id})

    assert db_session.get(GamificationState, user_id).xp_total == config.XP_HABIT_LOGGED
    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="habit_logged")
        .count()
        == 1
    )


def test_habit_log_makes_mascot_happy(db_session, user_id):
    habit = _habit(db_session, user_id)

    log_habit(db_session, user_id, {"habit_id": habit.id})

    assert (
        mascot_engine.resolve_state(db_session, user_id)["current_expression"] == "happy"
    )


def test_habit_logged_feeds_global_streak_without_changing_its_definition(db_session, user_id):
    # "habit_logged" já estava em STREAK_QUALIFYING_EVENTS desde a FASE 9;
    # a FASE 10 não altera a definição do streak global — só passa a haver
    # eventos reais para ele consumir. (A fórmula é testada de forma
    # determinística em test_gamification_streak.py.)
    assert config.STREAK_QUALIFYING_EVENTS == (
        "task_completed",
        "pomodoro_completed",
        "habit_logged",
    )
    habit = _habit(db_session, user_id)
    log_habit(db_session, user_id, {"habit_id": habit.id})

    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="habit_logged")
        .count()
        == 1
    )
