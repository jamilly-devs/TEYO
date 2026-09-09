"""Planejador — Plano do Dia (PLANNER.md).

Não é um LLM: cálculo determinístico em Python sobre `tasks`/`events` já
existentes e sobre os padrões `active` já calculados pelo Motor de Padrões
da FASE 7 (ARCHITECTURE.md: cálculos e regras de negócio pertencem ao
sistema, nunca ao LLM — o LLM só interpreta o resultado já pronto).

Escopo real da FASE 8 (decisão registrada em DOCUMENTATION_AUDIT.md, mesmo
raciocínio da FASE 7 para o Motor de Padrões): só `tasks` + `events` +
padrões `task_time_of_day`. `habits`/`habit_logs` (sem módulo construído),
progresso de `goals` (não implementado desde a FASE 2) e um eventual
padrão `productivity_time` (nunca existiu — só `task_time_of_day` foi
implementado na FASE 7) não são usados aqui; nenhuma tabela ou tool de
fases anteriores foi alterada para passar a alimentar dado novo.

## Algoritmo de ordenação de `get_daily_plan` (DECIDIDO com Jams — Opção A
de PLANNER.md, ver DOCUMENTATION_AUDIT.md)

1. Eventos e tarefas com horário certo (`due_date` hoje) são âncoras: cada
   um cai no período do dia (madrugada/manhã/tarde/noite) da sua própria
   hora, mantendo ordem cronológica dentro do período.
2. Tarefas sem `due_date` são ordenadas primariamente por `priority`
   (alta → média → baixa, critério principal); quando existe um padrão
   `active` de `task_time_of_day` para a categoria da tarefa, ela é
   colocada no período predominante daquele padrão (critério adicional de
   posicionamento) — dentro do mesmo período, a ordem continua sendo por
   prioridade, e `created_at` decide o empate final. Tarefas sem `due_date`
   e sem padrão ativo para a categoria (ou sem categoria) formam um grupo
   "sem período" ao final da lista, para não inventar um horário que
   nenhum dado sustenta.
3. Dentro de um mesmo período, as tarefas sem horário fixo aparecem antes
   dos itens-âncora daquele período (evita fingir que o Planejador sabe
   encaixar a tarefa num horário exato entre compromissos, já que não há
   duração estimada em `tasks`/`events`)."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from core.day_window import PERIOD_ORDER, day_bounds, local_today, period_for_hour
from core.effort import is_high_effort
from db.models.enums import PatternStatus, TaskPriority, TaskStatus
from db.models.event import Event
from db.models.task import Task
from db.models.user import User
from pattern_engine.task_time_of_day import PATTERN_TYPE_PREFIX, refresh_patterns_for_user

# Definição de dia/fuso e divisão de período agora vêm de `core.day_window`
# (compartilhado com a FASE 9); "maior esforço" vem de `core.effort`.
_PRIORITY_RANK = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}
_OPEN_STATUSES = (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)


@dataclass
class PlanItem:
    kind: str  # "event" | "task"
    id: int
    title: str
    period: Optional[str]
    start_at: Optional[datetime] = None  # só quando o horário é fixo (evento ou due_date)
    priority: Optional[TaskPriority] = None  # só tasks
    pomodoro_enabled: Optional[bool] = None  # só tasks
    created_at: Optional[datetime] = None  # desempate final; não é dado de produto
    reason: Optional[str] = None  # motivo apresentado por reorganize_day
    suggested_due_date: Optional[date] = None  # sugestão de adiar (reorganize_day)


@dataclass
class DailyPlan:
    plan_date: date
    items: list[PlanItem]
    # Ecoam o pedido de `reorganize_day` para a FASE 9 estender o objeto
    # tipado (ex.: anexar expressão do mascote) sem mudar assinatura. NÃO
    # são serializados no retorno das tools/endpoints — o contrato de
    # `TOOLS.md` (`{"date", "items": [...]}`) fica byte-a-byte igual.
    energy_level: Optional[str] = None
    reorganized: bool = False


def _active_predominant_periods(db: Session, user_id: int) -> dict[str, str]:
    """categoria -> período predominante, só para padrões `active`
    (Motor de Padrões, FASE 7). Nunca recalcula a lógica de padrões aqui —
    só reconsulta o resultado já materializado por
    `refresh_patterns_for_user` (PATTERN_ENGINE.md: só o Motor calcula)."""
    pairs = refresh_patterns_for_user(db, user_id)
    periods: dict[str, str] = {}
    for row, computed in pairs:
        if not row.pattern_type.startswith(f"{PATTERN_TYPE_PREFIX}:"):
            continue
        if row.status == PatternStatus.ACTIVE and computed.historical_predominant_period:
            periods[computed.category] = computed.historical_predominant_period
    return periods


def _anchored_items(events: list[Event], tasks_with_due_date: list[Task]) -> list[PlanItem]:
    items = [
        PlanItem(
            kind="event",
            id=event.id,
            title=event.title,
            period=period_for_hour(event.start_at.hour),
            start_at=event.start_at,
        )
        for event in events
    ]
    items.extend(
        PlanItem(
            kind="task",
            id=task.id,
            title=task.title,
            period=period_for_hour(task.due_date.hour),
            start_at=task.due_date,
            priority=task.priority,
            pomodoro_enabled=task.pomodoro_enabled,
            created_at=task.created_at,
        )
        for task in tasks_with_due_date
    )
    items.sort(key=lambda item: item.start_at)
    return items


def _unanchored_sort_key(item: PlanItem) -> tuple:
    rank = _PRIORITY_RANK.get(item.priority, len(_PRIORITY_RANK))
    return (rank, item.created_at or datetime.min, item.id)


def _unanchored_items(
    tasks_without_due_date: list[Task], active_periods: dict[str, str]
) -> tuple[dict[str, list[PlanItem]], list[PlanItem]]:
    buckets: dict[str, list[PlanItem]] = {period: [] for period in PERIOD_ORDER}
    unscheduled: list[PlanItem] = []
    for task in tasks_without_due_date:
        item = PlanItem(
            kind="task",
            id=task.id,
            title=task.title,
            period=None,
            priority=task.priority,
            pomodoro_enabled=task.pomodoro_enabled,
            created_at=task.created_at,
        )
        category_value = task.category.value if task.category else None
        period = active_periods.get(category_value) if category_value else None
        if period is not None:
            item.period = period
            buckets[period].append(item)
        else:
            unscheduled.append(item)

    for period_items in buckets.values():
        period_items.sort(key=_unanchored_sort_key)
    unscheduled.sort(key=_unanchored_sort_key)
    return buckets, unscheduled


def compute_daily_plan(db: Session, user: User, now: Optional[datetime] = None) -> DailyPlan:
    today = local_today(user, now=now)
    day_start, day_end = day_bounds(user, now=now)

    events = (
        db.query(Event)
        .filter(Event.user_id == user.id, Event.start_at >= day_start, Event.start_at <= day_end)
        .all()
    )
    tasks_with_due_date = (
        db.query(Task)
        .filter(
            Task.user_id == user.id,
            Task.status.in_(_OPEN_STATUSES),
            Task.due_date >= day_start,
            Task.due_date <= day_end,
        )
        .all()
    )
    tasks_without_due_date = (
        db.query(Task)
        .filter(
            Task.user_id == user.id,
            Task.status.in_(_OPEN_STATUSES),
            Task.due_date.is_(None),
        )
        .all()
    )

    active_periods = _active_predominant_periods(db, user.id)
    anchored = _anchored_items(events, tasks_with_due_date)
    buckets, unscheduled = _unanchored_items(tasks_without_due_date, active_periods)

    items: list[PlanItem] = []
    for period in PERIOD_ORDER:
        items.extend(buckets[period])
        items.extend(item for item in anchored if item.period == period)
    items.extend(unscheduled)

    return DailyPlan(plan_date=today, items=items)


def compute_reorganized_plan(
    db: Session, user: User, energy_level: Optional[str] = None, now: Optional[datetime] = None
) -> DailyPlan:
    """Proposta de reorganização (PLANNER.md: "o TEYO sugere, não impõe") —
    não grava nada; a aplicação real acontece via `update_task`/
    `update_event` normais, só depois de confirmação do usuário
    (FLOWS.md item 5, BUSINESS_RULES.md #12).

    DECIDIDO com Jams (Opção A): só `energy_level == "low"` tem efeito.
    Tarefas sem horário fixo consideradas de maior esforço (`priority`
    alta e/ou `pomodoro_enabled`) são movidas para o fim da lista de hoje,
    com uma sugestão (não aplicada) de adiar para amanhã. Eventos fixos e
    tarefas já com horário marcado nunca são tocados. Qualquer outro valor
    de `energy_level` (ou nenhum) devolve o mesmo plano de
    `compute_daily_plan` — não existe métrica de esforço/produtividade
    para justificar outro comportamento sem inventar dado."""
    plan = compute_daily_plan(db, user, now=now)
    if energy_level != "low":
        plan.energy_level = energy_level
        return plan

    tomorrow = plan.plan_date + timedelta(days=1)
    kept: list[PlanItem] = []
    deferred: list[PlanItem] = []
    for item in plan.items:
        is_unanchored_task = item.kind == "task" and item.start_at is None
        is_heavy = is_unanchored_task and is_high_effort(
            priority=item.priority, pomodoro_enabled=item.pomodoro_enabled
        )
        if is_heavy:
            item.reason = (
                "Esforço mais alto (prioridade alta e/ou Pomodoro) — sugerido "
                "adiar por causa do seu nível de energia hoje."
            )
            item.suggested_due_date = tomorrow
            deferred.append(item)
        else:
            kept.append(item)

    return DailyPlan(
        plan_date=plan.plan_date,
        items=kept + deferred,
        energy_level="low",
        reorganized=True,
    )


def find_overlapping_events(
    db: Session,
    user_id: int,
    start_at: datetime,
    end_at: datetime,
    exclude_event_id: Optional[int] = None,
) -> list[Event]:
    """Duas janelas se sobrepõem quando uma começa antes da outra terminar
    e termina depois da outra começar; um evento que termina exatamente
    quando o outro começa não conta como conflito (MODULES/AGENDA.md,
    PLANNER.md — sinalizar sobreposição real, não encostar horários)."""
    query = db.query(Event).filter(
        Event.user_id == user_id,
        Event.start_at < end_at,
        Event.end_at > start_at,
    )
    if exclude_event_id is not None:
        query = query.filter(Event.id != exclude_event_id)
    return query.all()
