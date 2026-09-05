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
- Efeito colateral: dispara evento de gamificação (`gamification_events`) e possível atualização de `mascot_state`.

## create_event / update_event / delete_event
- Mesma estrutura de `tasks`, aplicada a `events`. `delete_event` exige confirmação.
- `create_event` deve resolver linguagem natural de data/hora (ex.: "amanhã às duas") no Orquestrador antes de chamar a tool com `start_at`/`end_at` já normalizados — a tool em si recebe apenas valores estruturados, não texto livre.

## create_goal / update_goal
- Parâmetros obrigatórios (create): `title`. Opcionais: `description`, `target_date`.

## add_market_item
- Parâmetros obrigatórios: `name`. Opcionais: `category`.

## remove_market_item
- Parâmetros obrigatórios: `item_id`.
- A DEFINIR: se "remover" significa excluir o item da lista ou marcar como comprado/consumido (ver `MODULES/MARKET.md`). Até a decisão, a tool existe com este nome mas seu efeito exato fica documentado como A DEFINIR.

## get_daily_plan
- Sem parâmetros obrigatórios (usa `user_id` da sessão).
- Retorno: lista ordenada de tarefas/compromissos do dia, montada pelo Planejador (ver `PLANNER.md`), não pelo LLM.

## reorganize_day
- Parâmetros opcionais: `constraint` (texto livre transformado pelo Orquestrador em parâmetros estruturados, ex.: `energy_level: low`).
- Retorno: novo plano proposto. DECIDIDO: o TEYO sugere, o usuário aceita ou recusa — a tool não aplica a reorganização definitivamente sem uma confirmação (ver `BUSINESS_RULES.md`).


## get_user_preferences
- Retorno: preferências armazenadas em `memory_entries` (categoria `preference`).

## get_memory
- Parâmetros opcionais: `query`/`category` para filtrar.
- Retorno: apenas memória relevante ao contexto atual, não o dump completo (ver `MEMORY.md`).

## get_patterns
- Parâmetros opcionais: `pattern_type`.
- Retorno: padrões com `status = active` (e `candidate` apenas quando explicitamente solicitado), no formato estruturado definido em `PATTERN_ENGINE.md` (ex.: padrão, período predominante, frequência, status, mudança recente, confiança).

## get_routine_changes
- Retorno: mudanças de rotina detectadas com confiança acima do limiar (A DEFINIR o valor exato — ver `PATTERN_ENGINE.md`), para o TEYO poder comentar proativamente ("Percebi que ultimamente...").

## Regras gerais de todas as tools (DECIDIDO)

- Toda tool valida os parâmetros recebidos antes de executar; parâmetro obrigatório ausente é erro (ver `ERROR_HANDLING.md`), nunca é inferido pelo LLM sem confirmação do usuário.
- Toda tool retorna sucesso/erro de forma explícita; o LLM só pode informar ao usuário que uma ação foi concluída após receber confirmação de sucesso da tool.
- Tools de leitura (`get_*`) não alteram dados e podem ser chamadas livremente pelo contexto da conversa.
- Tools de escrita que sejam destrutivas ou ambíguas exigem confirmação prévia do usuário antes da chamada.

## Fora do V1

Não criar tools de Notícias ou Relatórios na V1.
