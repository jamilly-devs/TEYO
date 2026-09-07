"""Tools de Tarefas (MODULES/TASKS.md, TOOLS.md).

Reaproveita os schemas Pydantic de `api/schemas/task.py` para validação —
mesma validação usada pela tela e pela conversa (API.md: 'mesma ação
possível tanto pela tela quanto pela conversa, com a mesma validação de
regras de negócio')."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.schemas.task import TaskCreate, TaskOut, TaskUpdate
from db.models.enums import TaskCategory, TaskPriority, TaskStatus
from db.models.goal import Goal
from db.models.task import Task
from llm.base import ToolSpec
from tools.base import ToolDefinition
from tools.errors import ToolNotFoundError, ToolValidationError, format_validation_error, require_id


def _get_owned_task(db: Session, user_id: int, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.user_id != user_id:
        raise ToolNotFoundError(f"tarefa {task_id} não encontrada")
    return task


def _validate_goal_ownership(db: Session, user_id: int, goal_id: int) -> None:
    goal = db.get(Goal, goal_id)
    if goal is None or goal.user_id != user_id:
        raise ToolNotFoundError(f"objetivo {goal_id} não encontrado")


def _serialize(task: Task) -> dict[str, Any]:
    return TaskOut.model_validate(task).model_dump(mode="json")


def create_task(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = TaskCreate(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    if payload.goal_id is not None:
        _validate_goal_ownership(db, user_id, payload.goal_id)

    task = Task(user_id=user_id, **payload.model_dump(exclude_unset=True))
    db.add(task)
    db.commit()
    db.refresh(task)
    return _serialize(task)


def update_task(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    task_id = require_id(arguments, "task_id")
    task = _get_owned_task(db, user_id, task_id)

    rest = {key: value for key, value in arguments.items() if key != "task_id"}
    try:
        payload = TaskUpdate(**rest)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    fields = payload.model_dump(exclude_unset=True)
    if fields.get("goal_id") is not None:
        _validate_goal_ownership(db, user_id, fields["goal_id"])

    for field, value in fields.items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return _serialize(task)


def delete_task(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    task_id = require_id(arguments, "task_id")
    task = _get_owned_task(db, user_id, task_id)
    db.delete(task)
    db.commit()
    return {"deleted": True, "task_id": task_id}


def complete_task(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    """Marca a tarefa como concluída. O efeito colateral de gamificação
    citado em TOOLS.md (`gamification_events` / `mascot_state`) é FASE 9 —
    ainda não existe (`backend/gamification`, `backend/mascot` estão
    vazios) e não é implementado aqui."""
    task_id = require_id(arguments, "task_id")
    task = _get_owned_task(db, user_id, task_id)
    task.status = TaskStatus.DONE
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return _serialize(task)


def list_tasks(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    tasks = db.query(Task).filter_by(user_id=user_id).all()
    return {"items": [_serialize(task) for task in tasks]}


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="create_task",
            description="Cria uma tarefa nova para o usuário.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Título da tarefa."},
                    "description": {"type": "string"},
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": (
                            "Data/hora limite em ISO 8601, já resolvida pelo "
                            "Orquestrador a partir da linguagem natural — nunca "
                            "texto livre como 'amanhã'."
                        ),
                    },
                    "priority": {"type": "string", "enum": [p.value for p in TaskPriority]},
                    "category": {"type": "string", "enum": [c.value for c in TaskCategory]},
                    "goal_id": {
                        "type": "integer",
                        "description": "Objetivo ao qual a tarefa se associa, se houver.",
                    },
                    "pomodoro_enabled": {"type": "boolean"},
                },
                "required": ["title"],
            },
        ),
        execute=create_task,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="update_task",
            description=(
                "Atualiza campos de uma tarefa existente. Requer task_id já "
                "resolvido sem ambiguidade — use list_tasks se precisar "
                "identificar qual tarefa o usuário quer dizer."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": [s.value for s in TaskStatus]},
                    "due_date": {"type": "string", "format": "date-time"},
                    "priority": {"type": "string", "enum": [p.value for p in TaskPriority]},
                    "category": {"type": "string", "enum": [c.value for c in TaskCategory]},
                    "is_recurring": {"type": "boolean"},
                    "pomodoro_enabled": {"type": "boolean"},
                    "goal_id": {"type": "integer"},
                },
                "required": ["task_id"],
            },
        ),
        execute=update_task,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="delete_task",
            description=(
                "Exclui uma tarefa permanentemente. AÇÃO DESTRUTIVA: só chame "
                "depois que o usuário confirmar explicitamente, na conversa, "
                "que quer excluir esta tarefa específica."
            ),
            parameters={
                "type": "object",
                "properties": {"task_id": {"type": "integer"}},
                "required": ["task_id"],
            },
        ),
        execute=delete_task,
        destructive=True,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="complete_task",
            description="Marca uma tarefa como concluída.",
            parameters={
                "type": "object",
                "properties": {"task_id": {"type": "integer"}},
                "required": ["task_id"],
            },
        ),
        execute=complete_task,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="list_tasks",
            description=(
                "Lista as tarefas existentes do usuário. Use para consultar o "
                "que existe ou para resolver a qual tarefa uma mensagem "
                "ambígua se refere antes de chamar update_task/delete_task/"
                "complete_task."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=list_tasks,
    ),
]
