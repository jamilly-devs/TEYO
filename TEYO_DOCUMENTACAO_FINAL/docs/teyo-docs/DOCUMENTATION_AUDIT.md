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

### Critério de entrega

A documentação só deve ser considerada fonte segura quando o Claude Code conseguir identificar, sem inferência, o que é V1, o que é V2+, o que é decisão fechada e o que ainda está pendente.

## Decisões registradas durante a implementação

### 2026-09-06 — FASE 5 (Tools)

1. **`remove_market_item` = exclusão definitiva (hard delete).** Resolve a pendência "Semântica final de operações de Mercado" (antes listada em "Pendências legítimas" acima). A decisão já existia implicitamente no código da FASE 2 (`api/routers/market.py`, endpoint `DELETE /market/items/{id}`, comentado como "per Jams's decision" desde aquela fase) — nesta entrada ela é formalizada e sincronizada em `TOOLS.md`, `MODULES/MARKET.md` e `API.md`. Distinta de marcar como comprado (`PATCH .../items/{id}`, `status=purchased`, não remove a linha).
2. **Tools de listagem adicionadas: `list_tasks`, `list_events`, `list_goals`, `list_market_items`, `list_financial_records`.** A lista-base de `TOOLS.md` não tinha nenhuma tool de leitura para esses módulos além de `get_daily_plan` (que só cobre o dia atual e só chega na FASE 8) — sem elas o LLM não teria como resolver referências ambíguas a itens existentes fora da conversa atual. Decisão tomada com Jams em 2026-09-06 (opção "adicionar list_* para todos os módulos"), documentada em `TOOLS.md`.
3. **`complete_task` na FASE 5 não implementa o efeito colateral de gamificação/mascote descrito em `TOOLS.md`.** Esse efeito é FASE 9 (`GAMIFICATION.md`, `MASCOT.md`, ainda vazios em `backend/gamification` e `backend/mascot`); a tool desta fase só marca a tarefa como concluída. Não é uma mudança de escopo — é a mesma sequência de fases já definida em `ROADMAP.md`.
4. **Escopo de tools da FASE 5 limitado aos endpoints da FASE 2** (Tarefas, Agenda, Objetivos, Mercado, Finanças), conforme o próprio texto do `ROADMAP.md` ("conectando Orquestrador aos endpoints da FASE 2"). `get_daily_plan`, `reorganize_day`, `get_user_preferences`, `get_memory`, `get_patterns` e `get_routine_changes` continuam definidas em `TOOLS.md` mas ficam para as FASES 6–8, quando os sistemas de que dependem (Memória, Motor de Padrões, Planejador) existirem.

### 2026-09-07 — FASE 6 (Memória)

1. **Tools de escrita de memória adicionadas: `remember_preference`, `remember_fact`, `forget_memory`.** A lista-base de `TOOLS.md` só tinha `get_user_preferences`/`get_memory` (leitura) — sem uma tool de escrita, `memory_entries` nunca seria criada a partir da conversa, contradizendo `MEMORY.md` ("quando algo é salvo") e `ACCEPTANCE_CRITERIA.md` (remoção de memória precisa funcionar). Decisão tomada com Jams em 2026-09-06 (opção "tools de escrita conversacionais"), documentada em `TOOLS.md`.
2. **`memory_entries`: mesma `key`+`category` do mesmo usuário sobrescreve, não versiona.** Resolve o "A DEFINIR" de `MEMORY.md` sobre atualização de memória contraditória — decisão técnica, sem recomendação prévia no documento; escolhida por consistência com o resto do V1 (nenhuma outra entidade é versionada).
3. **Critério de relevância de `MEMORY.md` resolvido tecnicamente**: preferências vão inteiras ao `Context` a cada turno (poucas, devem moldar o comportamento de forma consistente); fatos/decisões são filtrados por correspondência de palavra com a mensagem atual, limitados a 5 por turno. Documentado em `MEMORY.md` e implementado em `tools/memory.py:select_relevant_context`.
4. **`Context` (memória/preferências/padrões) passou a ser efetivamente usado pelo Adapter.** Até a FASE 5, `OllamaAdapter.generate()` recebia `context` mas nunca o utilizava — o parâmetro existia no contrato (LLM.md) mas não chegava ao modelo. Corrigido nesta fase: memória/preferências relevantes são enviadas como uma mensagem `system` adicional. `context.patterns` continua sem uso — formato fica para a FASE 7 (`PATTERN_ENGINE.md`).
5. **Escopo de memória limitado a `memory_entries` (memória permanente)**, conforme o próprio texto do `ROADMAP.md` ("Implementar MEMORY.md: memory_entries, recuperação de contexto relevante"). Memória temporária (camada 2 de `MEMORY.md`, ex.: "hoje estou cansado", sem tabela em `DATABASE.md`) não foi implementada nesta fase.
