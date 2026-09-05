# MASCOT.md

## Identidade (DECIDIDO)

O mascote se chama TEYO — mesma identidade textual/conversacional do assistente. A grafia oficial é sempre "TEYO" (não usar "Teyo", "TEO", "Teo").

## Comportamento (DECIDIDO)

- Reage a acontecimentos do usuário (ex.: conclui muitas tarefas → expressão feliz/orgulhosa; usuário cansado → expressão acolhedora; conquista alcançada → comemoração).
- Possui expressões diferentes, controladas pelo sistema, não pelo usuário.
- Evolui visualmente conforme progresso do usuário (níveis/gamificação).

## Personalização (DECIDIDO)

Permitido: alterar a cor do TEYO.

Não permitido: escolher/personalizar expressões, adicionar acessórios livremente (fones, bonés, óculos), criar combinações, criar tipos diferentes de TEYO.

## Evolução (DECIDIDO — conceito; A DEFINIR os estágios exatos)

Evolução pré-definida pelo sistema, não escolhida pelo usuário. Exemplo conceitual dado no histórico:

```
nível inicial → cresce um pouco → roupa nova → evolui → coroa → ...
```

A DEFINIR: número exato de estágios de evolução e o critério de XP/nível que dispara cada estágio (depende de `GAMIFICATION.md`, também A DEFINIR nos valores).

## Expressões

Determinadas pelo sistema com base em eventos (conclusão de tarefas, conquistas, sinais de cansaço relatados pelo usuário). A lista completa e exaustiva de expressões e seus gatilhos é NECESSÁRIO PARA IMPLEMENTAÇÃO / A DEFINIR — este documento estabelece o princípio (reativo, controlado pelo sistema), não o catálogo final de estados.

## Relação com a personalidade textual (DECIDIDO)

O mascote deve parecer parte do TEYO, não um elemento visual separado — a expressão visual e o tom da mensagem de texto devem combinar (ex.: mascote com expressão de orgulho junto de uma mensagem como "Você mandou bem hoje.").

## Animações — risco técnico (DECIDIDO como requisito + regra de tratamento de risco)

As animações do mascote devem ser implementadas pelo Claude Code; o dono do produto não sabe criar animações manualmente. Se uma animação específica não for tecnicamente viável na stack escolhida, o Claude Code deve:
1. Identificar e registrar o problema explicitamente (não simplificar o mascote silenciosamente).
2. Propor uma alternativa técnica viável.

RISCO TÉCNICO IDENTIFICADO: a viabilidade de animações ricas (transições suaves entre expressões, evolução animada) depende da stack de frontend ainda A DEFINIR (`ARCHITECTURE.md`). Este é um risco a ser resolvido na FASE 3/FASE 8 do roadmap, não antes.
