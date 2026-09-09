"""Ponto único de conclusão de tarefa.

Antes da completude da FASE 8 havia quatro caminhos independentes que
marcavam `tasks.status = done`: `tools/tasks.py:complete_task`,
`tools/tasks.py:update_task` (via campo `status`), e os equivalentes em
`api/routers/tasks.py` (`POST /tasks/{id}/complete` e `PATCH /tasks/{id}`).
Todos passam a chamar `complete_task` daqui, para que o gancho de domínio
`on_task_completed` (FASE 9) tenha um lugar só onde se ligar.

Não dá `commit` — quem chama já é dono da transação (mesma regra das
tools, ARCHITECTURE.md)."""

from datetime import datetime

from sqlalchemy.orm import Session

from core.domain_events import on_task_completed
from db.models.enums import TaskStatus
from db.models.task import Task


def complete_task(db: Session, user_id: int, task: Task) -> None:
    """Marca a tarefa como concluída e dispara o gancho de domínio.

    Idempotente: se a tarefa já estava `done`, não redispara o gancho
    (evita XP/reação em dobro na FASE 9 quando um `update_task` reescreve
    `status=done` numa tarefa já concluída)."""
    if task.status == TaskStatus.DONE:
        return
    task.status = TaskStatus.DONE
    task.updated_at = datetime.utcnow()
    on_task_completed(db, user_id, task)
