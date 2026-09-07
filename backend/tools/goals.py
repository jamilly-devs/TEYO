"""Tools de Objetivos (MODULES/GOALS.md, TOOLS.md).

Sem delete_goal: nem TOOLS.md nem API.md definem exclusão de objetivo (só
GET/POST/PATCH) — não é criada aqui."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.schemas.goal import GoalCreate, GoalOut, GoalUpdate
from db.models.enums import GoalStatus
from db.models.goal import Goal
from llm.base import ToolSpec
from tools.base import ToolDefinition
from tools.errors import ToolNotFoundError, ToolValidationError, format_validation_error, require_id


def _get_owned_goal(db: Session, user_id: int, goal_id: int) -> Goal:
    goal = db.get(Goal, goal_id)
    if goal is None or goal.user_id != user_id:
        raise ToolNotFoundError(f"objetivo {goal_id} não encontrado")
    return goal


def _serialize(goal: Goal) -> dict[str, Any]:
    return GoalOut.model_validate(goal).model_dump(mode="json")


def create_goal(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = GoalCreate(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    goal = Goal(user_id=user_id, **payload.model_dump(exclude_unset=True))
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _serialize(goal)


def update_goal(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    goal_id = require_id(arguments, "goal_id")
    goal = _get_owned_goal(db, user_id, goal_id)

    rest = {key: value for key, value in arguments.items() if key != "goal_id"}
    try:
        payload = GoalUpdate(**rest)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return _serialize(goal)


def list_goals(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    goals = db.query(Goal).filter_by(user_id=user_id).all()
    return {"items": [_serialize(goal) for goal in goals]}


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="create_goal",
            description="Cria um objetivo de médio/longo prazo para o usuário.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "target_date": {"type": "string", "format": "date"},
                },
                "required": ["title"],
            },
        ),
        execute=create_goal,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="update_goal",
            description=(
                "Atualiza campos de um objetivo existente. Requer goal_id já "
                "resolvido sem ambiguidade — use list_goals se precisar "
                "identificar qual objetivo o usuário quer dizer. O progresso "
                "do objetivo é calculado pelo sistema a partir das tarefas "
                "associadas concluídas — não é um campo editável aqui."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "goal_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": [s.value for s in GoalStatus]},
                    "target_date": {"type": "string", "format": "date"},
                },
                "required": ["goal_id"],
            },
        ),
        execute=update_goal,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="list_goals",
            description=(
                "Lista os objetivos existentes do usuário. Use para consultar "
                "ou resolver a qual objetivo uma mensagem ambígua se refere "
                "antes de chamar update_goal."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=list_goals,
    ),
]
