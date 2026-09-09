# MODULES/HABITS.md — Hábitos

1. **Objetivo**: acompanhar hábitos recorrentes do usuário.
2. **Funcionalidades**: criar hábito, registrar ocorrência (log), acompanhar sequência (streak).
3. **Telas**: lista de hábitos com indicação de progresso/sequência.
4. **Componentes**: item de hábito, indicador de streak.
5. **Dados**: `habits`, `habit_logs` (ver `DATABASE.md`) — reutilizados sem alteração de schema. `frequency_target` = **dias por semana, 1 a 7** (DECIDIDO na FASE 10; já era o range do `CheckConstraint` da FASE 1). `habit_logs.context` passa a ser gravado como `{"hour": h, "weekday": w}` (uso futuro do Motor de Padrões — que **não** é tocado nesta fase).
6. **Ações** (DECIDIDO na FASE 10): tools próprias `create_habit`, `list_habits`, `update_habit`, `log_habit` (sem `delete_habit`, como Objetivos); endpoints `GET/POST /habits`, `PATCH /habits/{id}`, `POST /habits/{id}/log`.
7. **Regras de negócio** (FASE 10):
   - Um log isolado fora do padrão **não quebra** o hábito.
   - **`log_habit` é idempotente por dia** (fuso do usuário, via `core.day_window`): a 2ª chamada no mesmo dia devolve o log existente, sem novo registro, sem novo XP.
   - **Streak individual do hábito** = semanas-calendário consecutivas (segunda–domingo) em que o hábito teve **≥ `frequency_target`** logs. A semana corrente conta como "em andamento" — não soma enquanto não bate o alvo, mas também não zera. É **distinto** do streak global da gamificação (esse não é alterado na FASE 10).
8. **Interação com TEYO**: usuário pode registrar cumprimento de hábito conversando.
9. **Interação com outros módulos**: gamificação — `log_habit` dispara `core.domain_events.on_habit_logged`; o subscriber de gamificação credita `XP_HABIT_LOGGED` (regra e `event_type` `habit_logged` já existentes desde a FASE 9) e o mascote fica `happy`. `"habit_logged"` já era evento qualificante do streak global desde a FASE 9. O Motor de Padrões (`habit_frequency`) **não** é implementado na FASE 10 (escopo da FASE 7).
10. **V1**: criação e registro de log, visualização de streak.
11. **Depois**: lembretes automáticos programados, hábitos compartilhados entre usuários — não mencionados no histórico, FORA DO V1.
