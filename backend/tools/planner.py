"""Tools do Planejador (PLANNER.md, TOOLS.md).

Só leitura: nenhuma delas altera `tasks`/`events`. `reorganize_day`
devolve uma PROPOSTA — a aplicação real acontece por `update_task`/
`update_event` normais, chamados pelo LLM só depois de o usuário
confirmar (BUSINESS_RULES.md #12, FLOWS.md item 5). O LLM nunca calcula
a ordem sozinho — só interpreta o resultado já pronto do Planejador
(ARCHITECTURE.md)."""

from typing import Any, Optional

from sqlalchemy.orm import Session

from db.models.user import User
from llm.base import ToolSpec
from planner.daily_plan import DailyPlan, PlanItem, compute_daily_plan, compute_reorganized_plan
from tools.base import ToolDefinition
from tools.errors import ToolNotFoundError


def _get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise ToolNotFoundError(f"usuário {user_id} não encontrado")
    return user


def _serialize_item(item: PlanItem) -> dict[str, Any]:
    return {
        "kind": item.kind,
        "id": item.id,
        "title": item.title,
        "period": item.period,
        "start_at": item.start_at.isoformat() if item.start_at else None,
        "priority": item.priority.value if item.priority else None,
        "reason": item.reason,
        "suggested_due_date": (
            item.suggested_due_date.isoformat() if item.suggested_due_date else None
        ),
    }


def _serialize_plan(plan: DailyPlan) -> dict[str, Any]:
    return {
        "date": plan.plan_date.isoformat(),
        "items": [_serialize_item(item) for item in plan.items],
    }


def get_daily_plan(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    user = _get_user(db, user_id)
    plan = compute_daily_plan(db, user)
    return _serialize_plan(plan)


def reorganize_day(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    user = _get_user(db, user_id)
    energy_level: Optional[str] = arguments.get("energy_level")
    plan = compute_reorganized_plan(db, user, energy_level=energy_level)
    return _serialize_plan(plan)


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="get_daily_plan",
            description=(
                "Monta o plano do dia de hoje (lista ordenada de tarefas e "
                "compromissos), calculado pelo sistema — você nunca "
                "recalcula essa ordem sozinho. Compromissos e tarefas com "
                "horário marcado aparecem no horário certo; tarefas sem "
                "horário são ordenadas por prioridade e, quando existe um "
                "padrão de rotina ativo para a categoria, posicionadas no "
                "período do dia sugerido por esse padrão."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=get_daily_plan,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="reorganize_day",
            description=(
                "Propõe uma reorganização do plano de hoje a partir de uma "
                "restrição já interpretada por você a partir da mensagem do "
                "usuário (ex.: 'estou cansado hoje' -> energy_level='low'). "
                "Só sugere — não altera nenhuma tarefa ou compromisso "
                "sozinha. Se o usuário aceitar a proposta, aplique com "
                "update_task/update_event normais, chamada por chamada, só "
                "depois da confirmação explícita. energy_level='low' é o "
                "único valor com efeito definido por enquanto: tarefas sem "
                "horário marcado e de maior esforço (prioridade alta e/ou "
                "com Pomodoro habilitado) aparecem no fim da lista, com uma "
                "sugestão de adiar para amanhã; eventos fixos nunca são "
                "tocados. Outros valores devolvem o mesmo plano de "
                "get_daily_plan, sem inventar um efeito que não existe."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "energy_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": (
                            "Nível de energia do usuário hoje, já interpretado "
                            "por você a partir da mensagem. Só 'low' muda a "
                            "ordem do plano."
                        ),
                    },
                },
            },
        ),
        execute=reorganize_day,
    ),
]
