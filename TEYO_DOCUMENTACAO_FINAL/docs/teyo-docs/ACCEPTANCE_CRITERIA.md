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
- Um único evento fora do padrão não altera `routines.status` de `active` para `deprecated`.
- Uma sequência sustentada de eventos divergentes (conforme limiar A DEFINIR) resulta em novo `candidate` sendo observado.

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
