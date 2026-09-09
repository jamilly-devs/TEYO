"""core/domain_events.py — contrato do despachante síncrono da FASE 9:
subscribers isolados (um que falha não derruba os outros nem a ação de
origem) e registro idempotente."""

import pytest

from core import domain_events


@pytest.fixture()
def isolated_bus():
    saved = {name: list(fns) for name, fns in domain_events._subscribers.items()}
    domain_events.clear_subscribers()
    try:
        yield domain_events
    finally:
        domain_events.clear_subscribers()
        domain_events._subscribers.update(saved)


def test_failing_subscriber_does_not_break_others_or_caller(isolated_bus, caplog):
    seen = []

    def boom(**_):
        raise RuntimeError("boom")

    isolated_bus.subscribe("evt", boom)
    isolated_bus.subscribe("evt", lambda **payload: seen.append(payload))

    isolated_bus.emit("evt", x=1)  # não levanta a exceção do subscriber

    assert seen == [{"x": 1}]  # o subscriber seguinte rodou mesmo assim
    assert "falhou para o evento 'evt'" in caplog.text  # foi logado como WARNING


def test_subscribe_is_idempotent(isolated_bus):
    calls = []

    def handler(**payload):
        calls.append(payload)

    isolated_bus.subscribe("evt", handler)
    isolated_bus.subscribe("evt", handler)
    isolated_bus.emit("evt")

    assert len(calls) == 1


def test_emit_without_subscribers_is_noop(isolated_bus):
    isolated_bus.emit("sem_ninguem", a=1)  # não levanta
