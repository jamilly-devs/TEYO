"""Catálogo do mascote — mapeia estado do sistema para aparência.

`MASCOT.md` marca "número exato de estágios de evolução", "critério de
XP/nível que dispara cada estágio" e "lista completa de expressões e
gatilhos" como A DEFINIR. A FASE 9 adota a **DECISÃO C** (evolução
híbrida: o NÍVEL determina o estágio estrutural; CONQUISTAS desbloqueiam
elementos complementares) e mantém todos os limiares/mapas aqui,
configuráveis. Ver `DOCUMENTATION_AUDIT.md` (FASE 9).
"""

from typing import Iterable

# Conjunto mínimo de expressões reativas (o catálogo exaustivo era
# "NECESSÁRIO PARA IMPLEMENTAÇÃO / A DEFINIR" em MASCOT.md):
# idle, happy, proud, celebrating, caring, tired.
DEFAULT_EXPRESSION = "idle"

# Tempo sem novo evento após o qual a expressão volta ao repouso (só na
# leitura — "idle" não é persistido).
EXPRESSION_TTL_MIN = 90

DEFAULT_COLOR = "#7C5CFF"

# DECISÃO C — o nível dirige o estágio estrutural. (estágio, nível mínimo),
# crescente. Exemplo conceitual de MASCOT.md: inicial → cresce → roupa
# nova → evolui → coroa.
_STAGE_MIN_LEVEL = ((1, 1), (2, 3), (3, 6), (4, 10), (5, 15))


def stage_for_level(level: int) -> int:
    stage = 1
    for candidate_stage, min_level in _STAGE_MIN_LEVEL:
        if level >= min_level:
            stage = candidate_stage
    return stage


# DECISÃO C — conquistas desbloqueiam elementos COMPLEMENTARES (detalhes,
# itens, expressões extras); não alteram o estágio. Mapa extensível: novas
# conquistas/elementos entram aqui sem reestruturar o resto.
ACHIEVEMENT_FEATURE = {
    "streak_3": "detail_spark",
    "streak_7": "item_scarf",
    "streak_30": "item_crown",
    "pomodoro_1": "expression_focus",
    "pomodoro_10": "item_headphones",
    "pomodoro_50": "detail_aura",
    "focus_day": "expression_proud_plus",
    "tasks_25": "detail_badge",
    "tasks_100": "detail_badge_gold",
    "weekly_hours_5": "detail_star",
}


def features_for_achievements(codes: Iterable[str]) -> list[str]:
    return [ACHIEVEMENT_FEATURE[code] for code in codes if code in ACHIEVEMENT_FEATURE]
