# MODULES/POMODORO.md — Pomodoro

Criado na FASE 10. Até então não havia documento próprio de Pomodoro — só
menções em `V1_SCOPE.md`, `NAVIGATION.md`, `FLOWS.md` #11 e
`BUSINESS_RULES.md` #9. Este documento fixa a especificação V1 mínima.

1. **Objetivo**: cronômetro de foco associado a uma tarefa, opcional.
2. **Funcionalidades V1**: iniciar sessão de foco, pausar, retomar, concluir. Só sessões de **foco** — pausas curtas/longas são conceito de UI, **não** persistidas (DT-7).
3. **Telas**: **não** é um módulo no menu. É um controle (`frontend/src/components/PomodoroTimer.tsx`) aberto sob demanda a partir de uma tarefa com `pomodoro_enabled = true`, na `TasksScreen`. Duração de foco padrão (25 min) é constante de UI — o backend não fixa duração.
4. **Componentes**: contagem regressiva (`role="timer"`) + botões Pausar/Retomar/Concluir/Fechar.
5. **Dados**: **exclusivamente** `pomodoro_sessions` (DT-8). **Não** usa `productivity_logs` (fica sem escritor no V1; Relatórios é V2+). Campos usados: `user_id`, `task_id` (nullable), `status` (`active`/`paused`/`completed`), `started_at`, `ended_at`.
6. **Ações / API** (FASE 10):
   - `POST /pomodoro/sessions` — inicia (opcional `task_id`). **409** se já houver sessão `active`/`paused` do usuário (DT-5); **404** se `task_id` não for do usuário.
   - `GET /pomodoro/sessions/active` — a sessão em andamento ou `null`.
   - `POST /pomodoro/sessions/{id}/pause` · `.../resume` — flip de estado; **409** em transição inválida.
   - `POST /pomodoro/sessions/{id}/complete` — conclui via o ponto único `core.pomodoro_completion.complete_session`.
   - **Sem tool de LLM** (DT-9): timer é experiência de UI/tempo real. Desvio registrado da regra 1:1 de `API.md`.
7. **Regras de negócio**:
   - Estado controlado pelo sistema (`FLOWS.md` #11).
   - **Sessão válida** (DT-4): estava `active`/`paused`, concluída pela 1ª vez, e `ended_at - started_at ≥ 1 min` (`core.pomodoro_completion.MIN_VALID_MINUTES`, ajustável). Só sessão válida dispara `core.domain_events.on_pomodoro_completed`. Sessão curta demais vira `completed` mas **não** concede XP (anti-farm).
   - Pausa **não** é descontada do tempo decorrido (DT-6): "tempo" = `ended_at - started_at`. Imperfeição aceita no V1; é a mesma conta de `gamification/streak.weekly_pomodoro_hours`.
   - Uma sessão em andamento por usuário (DT-5).
8. **Interação com TEYO**: nenhuma (sem tool). O TEYO pode **comentar** um Pomodoro concluído porque a gamificação registrou o evento, mas não inicia/controla o timer.
9. **Interação com outros módulos**: gamificação — `on_pomodoro_completed` (ligado desde a FASE 9) credita `XP_POMODORO_COMPLETED` e avalia conquistas `pomodoro_*` / `weekly_hours_5`. **Sem** lógica de XP no módulo de Pomodoro.
10. **V1**: iniciar/pausar/retomar/concluir sessão de foco associada a uma tarefa, persistida em `pomodoro_sessions`, disparando o evento de gamificação na conclusão válida.
11. **Depois** (FORA DO V1): ciclos automáticos foco/pausa, pausas longas, som/notificações, estatísticas próprias, tool conversacional (`start_pomodoro`), `focus_score`.
