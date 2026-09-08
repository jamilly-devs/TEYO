# ACCEPTANCE_CRITERIA.md

Critérios verificáveis por área — cada um deve ser demonstrável por um teste automatizado ou uma verificação manual objetiva, não por "parece funcionar".

## Tarefas
- Criar, editar, concluir e excluir uma tarefa pela conversa produz o mesmo resultado no banco que fazer pela tela.
- Excluir uma tarefa sem confirmação prévia não remove o registro do banco.
- Uma tarefa criada sem `is_recurring` explícito nunca é marcada como recorrente automaticamente.

## Agenda
- Criar um compromisso por linguagem natural ("amanhã às duas") resulta em `events.start_at` correto para o dia seguinte às 14:00 no fuso do usuário.
- Compromisso sobreposto a outro existente gera sinalização ao usuário antes da confirmação: `create_event`/`update_event` não criam/alteram nada quando há sobreposição não confirmada (`conflict: true` na tool, HTTP 409 no endpoint REST), e só criam/alteram mesmo assim com `confirm_overlap: true` explícito, depois da confirmação do usuário. DECIDIDO com Jams na FASE 8 (ver `PLANNER.md`, `DOCUMENTATION_AUDIT.md`) — resolve o "A DEFINIR" anterior.

## Planejador
- `get_daily_plan` nunca reordena/move um `event` ou uma `task` com `due_date` hoje — eles são âncoras fixas do plano.
- Uma tarefa sem `due_date` some do plano ao ser concluída (`status = done`) ou cancelada; tarefas `done`/`cancelled` nunca aparecem em `get_daily_plan`.
- `reorganize_day` nunca altera `tasks`/`events` no banco por si só — a proposta só vira mudança real depois de uma chamada explícita a `update_task`/`update_event`, feita após confirmação do usuário na conversa.
- `reorganize_day` com `energy_level: "low"` nunca move um `event` ou uma tarefa com `due_date` hoje; só afeta tarefas sem horário fixo de maior esforço (`priority = high` e/ou `pomodoro_enabled = true`).
- O plano do dia calculado por `get_daily_plan` é isolado por `user_id` (`BUSINESS_RULES.md` #17).

## Motor de Padrões
- Um único evento fora do padrão não altera `patterns.status` de `active` para `deprecated`.
- Uma sequência sustentada de eventos divergentes na janela recente (limiar de 70% de confiança sobre um mínimo de 3 ocorrências, ver `PATTERN_ENGINE.md`) despromove a linha existente de `active` para `deprecated`. DECIDIDO na FASE 7 (ver `DOCUMENTATION_AUDIT.md`): isso não cria uma segunda linha `candidate` para o período emergente — mantém-se uma única linha por usuário/categoria, e a mudança emergente fica disponível via `recent_change`/`get_routine_changes`, sem promoção automática a `active` do novo período (a promoção definitiva continua exigindo a trilha normal: `candidate` → `active` a 80% de frequência na janela histórica de 21 dias).
- `get_patterns` (padrões atuais confirmados) pode retornar vazio para uma categoria no exato momento em que ela é despromovida por divergência — isso nunca deve ser interpretado como "não há padrão/mudança"; `get_routine_changes` (ou o bloco de padrões em `Context.patterns`) permanece com a informação da mudança detectada.

## Memória
- Uma preferência declarada pelo usuário aparece em `memory_entries` com `category = preference`.
- Remover uma entrada de memória a pedido do usuário efetivamente a exclui/torna inacessível ao LLM.

## LLM / Tools
- Nenhuma resposta do TEYO afirma sucesso de uma ação sem que a tool correspondente tenha retornado sucesso.
- Chamada de tool com parâmetro obrigatório ausente nunca executa a ação.

## Mascote
- Alterar a cor do mascote é a única personalização visual disponível ao usuário na interface.
- Evento de conclusão de tarefa relevante dispara mudança de `mascot_state.current_expression` visível na UI.

## Gamificação
- XP e nível exibidos ao usuário sempre correspondem ao valor persistido em `gamification_state`, nunca a uma estimativa do LLM.

## Escopo
- Nenhuma funcionalidade listada em "NÃO INCLUI NO V1" (`V1_SCOPE.md`) está presente na build entregue como V1.
