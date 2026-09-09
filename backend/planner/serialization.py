"""Forma canônica do Plano do Dia no fio.

Único ponto de serialização de `DailyPlan` — usado pela tool
(`tools/planner.py`) e pelo endpoint (`api/routers/planner.py`), para que
"mesma ação pela tela e pela conversa" também signifique mesmo formato de
saída (API.md). O contrato é o de `TOOLS.md`:

    {"date": "AAAA-MM-DD", "items": [ {item}, ... ]}

    item: kind, id, title, period, start_at, priority, reason,
          suggested_due_date

DECIDIDO (completude da FASE 8, opção "serializer tipado, contrato
intacto"): os campos internos `DailyPlan.energy_level` /
`DailyPlan.reorganized` NÃO entram aqui — existem só para a FASE 9
estender o objeto tipado sem mexer neste contrato."""

from typing import Any

from planner.daily_plan import DailyPlan, PlanItem


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


def serialize_plan(plan: DailyPlan) -> dict[str, Any]:
    return {
        "date": plan.plan_date.isoformat(),
        "items": [_serialize_item(item) for item in plan.items],
    }
