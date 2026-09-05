# TEYO V1 — Documentação Fonte da Verdade

Este pacote de documentos é a especificação oficial do TEYO V1. Ele foi escrito para ser lido e seguido pelo Claude Code durante a implementação, sem necessidade de reinterpretar conversas antigas do produto.

## Ordem de leitura recomendada

1. `CLAUDE_CODE_CONTEXT.md` — resumo compacto para carregar como contexto inicial.
2. `CLAUDE_CODE_INSTRUCTIONS.md` — regras de como usar esta documentação.
3. `PRODUCT.md` — o que é o TEYO.
4. `V1_SCOPE.md` — o que entra e o que não entra no V1.
5. `ARCHITECTURE.md` — arquitetura geral.
6. `DATABASE.md`, `API.md`, `LLM.md`, `TOOLS.md`, `MEMORY.md`, `PATTERN_ENGINE.md`, `PLANNER.md`.
7. `BUSINESS_RULES.md`.
8. `UX.md`, `NAVIGATION.md`, `MASCOT.md`, `GAMIFICATION.md`.
9. `MODULES/*.md` (um por módulo).
10. `FLOWS.md`, `ERROR_HANDLING.md`.
11. `TESTING.md`, `ACCEPTANCE_CRITERIA.md`.
12. `ROADMAP.md`, `DEFINITION_OF_DONE.md`.
13. `DOCUMENTATION_AUDIT.md` — pendências e inconsistências conhecidas.

## Convenções usadas em todos os documentos

- **DECIDIDO**: já foi definido explicitamente pelo dono do produto (Jams). Não pode ser alterado sem uma decisão nova registrada.
- **NECESSÁRIO PARA IMPLEMENTAÇÃO**: detalhe técnico que precisa existir para a funcionalidade decidida funcionar, mas que não é uma escolha de produto.
- **A DEFINIR**: ainda não foi decidido. Não deve ser implementado como definitivo. Quando bloqueia uma tarefa, é registrado com uma **OPÇÃO RECOMENDADA**.
- **FORA DO V1**: decisão de produto já tomada, mas adiada para uma versão futura.

## Regra geral para o Claude Code

Nunca transformar um item **A DEFINIR** em decisão definitiva por conta própria. Nunca implementar um item **FORA DO V1**. Ver `CLAUDE_CODE_INSTRUCTIONS.md`.
