"""Regras de gamificação — parâmetros de PRODUTO isolados num único lugar.

`GAMIFICATION.md` marca "quais eventos dão XP e quanto", "fórmula de
progressão de nível" e "lista final de conquistas e critérios" como
A DEFINIR por Jams. A FASE 9 adota a OPÇÃO RECOMENDADA do próprio
documento (conjunto mínimo de eventos + progressão linear simples) e
mantém TODOS os números aqui, para ratificação e ajuste futuro sem tocar
em lógica. Ver `DOCUMENTATION_AUDIT.md` (FASE 9).

Nada aqui é "invenção contra a documentação" — preenche pontos que a
própria documentação deixou abertos, de forma configurável.
"""

from dataclasses import dataclass
from typing import Optional

# --- XP por evento -----------------------------------------------------------
# `task_completed_high_effort` é um BÔNUS somado ao `task_completed` quando
# `core.effort.is_high_effort_task` for verdadeiro (mesma heurística da FASE 8).
XP_TASK_COMPLETED = 10
XP_TASK_HIGH_EFFORT_BONUS = 5
XP_POMODORO_COMPLETED = 20
XP_ACHIEVEMENT_UNLOCKED = 25

# Pendência registrada (DOCUMENTATION_AUDIT.md FASE 9): a OPÇÃO RECOMENDADA
# de GAMIFICATION.md também cita "completar hábito do dia", mas não existe
# módulo de Hábitos nem hook `on_habit_logged`. Valor deixado pronto:
XP_HABIT_LOGGED = 15

# --- Progressão de nível (linear) -----------------------------------------
# Nível N começa em (N - 1) * XP_PER_LEVEL de XP acumulado.
XP_PER_LEVEL = 100


def level_for_xp(xp_total: int) -> int:
    return xp_total // XP_PER_LEVEL + 1


def xp_progress(xp_total: int) -> tuple[int, int]:
    """(XP acumulado dentro do nível atual, XP que o nível atual exige)."""
    return xp_total % XP_PER_LEVEL, XP_PER_LEVEL


# --- Streak --------------------------------------------------------------------
# Eventos de `gamification_events.event_type` que contam como "atividade do
# dia" para o streak (dias consecutivos no fuso do usuário — ver
# `core.day_window`). `habit_logged` já entra na lista para quando o módulo
# de Hábitos existir.
STREAK_QUALIFYING_EVENTS = ("task_completed", "pomodoro_completed", "habit_logged")

# --- Conquistas -------------------------------------------------------------
@dataclass(frozen=True)
class AchievementSpec:
    code: str
    title: str
    description: str
    # "streak" | "event_total" | "focus_day" | "weekly_pomodoro_hours"
    metric: str
    threshold: int
    event_type: Optional[str] = None  # usado quando metric == "event_total"


ACHIEVEMENTS: tuple[AchievementSpec, ...] = (
    AchievementSpec(
        "streak_3", "Três dias seguidos", "Manteve a rotina por 3 dias seguidos.", "streak", 3
    ),
    AchievementSpec(
        "streak_7", "Uma semana firme", "Manteve a rotina por 7 dias seguidos.", "streak", 7
    ),
    AchievementSpec(
        "streak_30", "Um mês inteiro", "Manteve a rotina por 30 dias seguidos.", "streak", 30
    ),
    AchievementSpec(
        "tasks_25", "25 tarefas", "Concluiu 25 tarefas.", "event_total", 25, "task_completed"
    ),
    AchievementSpec(
        "tasks_100", "100 tarefas", "Concluiu 100 tarefas.", "event_total", 100, "task_completed"
    ),
    AchievementSpec(
        "pomodoro_1",
        "Primeiro foco",
        "Concluiu a primeira sessão de Pomodoro.",
        "event_total",
        1,
        "pomodoro_completed",
    ),
    AchievementSpec(
        "pomodoro_10",
        "Foco constante",
        "Concluiu 10 sessões de Pomodoro.",
        "event_total",
        10,
        "pomodoro_completed",
    ),
    AchievementSpec(
        "pomodoro_50",
        "Mestre do foco",
        "Concluiu 50 sessões de Pomodoro.",
        "event_total",
        50,
        "pomodoro_completed",
    ),
    AchievementSpec(
        "focus_day",
        "Dia de foco total",
        "Concluiu 3 tarefas de maior esforço num único dia.",
        "focus_day",
        3,
    ),
    AchievementSpec(
        "weekly_hours_5",
        "Semana produtiva",
        "Somou 5 horas de Pomodoro numa semana.",
        "weekly_pomodoro_hours",
        5,
    ),
)
