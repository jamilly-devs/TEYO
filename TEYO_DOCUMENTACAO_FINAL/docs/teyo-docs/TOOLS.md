# TOOLS.md

DECIDIDO: o LLM nunca executa lógica de negócio diretamente. Toda ação passa por uma tool com contrato fixo. A lista abaixo é a lista base (DECIDIDO em doc. 3, item 36, "não é necessariamente definitiva — deve ser refinada durante a arquitetura técnica" → portanto os nomes são DECIDIDOS como conjunto inicial, mas a lista pode crescer, NECESSÁRIO PARA IMPLEMENTAÇÃO).

Formato de especificação por tool: nome, finalidade, parâmetros obrigatórios/opcionais, retorno, quando pode ser chamada, quando não deve ser chamada.

## create_task
- Finalidade: criar uma tarefa.
- Parâmetros obrigatórios: `title`. Opcionais: `description`, `due_date`, `priority`, `goal_id`, `pomodoro_enabled`.
- Retorno: task criada com `id`.
- Não deve ser chamada: se o usuário estiver apenas conversando sobre uma possibilidade ("eu deveria estudar amanhã?") sem confirmar a criação.

## update_task
- Parâmetros obrigatórios: `task_id`. Opcionais: qualquer campo de `tasks`.
- Não deve ser chamada sem `task_id` resolvido de forma não ambígua (ver `BUSINESS_RULES.md` sobre desambiguação).

## delete_task
- Parâmetros obrigatórios: `task_id`.
- DECIDIDO (regra de segurança): ação destrutiva — exige confirmação explícita do usuário antes da chamada (ver `BUSINESS_RULES.md`).

## complete_task
- Parâmetros obrigatórios: `task_id`.
- Efeito colateral: dispara evento de gamificação (`gamification_events`) e possível atualização de `mascot_state`. NECESSÁRIO PARA IMPLEMENTAÇÃO: esse efeito colateral é FASE 9 (`GAMIFICATION.md`, `MASCOT.md`); na FASE 5, `complete_task` apenas marca a tarefa como concluída, sem nenhum efeito de XP/mascote.

## create_event / update_event / delete_event
- Mesma estrutura de `tasks`, aplicada a `events`. `delete_event` exige confirmação.
- `create_event` deve resolver linguagem natural de data/hora (ex.: "amanhã às duas") no Orquestrador antes de chamar a tool com `start_at`/`end_at` já normalizados — a tool em si recebe apenas valores estruturados, não texto livre.

## create_goal / update_goal
- Parâmetros obrigatórios (create): `title`. Opcionais: `description`, `target_date`.

## add_market_item
- Parâmetros obrigatórios: `name`. Opcionais: `category`.

## remove_market_item
- Parâmetros obrigatórios: `item_id`.
- DECIDIDO (registrado em `DOCUMENTATION_AUDIT.md`, sincronizado na FASE 5): exclusão definitiva do item (hard delete), distinta de marcar como comprado (`status = purchased`, feito pela tela via `PATCH /market/items/{id}`). Ação destrutiva — exige confirmação explícita do usuário antes da chamada, como qualquer outra exclusão.

## list_tasks / list_events / list_goals / list_market_items / list_financial_records
- Adicionadas na FASE 5 (decisão tomada com Jams em 2026-09-06, registrada em `DOCUMENTATION_AUDIT.md`): a lista-base original não tinha nenhuma tool de leitura para Tarefas/Agenda/Objetivos/Mercado/Finanças além de `get_daily_plan` (que só cobre o dia atual e só existe a partir da FASE 8). Sem uma tool de listagem, o LLM não teria como resolver referências ambíguas a itens existentes fora do que já foi dito na própria conversa.
- Sem parâmetros obrigatórios; retornam todos os itens do módulo pertencentes ao usuário (mesmo dado que as telas correspondentes usam via `GET` de `API.md`).
- Tools de leitura: não alteram dados, podem ser chamadas livremente pelo contexto da conversa (regra geral abaixo).
- Uso típico: antes de `update_task`/`delete_task`/`complete_task`, `update_event`/`delete_event`, `update_goal` ou `remove_market_item`, quando o item mencionado pelo usuário não está claro a partir do histórico recente da conversa.

## get_daily_plan
- Sem parâmetros obrigatórios (usa `user_id` da sessão).
- Retorno: lista ordenada de tarefas/compromissos do dia, montada pelo Planejador (ver `PLANNER.md`), não pelo LLM.

## reorganize_day
- Parâmetros opcionais: `constraint` (texto livre transformado pelo Orquestrador em parâmetros estruturados, ex.: `energy_level: low`).
- Retorno: novo plano proposto. DECIDIDO: o TEYO sugere, o usuário aceita ou recusa — a tool não aplica a reorganização definitivamente sem uma confirmação (ver `BUSINESS_RULES.md`).


## remember_preference / remember_fact
- Adicionadas na FASE 6 (decisão tomada com Jams em 2026-09-06, registrada em `DOCUMENTATION_AUDIT.md`): a lista-base original não tinha nenhuma tool de escrita para `memory_entries` — sem elas a conversa nunca criaria memória, o que contradiz `MEMORY.md` ("quando algo é salvo").
- Parâmetros obrigatórios: `key`, `value`. `remember_preference` grava com `category = preference`; `remember_fact` com `category = fact`. Ambas gravam com `source = user_stated`.
- Se já existir uma entrada com a mesma `key` (e mesma categoria) do mesmo usuário, o valor é atualizado (sobrescreve — ver `MEMORY.md`, "versiona ou sobrescreve" resolvido nesta fase).
- Não deve ser chamada para estado emocional ou situacional pontual (ex.: "hoje estou cansado") — ver `MEMORY.md`, "quando algo NÃO deve ser salvo".

## forget_memory
- Adicionada na FASE 6 (mesma decisão acima). Parâmetro obrigatório: `memory_id`.
- DECIDIDO (regra de segurança, igual às outras exclusões): ação destrutiva — exige confirmação explícita do usuário antes da chamada (ver `BUSINESS_RULES.md`).
- Resolve `ACCEPTANCE_CRITERIA.md` ("remover uma entrada de memória a pedido do usuário efetivamente a exclui").

## get_user_preferences
- Retorno: preferências armazenadas em `memory_entries` (categoria `preference`).

## get_memory
- Parâmetros opcionais: `query`/`category` para filtrar.
- Retorno: apenas memória relevante ao contexto atual, não o dump completo (ver `MEMORY.md`).

## get_patterns
- Parâmetros opcionais: `pattern_type`.
- Retorno: `items` com os padrões `status = active` (e `candidate` apenas quando explicitamente solicitado, isto é, quando `pattern_type` é informado), no formato estruturado definido em `PATTERN_ENGINE.md` (ex.: padrão, período predominante, frequência, status, mudança recente, confiança); `deprecated` nunca aparece em `items`. Além de `items`, o retorno inclui `routine_changes_detected` (bool): `true` quando existe alguma categoria (dentro do filtro de `pattern_type`, se informado) com uma mudança recente sustentada detectada pelo Motor — inclusive quando essa categoria não aparece em `items` porque acabou de ser despromovida para `deprecated` na mesma computação (ver `PATTERN_ENGINE.md`, rebaixamento `active`→`deprecated`). Existe para que `items` vazio nunca seja lido como "não há padrão nem mudança": quando `routine_changes_detected` vier `true`, ou a pergunta do usuário for sobre mudança de rotina, a tool a usar para o detalhe é `get_routine_changes`, não esta.
- Implementado na FASE 7 só para `pattern_type = "task_time_of_day:<categoria>"` (ex.: `task_time_of_day:studies`) — único dado real disponível das FASES 2-6 (ver `PATTERN_ENGINE.md`). Passar só `"task_time_of_day"` retorna todas as categorias (prefixo).

## get_routine_changes
- Retorno: mudanças de rotina detectadas com confiança acima do limiar (70%, confirmado com Jams na FASE 7 — ver `PATTERN_ENGINE.md`), para o TEYO poder comentar proativamente ("Percebi que ultimamente...").

## Regras gerais de todas as tools (DECIDIDO)

- Toda tool valida os parâmetros recebidos antes de executar; parâmetro obrigatório ausente é erro (ver `ERROR_HANDLING.md`), nunca é inferido pelo LLM sem confirmação do usuário.
- Toda tool retorna sucesso/erro de forma explícita; o LLM só pode informar ao usuário que uma ação foi concluída após receber confirmação de sucesso da tool.
- Tools de leitura (`get_*`) não alteram dados e podem ser chamadas livremente pelo contexto da conversa.
- Tools de escrita que sejam destrutivas ou ambíguas exigem confirmação prévia do usuário antes da chamada.

## Fora do V1

Não criar tools de Notícias ou Relatórios na V1.
