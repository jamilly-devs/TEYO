"""Tools de Hábitos (MODULES/HABITS.md, TOOLS.md — FASE 10).

`create_habit` / `list_habits` / `update_habit` / `log_habit`. Sem
`delete_habit` (segue Objetivos; `API.md` não define exclusão). A
gamificação NÃO é chamada aqui — `log_habit` delega a `habits.service`,
que dispara `on_habit_logged`; o subscriber de gamificação faz o XP
(regra `XP_HABIT_LOGGED` já existente desde a FASE 9)."""

from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.schemas.habit import HabitCreate, HabitOut, HabitUpdate
from db.models.habit import Habit
from habits.service import log_habit as _log_habit_service
from habits.streak import individual_streak
from llm.base import ToolSpec
from tools.base import ToolDefinition
from tools.errors import ToolNotFoundError, ToolValidationError, format_validation_error, require_id


def _get_owned_habit(db: Session, user_id: int, habit_id: int) -> Habit:
    habit = db.get(Habit, habit_id)
    if habit is None or habit.user_id != user_id:
        raise ToolNotFoundError(f"hábito {habit_id} não encontrado")
    return habit


def _serialize(db: Session, habit: Habit) -> dict[str, Any]:
    data = HabitOut.model_validate(habit).model_dump(mode="json")
    data["streak"] = individual_streak(db, habit.id)
    return data


def create_habit(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = HabitCreate(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    habit = Habit(user_id=user_id, **payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return _serialize(db, habit)


def update_habit(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    habit_id = require_id(arguments, "habit_id")
    habit = _get_owned_habit(db, user_id, habit_id)

    rest = {key: value for key, value in arguments.items() if key != "habit_id"}
    try:
        payload = HabitUpdate(**rest)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    db.commit()
    db.refresh(habit)
    return _serialize(db, habit)


def list_habits(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    habits = db.query(Habit).filter_by(user_id=user_id).all()
    return {"items": [_serialize(db, habit) for habit in habits]}


def log_habit(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    habit_id = require_id(arguments, "habit_id")
    habit = _get_owned_habit(db, user_id, habit_id)
    result = _log_habit_service(db, user_id, habit)
    db.commit()
    return {
        "habit_id": habit.id,
        "logged_at": result["log"].completed_at.isoformat(),
        "already_logged_today": not result["created"],
        "streak": individual_streak(db, habit.id),
    }


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="create_habit",
            description=(
                "Cria um hábito recorrente. frequency_target é quantos dias "
                "por semana (1 a 7) o usuário quer cumprir o hábito."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "frequency_target": {"type": "integer", "minimum": 1, "maximum": 7},
                },
                "required": ["title", "frequency_target"],
            },
        ),
        execute=create_habit,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="update_habit",
            description=(
                "Atualiza título ou frequência-alvo de um hábito. Requer "
                "habit_id já resolvido sem ambiguidade — use list_habits se "
                "precisar identificar qual hábito o usuário quer dizer."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "habit_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "frequency_target": {"type": "integer", "minimum": 1, "maximum": 7},
                },
                "required": ["habit_id"],
            },
        ),
        execute=update_habit,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="list_habits",
            description=(
                "Lista os hábitos do usuário com o streak (semanas seguidas "
                "batendo a frequência-alvo) calculado pelo sistema. Use para "
                "consultar ou resolver a qual hábito uma mensagem ambígua se "
                "refere antes de update_habit/log_habit."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=list_habits,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="log_habit",
            description=(
                "Registra que o usuário cumpriu o hábito hoje. Requer "
                "habit_id resolvido sem ambiguidade. Idempotente por dia: se "
                "já houver registro do hábito hoje, não cria outro nem conta "
                "de novo (o retorno traz already_logged_today=true)."
            ),
            parameters={
                "type": "object",
                "properties": {"habit_id": {"type": "integer"}},
                "required": ["habit_id"],
            },
        ),
        execute=log_habit,
    ),
]
