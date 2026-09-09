# GAMIFICATION.md

## Decidido

- TEYO terá gamificação (XP, níveis, evolução, progresso, recompensas), relacionada às atividades do usuário nos módulos.
- Elementos de conquista considerados no histórico: sequência (streak), Pomodoro, foco total, produtividade, horas na semana.
- A evolução do mascote está ligada ao progresso de gamificação (ver `MASCOT.md`).
- Cálculo de XP e nível pertence ao sistema, nunca ao LLM (ver `ARCHITECTURE.md`).

## Valores V1 (DEFINIDO na FASE 9 — Jams; adotados da OPÇÃO RECOMENDADA, mantidos configuráveis)

Todos os números vivem em `backend/gamification/config.py` (e limiares de mascote em `backend/mascot/catalog.py`); ajustar não exige mudar lógica. Ver `DOCUMENTATION_AUDIT.md` (FASE 9).

**Eventos de XP** (via os hooks de domínio da FASE 8 — `on_task_completed`, `on_pomodoro_completed`; nenhuma regra de XP espalhada em tools/routers):

| Evento | XP |
|---|---|
| Tarefa concluída (`task_completed`) | +10 |
| Bônus por tarefa de maior esforço (`core.effort.is_high_effort_task` — `priority = high` e/ou `pomodoro_enabled`) | +5 |
| Sessão de Pomodoro concluída (`pomodoro_completed`) | +20 |
| Conquista desbloqueada (`achievement_unlocked`) | +25 |
| Hábito do dia (`habit_logged`) | +15 — **pendente**: sem módulo de Hábitos nem hook produtor; valor pronto em `config.py`, não ligado |

**Progressão de nível**: linear. `XP_PER_LEVEL = 100`; nível N começa em `(N-1) × 100` de XP acumulado (`level = xp_total // 100 + 1`).

**Streak**: dias consecutivos, no fuso do usuário (via `core.day_window` — mesma definição do Planejador), com ≥ 1 evento qualificante (`task_completed`, `pomodoro_completed`, `habit_logged`). Um "hoje em aberto" não zera o streak.

**Conquistas V1** (catálogo em `config.py`, extensível):

| Código | Critério |
|---|---|
| `streak_3` / `streak_7` / `streak_30` | streak atinge 3 / 7 / 30 |
| `tasks_25` / `tasks_100` | total de `task_completed` |
| `pomodoro_1` / `pomodoro_10` / `pomodoro_50` | total de `pomodoro_completed` |
| `focus_day` | 3 tarefas de maior esforço concluídas num mesmo dia |
| `weekly_hours_5` | 5 h somadas de Pomodoro numa semana-calendário |

**Relação nível ↔ estágio do mascote** (DECISÃO C — ver `MASCOT.md`): estágio 1 = nível 1–2; 2 = 3–5; 3 = 6–9; 4 = 10–14; 5 = 15+. Conquistas não mudam o estágio; desbloqueiam elementos complementares.

> Pendências registradas: `habit_logged` (sem produtor), e os valores acima são a proposta adotada — Jams pode ajustar qualquer número em `config.py`/`catalog.py` sem retrabalho estrutural.

## Persistência

Ver `gamification_state`, `gamification_events` e `achievements` (acrescentada na FASE 9) em `DATABASE.md`.

## Arquitetura (FASE 9)

`backend/gamification/` (domínio próprio, separado do mascote e do planner): `config.py` (números de produto), `engine.py` (aplica XP, recomputa nível, avalia conquistas), `streak.py`, `subscribers.py` (liga aos hooks da FASE 8), `service.py` (leitura para API/tool), `tools.py` (`get_gamification_state`, só leitura). Nenhuma função concede XP fora do `engine`; o LLM nunca calcula (`ARCHITECTURE.md`). Um subscriber que falha loga e não quebra a ação de origem (ex.: concluir tarefa funciona mesmo se o XP falhar).

## Interação com TEYO

O TEYO pode comentar eventos de gamificação na conversa (ex.: "Você concluiu 3 tarefas importantes hoje. Orgulho define!"), mas o número/XP em si vem do sistema via tool, nunca é estimado pelo LLM.
