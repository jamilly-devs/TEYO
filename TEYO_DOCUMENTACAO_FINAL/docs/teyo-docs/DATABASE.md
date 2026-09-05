# DATABASE.md

Todas as tabelas abaixo incluem `user_id` (FK para `users.id`) desde o V1, mesmo operando com um único usuário ativo, com isolamento por usuário desde a V1 e preparação para multiusuário (DECIDIDO em `ARCHITECTURE.md`).

## users
Justificativa: base de qualquer isolamento de dados.
- `id` (PK)
- `name`
- `email`
- `created_at`
- `preferences` (JSON — ver `MEMORY.md` para o que pode ir aqui)

## tasks
Justificativa: módulo Tarefas.
- `id` (PK)
- `user_id` (FK users)
- `title`
- `description` (nullable)
- `status` (enum: pending, in_progress, done, cancelled)
- `due_date` (nullable)
- `priority` (A DEFINIR — escala não decidida)
- `is_recurring` (boolean, default false) — DECIDIDO: tarefa única não vira recorrente automaticamente
- `pomodoro_enabled` (boolean, default false)
- `goal_id` (FK goals, nullable)
- `created_at`, `updated_at`
- Índices: `(user_id, status)`, `(user_id, due_date)`

## habits
Justificativa: módulo Hábitos.
- `id` (PK), `user_id` (FK)
- `title`, `frequency_target` (A DEFINIR formato exato)
- `created_at`

## habit_logs
Justificativa: histórico necessário para o Motor de Padrões.
- `id` (PK), `habit_id` (FK habits), `user_id` (FK)
- `completed_at`, `context` (JSON, ex.: horário, dia da semana)

## goals
Justificativa: módulo Objetivos, referenciado por tasks.
- `id` (PK), `user_id` (FK)
- `title`, `description`, `status`, `target_date` (nullable)
- `created_at`, `updated_at`

## events
Justificativa: módulo Agenda.
- `id` (PK), `user_id` (FK)
- `title`, `start_at`, `end_at`
- `source` (enum: manual, teyo_nlu) — de onde veio o compromisso
- `created_at`, `updated_at`
- Índice: `(user_id, start_at)`

## market_items
Justificativa: módulo Mercado.
- `id` (PK), `user_id` (FK) — DECIDIDO: pode ser compartilhado entre contas no futuro; V1 mantém `user_id` do criador
- `name`, `category` (enum/string: hortifruti, limpeza, etc.)
- `is_recurring_suggestion` (boolean) — DECIDIDO: itens recorrentes e sugestões por histórico são desejados
- `status` (enum: active, purchased)
- `created_at`

Nota: DECIDIDO que a funcionalidade de "remover da lista" como conceito principal foi reconsiderada; nesta conversa não há registro de decisão final sobre a mecânica exata de remoção/consumo. Ver A DEFINIR em `MODULES/MARKET.md`.

## financial_records
Justificativa: módulo Finanças.
- `id` (PK), `user_id` (FK)
- `type` (enum: income, expense — A DEFINIR se há mais tipos)
- `amount`, `category`, `date`, `description`
- `created_at`

## routines / patterns
Justificativa: Motor de Padrões precisa persistir padrões detectados, separado do histórico bruto.
- `id` (PK), `user_id` (FK)
- `pattern_type` (ex.: task_time_of_day, habit_frequency)
- `description` (texto gerado pelo sistema, não pelo LLM)
- `confidence` (float, 0–1)
- `status` (enum: candidate, active, deprecated)
- `window_start`, `window_end`
- `evidence_count`
- `created_at`, `updated_at`

## pattern_events
Justificativa: eventos brutos usados como evidência pelo Motor de Padrões (distinto dos logs de cada módulo, serve de índice unificado).
- `id` (PK), `user_id` (FK)
- `event_type`, `occurred_at`, `metadata` (JSON)

## memory_entries
Justificativa: memória permanente/estruturada do usuário (distinta do histórico de conversa). Ver `MEMORY.md`.
- `id` (PK), `user_id` (FK)
- `key`, `value`, `category` (enum: preference, fact, decision)
- `created_at`, `updated_at`, `source` (enum: user_stated, system_inferred)

## conversations
- `id` (PK), `user_id` (FK)
- `started_at`, `last_message_at`

## messages
- `id` (PK), `conversation_id` (FK conversations)
- `role` (enum: user, assistant, tool)
- `content`, `tool_calls` (JSON, nullable)
- `created_at`
- Índice: `(conversation_id, created_at)`

## productivity_logs
Justificativa: base para relatórios e para o planejador usar horários de maior produtividade.
- `id` (PK), `user_id` (FK)
- `task_id` (FK tasks, nullable), `started_at`, `ended_at`, `focus_score` (A DEFINIR se existe)

## gamification_state
Justificativa: XP/nível pertence ao sistema, não ao LLM.
- `user_id` (PK/FK)
- `xp_total`, `level`, `updated_at`

## gamification_events
- `id` (PK), `user_id` (FK)
- `event_type`, `xp_delta`, `related_entity_type`, `related_entity_id`, `created_at`

## mascot_state
Justificativa: evolução visual e cor pertencem ao sistema.
- `user_id` (PK/FK)
- `color` (customizável pelo usuário — DECIDIDO)
- `evolution_stage` (enum pré-definido pelo sistema — DECIDIDO, valores exatos A DEFINIR)
- `current_expression` (enum, calculado por eventos do sistema)
- `updated_at`

## Tabelas explicitamente NÃO criadas

- `pets` — DECIDIDO removido, não criar sob nenhuma justificativa.

## Estruturas fora do V1

`news_preferences` não faz parte do schema funcional da V1, pois Notícias é V2+. Sua necessidade deverá ser definida quando o módulo entrar no escopo.

Relatórios também não possui tabela/módulo próprio na V1; dados de atividade podem existir quando necessários a funcionalidades V1 (por exemplo, Planejador e Motor de Padrões), mas isso não constitui a implementação do módulo Relatórios.
