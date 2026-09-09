"""Tools de Carreira (MODULES/CAREER.md, TOOLS.md — FASE 10).

Acompanhamento MANUAL de candidaturas: sem busca automatizada de vagas,
sem uso de LLM para buscar (BUSINESS_RULES.md / MODULES/CAREER.md). Sem
delete_job_application — segue Objetivos e API.md, que não definem
exclusão. Reaproveita os schemas Pydantic de `api/schemas/career.py`
(mesma validação da tela)."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.schemas.career import (
    JobApplicationCreate,
    JobApplicationOut,
    JobApplicationUpdate,
)
from db.models.enums import JobApplicationStatus
from db.models.job_application import JobApplication
from llm.base import ToolSpec
from tools.base import ToolDefinition
from tools.errors import ToolNotFoundError, ToolValidationError, format_validation_error, require_id


def _get_owned(db: Session, user_id: int, app_id: int) -> JobApplication:
    application = db.get(JobApplication, app_id)
    if application is None or application.user_id != user_id:
        raise ToolNotFoundError(f"candidatura {app_id} não encontrada")
    return application


def _serialize(application: JobApplication) -> dict[str, Any]:
    return JobApplicationOut.model_validate(application).model_dump(mode="json")


def create_job_application(
    db: Session, user_id: int, arguments: dict[str, Any]
) -> dict[str, Any]:
    try:
        payload = JobApplicationCreate(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    application = JobApplication(user_id=user_id, **payload.model_dump(exclude_unset=True))
    db.add(application)
    db.commit()
    db.refresh(application)
    return _serialize(application)


def update_job_application(
    db: Session, user_id: int, arguments: dict[str, Any]
) -> dict[str, Any]:
    app_id = require_id(arguments, "application_id")
    application = _get_owned(db, user_id, app_id)

    rest = {key: value for key, value in arguments.items() if key != "application_id"}
    try:
        payload = JobApplicationUpdate(**rest)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    application.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    return _serialize(application)


def list_job_applications(
    db: Session, user_id: int, arguments: dict[str, Any]
) -> dict[str, Any]:
    applications = db.query(JobApplication).filter_by(user_id=user_id).all()
    return {"items": [_serialize(a) for a in applications]}


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="create_job_application",
            description=(
                "Registra uma candidatura a vaga para acompanhamento manual "
                "(empresa, cargo, data, status, observações). O TEYO não "
                "busca vagas automaticamente — só registra o que o usuário "
                "informa."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "role": {"type": "string", "description": "Cargo/vaga."},
                    "applied_on": {
                        "type": "string",
                        "format": "date",
                        "description": (
                            "Data da candidatura em ISO 8601, já resolvida "
                            "pelo Orquestrador — nunca texto livre."
                        ),
                    },
                    "notes": {"type": "string"},
                },
                "required": ["company", "role"],
            },
        ),
        execute=create_job_application,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="update_job_application",
            description=(
                "Atualiza uma candidatura existente (ex.: mudar o status para "
                "'interviewing' ou 'rejected'). Requer application_id já "
                "resolvido sem ambiguidade — use list_job_applications se "
                "precisar identificar qual candidatura o usuário quer dizer."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "application_id": {"type": "integer"},
                    "company": {"type": "string"},
                    "role": {"type": "string"},
                    "applied_on": {"type": "string", "format": "date"},
                    "status": {
                        "type": "string",
                        "enum": [s.value for s in JobApplicationStatus],
                    },
                    "notes": {"type": "string"},
                },
                "required": ["application_id"],
            },
        ),
        execute=update_job_application,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="list_job_applications",
            description=(
                "Lista as candidaturas registradas pelo usuário. Use para "
                "consultar ou resolver a qual candidatura uma mensagem "
                "ambígua se refere antes de chamar update_job_application."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=list_job_applications,
    ),
]
