"""Planejador — Plano do Dia (PLANNER.md), algoritmo confirmado com Jams
na FASE 8 (ver DOCUMENTATION_AUDIT.md): eventos fixos como âncoras;
tarefas com due_date ordenadas por horário; tarefas sem due_date por
prioridade, com padrões `task_time_of_day` ativos como critério adicional
de posicionamento no período do dia; created_at como desempate final."""

from datetime import datetime, timedelta

from db.models.enums import EventSource, TaskCategory, TaskPriority, TaskStatus
from db.models.event import Event
from db.models.task import Task
from db.models.user import User
from planner.daily_plan import compute_daily_plan, compute_reorganized_plan, find_overlapping_events

NOW = datetime(2026, 9, 7, 12, 0, 0)
TODAY = NOW.date()


def _user(db, user_id) -> User:
    return db.get(User, user_id)


def _event(db, user_id, hour, minute=0, title="evento", day_offset=0):
    start = datetime.combine(TODAY, datetime.min.time()) + timedelta(
        days=day_offset, hours=hour, minutes=minute
    )
    event = Event(
        user_id=user_id,
        title=title,
        start_at=start,
        end_at=start + timedelta(hours=1),
        source=EventSource.MANUAL,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def _task(
    db,
    user_id,
    title="tarefa",
    due_hour=None,
    day_offset=0,
    priority=TaskPriority.MEDIUM,
    category=None,
    status=TaskStatus.PENDING,
    pomodoro_enabled=False,
):
    due_date = None
    if due_hour is not None:
        due_date = datetime.combine(TODAY, datetime.min.time()) + timedelta(
            days=day_offset, hours=due_hour
        )
    task = Task(
        user_id=user_id,
        title=title,
        due_date=due_date,
        priority=priority,
        category=category,
        status=status,
        pomodoro_enabled=pomodoro_enabled,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def _patch_now(monkeypatch):
    """Trava datetime.utcnow() do Motor de Padrões (usado internamente pelo
    Planejador para consultar padrões ativos) no mesmo instante de
    referência usado para seed do histórico sintético — mesma técnica de
    tests/integration/test_tools_patterns.py:_patch_now."""
    import pattern_engine.task_time_of_day as engine

    class _FixedDatetime(datetime):
        @classmethod
        def utcnow(cls):
            return NOW

    monkeypatch.setattr(engine, "datetime", _FixedDatetime)


def _seed_active_studies_pattern(db, user_id):
    """21 dias com predomínio de manhã (>= 80%) para task_time_of_day:studies
    — mesma forma de histórico sintético de test_pattern_engine.py."""
    for offset in range(1, 19):
        when = NOW - timedelta(days=offset)
        when = when.replace(hour=8, minute=0, second=0, microsecond=0)
        task = Task(
            user_id=user_id,
            title="estudo concluído",
            category=TaskCategory.STUDIES,
            status=TaskStatus.DONE,
            updated_at=when,
        )
        db.add(task)
    for offset in (19, 20, 21):
        when = (NOW - timedelta(days=offset)).replace(hour=20, minute=0, second=0, microsecond=0)
        task = Task(
            user_id=user_id,
            title="estudo concluído",
            category=TaskCategory.STUDIES,
            status=TaskStatus.DONE,
            updated_at=when,
        )
        db.add(task)
    db.commit()


def test_events_are_anchored_and_ordered_chronologically(db_session, user_id):
    _event(db_session, user_id, hour=14, title="tarde")
    _event(db_session, user_id, hour=8, title="manhã")

    plan = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)

    titles = [item.title for item in plan.items]
    assert titles == ["manhã", "tarde"]
    assert plan.items[0].period == "manhã"
    assert plan.items[1].period == "tarde"


def test_task_with_due_date_today_is_anchored_by_its_hour(db_session, user_id):
    _task(db_session, user_id, title="revisão", due_hour=19)

    plan = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)

    assert len(plan.items) == 1
    assert plan.items[0].kind == "task"
    assert plan.items[0].period == "noite"


def test_task_due_tomorrow_is_not_included_today(db_session, user_id):
    _task(db_session, user_id, title="amanhã", due_hour=9, day_offset=1)

    plan = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)

    assert plan.items == []


def test_done_and_cancelled_tasks_are_never_included(db_session, user_id):
    _task(db_session, user_id, title="feita", due_hour=9, status=TaskStatus.DONE)
    _task(db_session, user_id, title="cancelada", status=TaskStatus.CANCELLED)

    plan = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)

    assert plan.items == []


def test_unanchored_tasks_ordered_by_priority_then_created_at(db_session, user_id):
    low = _task(db_session, user_id, title="baixa", priority=TaskPriority.LOW)
    high = _task(db_session, user_id, title="alta", priority=TaskPriority.HIGH)
    high2 = _task(db_session, user_id, title="alta2", priority=TaskPriority.HIGH)

    plan = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)

    titles = [item.title for item in plan.items]
    assert titles == ["alta", "alta2", "baixa"]
    assert high.created_at <= high2.created_at


def test_unanchored_task_is_positioned_in_active_pattern_period(db_session, user_id, monkeypatch):
    _patch_now(monkeypatch)
    _seed_active_studies_pattern(db_session, user_id)
    pending = _task(
        db_session, user_id, title="ler capítulo", category=TaskCategory.STUDIES, priority=TaskPriority.LOW
    )

    plan = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)

    matching = [item for item in plan.items if item.id == pending.id]
    assert len(matching) == 1
    assert matching[0].period == "manhã"


def test_unanchored_task_without_active_pattern_goes_to_trailing_group(
    db_session, user_id, monkeypatch
):
    _patch_now(monkeypatch)
    no_category_high = _task(db_session, user_id, title="sem categoria", priority=TaskPriority.HIGH)
    _event(db_session, user_id, hour=10, title="evento manhã")

    plan = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)

    # o item sem período fica depois de todos os buckets/âncoras, mesmo com
    # prioridade alta — não existe dado para posicioná-lo em outro lugar.
    assert plan.items[-1].id == no_category_high.id
    assert plan.items[-1].period is None


def test_daily_plan_is_isolated_by_user_id(db_session, user_id, other_user_id):
    _task(db_session, other_user_id, title="de outro usuário", priority=TaskPriority.HIGH)

    plan = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)

    assert plan.items == []


def test_reorganize_day_low_energy_defers_high_priority_and_pomodoro_unanchored_tasks(
    db_session, user_id
):
    light = _task(db_session, user_id, title="leve", priority=TaskPriority.LOW)
    heavy_priority = _task(db_session, user_id, title="pesada", priority=TaskPriority.HIGH)
    heavy_pomodoro = _task(
        db_session, user_id, title="pomodoro", priority=TaskPriority.LOW, pomodoro_enabled=True
    )
    anchored_high = _task(db_session, user_id, title="ancorada", due_hour=9, priority=TaskPriority.HIGH)

    plan = compute_reorganized_plan(
        db_session, _user(db_session, user_id), energy_level="low", now=NOW
    )

    by_id = {item.id: item for item in plan.items}
    assert by_id[light.id].reason is None
    assert by_id[anchored_high.id].reason is None  # âncora nunca é tocada
    assert by_id[heavy_priority.id].reason is not None
    assert by_id[heavy_priority.id].suggested_due_date == TODAY + timedelta(days=1)
    assert by_id[heavy_pomodoro.id].reason is not None

    # tarefas adiadas vêm depois das mantidas
    ids_in_order = [item.id for item in plan.items]
    assert ids_in_order.index(heavy_priority.id) > ids_in_order.index(light.id)
    assert ids_in_order.index(heavy_pomodoro.id) > ids_in_order.index(light.id)


def test_reorganize_day_without_low_energy_matches_daily_plan(db_session, user_id):
    _task(db_session, user_id, title="alta", priority=TaskPriority.HIGH)

    baseline = compute_daily_plan(db_session, _user(db_session, user_id), now=NOW)
    for level in (None, "medium", "high"):
        reorganized = compute_reorganized_plan(
            db_session, _user(db_session, user_id), energy_level=level, now=NOW
        )
        assert [item.title for item in reorganized.items] == [item.title for item in baseline.items]
        assert all(item.reason is None for item in reorganized.items)


def test_find_overlapping_events_detects_real_overlap_not_touching_boundaries(db_session, user_id):
    existing = _event(db_session, user_id, hour=14, title="existente")

    touching_before = find_overlapping_events(
        db_session, user_id, existing.start_at - timedelta(hours=1), existing.start_at
    )
    touching_after = find_overlapping_events(
        db_session, user_id, existing.end_at, existing.end_at + timedelta(hours=1)
    )
    real_overlap = find_overlapping_events(
        db_session,
        user_id,
        existing.start_at + timedelta(minutes=30),
        existing.end_at + timedelta(minutes=30),
    )

    assert touching_before == []
    assert touching_after == []
    assert [e.id for e in real_overlap] == [existing.id]


def test_find_overlapping_events_excludes_given_event_id(db_session, user_id):
    existing = _event(db_session, user_id, hour=14, title="existente")

    conflicts = find_overlapping_events(
        db_session, user_id, existing.start_at, existing.end_at, exclude_event_id=existing.id
    )

    assert conflicts == []


def test_find_overlapping_events_isolated_by_user_id(db_session, user_id, other_user_id):
    other_event = _event(db_session, other_user_id, hour=14, title="de outro usuário")

    conflicts = find_overlapping_events(
        db_session, user_id, other_event.start_at, other_event.end_at
    )

    assert conflicts == []
