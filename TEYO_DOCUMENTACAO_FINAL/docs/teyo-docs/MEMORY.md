# MEMORY.md

DECIDIDO (doc. 3, item 15): a memória pertence ao sistema, não ao LLM.

## Camadas de memória (DECIDIDO)

1. **Contexto da conversa**: mensagens recentes da sessão atual. Vive em `conversations`/`messages`. Não é persistido como fato sobre o usuário.
2. **Memória temporária**: informação de curta duração, ligada ao momento (ex.: "hoje estou cansado"). NECESSÁRIO PARA IMPLEMENTAÇÃO: expira automaticamente (janela A DEFINIR, ex.: fim do dia).
3. **Memória permanente / preferências**: fatos estáveis declarados pelo usuário (ex.: "eu prefiro estudar à noite"). Persistida em `memory_entries` com `category = preference` ou `fact`.
4. **Histórico**: dados brutos de cada módulo (tarefas concluídas, logs de hábito, etc.), usados como evidência pelo Motor de Padrões, não são "memória" no sentido de fato declarado.
5. **Padrões / rotinas aprendidas**: não são memória declarada, são inferência do sistema com nível de confiança. Vivem em `routines`/`patterns`, não em `memory_entries` (ver `PATTERN_ENGINE.md`).

DECIDIDO (doc. 3, item 41) — distinção obrigatória:
- Memória: "o usuário gosta de X" (declarado).
- Padrão: "o usuário costuma fazer X às 19h" (inferido por frequência).
- Mudança: "nas últimas duas semanas o usuário começou a fazer X às 8h" (inferido por mudança de tendência).

## Quando algo é salvo (DECIDIDO)

- O usuário declara uma preferência ou fato estável → vira `memory_entries` (`source = user_stated`).
- Uma informação momentânea ("hoje estou cansado") → memória temporária, não vira `memory_entries` permanente.

## Quando algo NÃO deve ser salvo

- Estado emocional pontual não deve virar preferência permanente.
- Um padrão observado pelo Motor de Padrões não deve ser reescrito como se fosse uma preferência declarada pelo usuário — eles ficam em tabelas e categorias diferentes, mesmo quando o TEYO os menciona juntos na conversa.

## Como é recuperado (NECESSÁRIO PARA IMPLEMENTAÇÃO)

O Orquestrador seleciona memória relevante ao turno atual (não a memória inteira do usuário) antes de montar o prompt para o LLM. Critério exato de relevância (busca por palavra-chave, por módulo em foco, etc.) é A DEFINIR tecnicamente.

## Como é atualizada / removida

- Atualização: quando o usuário declara algo que contradiz uma entrada existente (ex.: "na verdade agora prefiro de manhã"), o sistema atualiza o registro, mantendo histórico de que houve mudança (NECESSÁRIO PARA IMPLEMENTAÇÃO: decidir se versiona ou sobrescreve — A DEFINIR).
- Remoção: DECIDIDO (doc. 3, item 42) — o usuário deve poder controlar/alterar/remover suas informações.

## Privacidade (DECIDIDO, doc. 3, item 42)

- Dados pertencem ao usuário.
- Memória deve ser controlável pelo usuário.
- Dados não devem ser inventados pelo sistema ou pelo LLM.
- Quando o multiusuário existir, informações de um usuário não podem vazar para outro.
- A DEFINIR: tratamento formal de LGPD antes de qualquer publicação pública do produto (FORA DO V1 em termos de compliance formal, mas a separação por `user_id` já é DECIDIDA desde o V1).
