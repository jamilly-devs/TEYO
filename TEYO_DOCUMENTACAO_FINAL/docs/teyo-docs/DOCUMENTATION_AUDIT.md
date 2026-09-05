# DOCUMENTATION_AUDIT.md

## Auditoria de correção — entrega para Claude Code

Esta versão foi revisada para eliminar contradições de escopo e status de decisão encontradas na versão anterior.

### Correções obrigatórias realizadas

1. **V1/V2 corrigido**: Notícias e Relatórios foram removidos do escopo V1 e marcados como V2+.
2. **Home corrigida**: a hierarquia confirmada permanece conversa → progresso → tarefas/plano do dia → agenda e demais blocos gerais. Referências históricas a Notícias não liberam sua implementação na V1.
3. **Multiusuário corrigido**: V1 começa com um usuário ativo, mas isolamento por `user_id` e preparação estrutural para múltiplos usuários já são requisitos V1. Experiência completa de multiusuário fica fora do V1.
4. **Qwen corrigido**: Qwen3.5-4B local é decisão fechada da V1; runtime/infraestrutura exatos continuam pendentes.
5. **Definition of Done corrigido**: deixou de exigir CRUD para todo módulo indiscriminadamente e passou a exigir critérios verificáveis das funcionalidades V1.
6. **API/Navegação corrigidas**: endpoints, rotas e telas de Notícias/Relatórios não fazem parte da V1.
7. **Schema corrigido**: `news_preferences` foi retirado do schema funcional V1.
8. **Documentos futuros preservados**: `MODULES/NEWS.md` e `MODULES/REPORTS.md` continuam como especificações futuras, claramente marcadas V2+.

### Pendências legítimas

- Stack de frontend/backend/banco.
- Runtime exato de produção do Qwen3.5-4B.
- Valores do Motor de Padrões.
- Regras exatas de gamificação.
- Estágios exatos do mascote.
- Mecanismo concreto de busca de vagas.
- Algoritmo de priorização do Planejador.
- Segurança/privacidade e schemas que ainda não estejam suficientemente especificados.
- Semântica final de operações de Mercado ainda marcada como pendente nos documentos correspondentes.

### Critério de entrega

A documentação só deve ser considerada fonte segura quando o Claude Code conseguir identificar, sem inferência, o que é V1, o que é V2+, o que é decisão fechada e o que ainda está pendente.
