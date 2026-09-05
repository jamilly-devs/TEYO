# DEFINITION_OF_DONE.md

"TEYO V1 está pronto" quando todos os itens abaixo forem verdadeiros e verificáveis:

1. Todas as funcionalidades explicitamente incluídas na V1 atendem aos critérios de `ACCEPTANCE_CRITERIA.md`.
2. Nenhuma funcionalidade listada como `FORA DO V1` está presente na build entregue como V1.
3. O LLM roda localmente com Qwen3.5-4B através do LLM Adapter, sem dependência de API paga de LLM em produção.
4. Toda ação de escrita realizada pela conversa passa por uma tool com validação de parâmetros.
5. As regras aplicáveis de `BUSINESS_RULES.md` têm testes automatizados e passam.
6. O Motor de Padrões não promove mudança a partir de um único evento.
7. Toda ação destrutiva exige confirmação explícita antes da execução.
8. Os critérios de `ACCEPTANCE_CRITERIA.md` passam integralmente.
9. Os fluxos V1 de `FLOWS.md` foram exercitados manualmente ou por testes E2E, incluindo caminhos de erro/ambiguidade quando aplicáveis.
10. `DOCUMENTATION_AUDIT.md` não contém contradição bloqueante não resolvida.
11. Toda pendência que permanecer `A DEFINIR` ao final da implementação está explicitamente registrada; nenhuma pendência foi resolvida arbitrariamente pelo Claude Code.
12. O isolamento por `user_id` está presente desde a V1, mesmo com um único usuário ativo, sem exigir a implementação da experiência completa de multiusuário.
