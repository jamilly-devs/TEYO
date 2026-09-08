"""Motor de Padrões (PATTERN_ENGINE.md) — casos sintéticos exigidos por
TESTING.md, replicando o exemplo do documento (21 dias / 18 noite / 3
manhã -> predominante noite; 7 dias recentes / 6 manhã / 1 noite ->
possível mudança) e as regras de regressão de BUSINESS_RULES.md."""

from datetime import datetime, timedelta

from db.models.enums import PatternStatus, TaskCategory, TaskStatus
from db.models.task import Task
from pattern_engine.task_time_of_day import (
    MIN_EVIDENCE,
    compute_pattern_for_category,
    refresh_patterns_for_user,
)

NOW = datetime(2026, 9, 7, 12, 0, 0)


def _at(days_ago: int, hour: int) -> datetime:
    return (NOW - timedelta(days=days_ago)).replace(hour=hour, minute=0, second=0, microsecond=0)


def _completed_task(db, user_id, category, when):
    task = Task(user_id=user_id, title="x", category=category, status=TaskStatus.DONE, updated_at=when)
    db.add(task)
    db.commit()
    return task


def test_fewer_than_minimum_evidence_creates_no_pattern(db_session, user_id):
    assert MIN_EVIDENCE == 3
    for day in range(MIN_EVIDENCE - 1):
        _completed_task(db_session, user_id, TaskCategory.HOUSE, _at(day, 20))

    result = compute_pattern_for_category(db_session, user_id, TaskCategory.HOUSE, now=NOW)
    assert result is None

    pairs = refresh_patterns_for_user(db_session, user_id, now=NOW)
    assert pairs == []


def test_replicates_testing_md_example_predominant_night_promotes_to_active(db_session, user_id):
    """21 dias, 18 noite / 3 manhã -> período predominante noite (~86%),
    sem divergência sustentada na janela recente -> active."""
    for i in range(15):
        _completed_task(db_session, user_id, TaskCategory.HOUSE, _at(8 + (i % 14), 20))
    for offset in (1, 3, 5):
        _completed_task(db_session, user_id, TaskCategory.HOUSE, _at(offset, 21))
    for offset in (20, 15, 10):
        _completed_task(db_session, user_id, TaskCategory.HOUSE, _at(offset, 8))

    result = compute_pattern_for_category(db_session, user_id, TaskCategory.HOUSE, now=NOW)

    assert result.status == PatternStatus.ACTIVE
    assert result.historical_predominant_period == "noite"
    assert result.evidence_count == 21
    assert round(result.historical_frequency, 3) == round(18 / 21, 3)
    assert result.recent_change is False


def test_replicates_testing_md_example_recent_divergence_demotes_to_deprecated(db_session, user_id):
    """Padrão histórico ainda bateria o limiar de 80% (noite), mas os
    últimos 7 dias divergem de forma sustentada (6 manhã / 1 noite,
    ~86% de confiança) -> despromovido para deprecated, sem promover
    automaticamente um novo padrão `active` para o período emergente
    (PATTERN_ENGINE.md: 'não promove automaticamente a novo padrão')."""
    for i in range(24):
        _completed_task(db_session, user_id, TaskCategory.STUDIES, _at(8 + (i % 14), 20))
    for offset in (1, 2, 3, 4, 5, 6):
        _completed_task(db_session, user_id, TaskCategory.STUDIES, _at(offset, 8))
    _completed_task(db_session, user_id, TaskCategory.STUDIES, _at(7, 20))

    result = compute_pattern_for_category(db_session, user_id, TaskCategory.STUDIES, now=NOW)

    assert result.historical_frequency >= 0.80
    assert result.status == PatternStatus.DEPRECATED
    assert result.recent_change is True
    assert result.recent_predominant_period == "manhã"
    assert round(result.recent_frequency, 3) == round(6 / 7, 3)


def test_single_recent_divergent_task_does_not_demote_active_pattern(db_session, user_id):
    """ACCEPTANCE_CRITERIA.md: 'um único evento fora do padrão não altera
    routines.status de active para deprecated.'"""
    for i in range(20):
        _completed_task(db_session, user_id, TaskCategory.GENERAL, _at(8 + (i % 14), 20))
    _completed_task(db_session, user_id, TaskCategory.GENERAL, _at(2, 8))

    result = compute_pattern_for_category(db_session, user_id, TaskCategory.GENERAL, now=NOW)

    assert result.status == PatternStatus.ACTIVE
    assert result.recent_change is False


def test_low_frequency_history_stays_candidate_not_active(db_session, user_id):
    for offset in range(5):
        _completed_task(db_session, user_id, TaskCategory.HOUSE, _at(offset + 10, 20))
    for offset in range(5):
        _completed_task(db_session, user_id, TaskCategory.HOUSE, _at(offset + 1, 8))

    result = compute_pattern_for_category(db_session, user_id, TaskCategory.HOUSE, now=NOW)

    assert result.historical_frequency < 0.80
    assert result.status == PatternStatus.CANDIDATE


def test_refresh_upserts_a_single_row_per_category_across_multiple_runs(db_session, user_id):
    for i in range(15):
        _completed_task(db_session, user_id, TaskCategory.HOUSE, _at(8 + (i % 14), 20))
    for offset in (20, 15, 10):
        _completed_task(db_session, user_id, TaskCategory.HOUSE, _at(offset, 8))

    first = refresh_patterns_for_user(db_session, user_id, now=NOW)
    second = refresh_patterns_for_user(db_session, user_id, now=NOW)

    assert len(first) == 1
    assert len(second) == 1
    assert first[0][0].id == second[0][0].id


def test_refresh_only_considers_the_requesting_users_tasks(db_session, user_id, other_user_id):
    for i in range(15):
        _completed_task(db_session, other_user_id, TaskCategory.HOUSE, _at(8 + (i % 14), 20))

    pairs = refresh_patterns_for_user(db_session, user_id, now=NOW)
    assert pairs == []
