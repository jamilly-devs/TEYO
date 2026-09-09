"""gamification/config.py — parâmetros de produto (FASE 9). Valores
adotados da OPÇÃO RECOMENDADA de GAMIFICATION.md, configuráveis; estes
testes travam a forma, não obrigam um número específico."""

from gamification import config


def test_level_for_xp_is_linear():
    assert config.level_for_xp(0) == 1
    assert config.level_for_xp(config.XP_PER_LEVEL - 1) == 1
    assert config.level_for_xp(config.XP_PER_LEVEL) == 2
    assert config.level_for_xp(config.XP_PER_LEVEL * 2 + 10) == 3


def test_xp_progress_splits_into_level_and_size():
    into, size = config.xp_progress(config.XP_PER_LEVEL + 25)
    assert into == 25
    assert size == config.XP_PER_LEVEL


def test_achievement_catalog_is_well_formed():
    codes = [spec.code for spec in config.ACHIEVEMENTS]
    assert len(codes) == len(set(codes)), "códigos de conquista duplicados"
    for spec in config.ACHIEVEMENTS:
        assert spec.title and spec.description
        assert spec.threshold >= 1
        if spec.metric == "event_total":
            assert spec.event_type, f"{spec.code} precisa de event_type"


def test_streak_qualifying_events_are_positive_activity():
    assert "task_completed" in config.STREAK_QUALIFYING_EVENTS
    assert "achievement_unlocked" not in config.STREAK_QUALIFYING_EVENTS
