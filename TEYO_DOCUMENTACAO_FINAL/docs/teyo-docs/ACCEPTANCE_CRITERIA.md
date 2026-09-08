# ACCEPTANCE_CRITERIA.md

Critérios verificáveis por área — cada um deve ser demonstrável por um teste automatizado ou uma verificação manual objetiva, não por "parece funcionar".

## Tarefas
- Criar, editar, concluir e excluir uma tarefa pela conversa produz o mesmo resultado no banco que fazer pela tela.
- Excluir uma tarefa sem confirmação prévia não remove o registro do banco.
- Uma tarefa criada sem `is_recurring` explícito nunca é marcada como recorrente automaticamente.

## Agenda
- Criar um compromisso por linguagem natural ("amanhã às duas") resulta em `events.start_at` correto para o dia seguinte às 14:00 no fuso do usuário.
- Compromisso sobreposto a outro existente gera sinalização ao usuário antes da confirmação (quando a decisão de `PLANNER.md` for confirmada).

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
