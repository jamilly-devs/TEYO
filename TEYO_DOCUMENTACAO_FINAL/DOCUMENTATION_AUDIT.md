# DOCUMENTATION_AUDIT.md

Auditoria realizada antes da entrega deste pacote. Lista de pontos identificados — nenhum foi resolvido arbitrariamente; cada um está marcado com o tratamento dado.

## Contradições / ambiguidades encontradas

1. **Mercado — "remover da lista"**: o briefing de documentação (mensagem do usuário desta tarefa) afirma que "não queremos a funcionalidade de simplesmente 'remover da lista' como conceito principal anteriormente discutido". O histórico consolidado de decisões não registra essa frase nem essa decisão de forma explícita — apenas reforça simplicidade, categorias, itens recorrentes e sugestões. **Tratamento**: mantido como A DEFINIR em `MODULES/MARKET.md`, sem resolver a favor de nenhuma das duas leituras. Precisa de esclarecimento direto de Jams antes da FASE 10 do roadmap.

2. **Nome de arquivo "Casa" vs. "HOUSE.md"**: o produto usa o nome "Casa" (português) para o módulo; por consistência com os demais arquivos de `MODULES/` (nomes técnicos em inglês, ex. `TASKS.md`, `FINANCE.md`), o arquivo foi nomeado `HOUSE.md`. **Tratamento**: não é uma decisão de produto, é convenção de nomenclatura de arquivo — sinalizado em `MODULES/HOUSE.md` e aqui para não ser confundido com renomeação do módulo em si.

## Funcionalidades removidas que poderiam reaparecer (ponto de atenção)

3. **Módulo de pets**: removido explicitamente em dois pontos do histórico (doc. 1 e doc. 3, item 21/46). Reforçado como regra em `BUSINESS_RULES.md`, `MODULES/HOUSE.md` e `CLAUDE_CODE_INSTRUCTIONS.md` para reduzir risco de reaparecer por engano durante a implementação do módulo Casa.

## Requisitos com decisão de produto mas sem valor técnico definido (não são contradições, são pendências esperadas — listadas para rastreabilidade)

4. Janela de observação e limiares de confiança do Motor de Padrões (`PATTERN_ENGINE.md`).
5. Regras exatas de XP/nível/conquistas da Gamificação (`GAMIFICATION.md`).
6. Estágios exatos de evolução visual do mascote (`MASCOT.md`).
7. Mecanismo concreto de busca de vagas em Carreira (`MODULES/CAREER.md`).
8. Fonte técnica de notícias (`MODULES/NEWS.md`).
9. Stack técnica de frontend/backend e runtime de hospedagem do Qwen3.5-4B (`ARCHITECTURE.md`, `LLM.md`).
10. Algoritmo de priorização do Planejador em caso de conflito entre itens sem horário fixo (`PLANNER.md`).

Nenhum desses itens foi transformado em decisão definitiva nesta documentação — todos aparecem como A DEFINIR com OPÇÃO RECOMENDADA quando havia uma proposta razoável a registrar.

## Cobertura verificada

- Toda tabela em `DATABASE.md` tem pelo menos uma tool ou fluxo que a usa, exceto `pattern_events` e `productivity_logs`, que são alimentadas por processos internos (registro automático a partir de outras ações), não por uma tool chamada pelo LLM — comportamento esperado, não uma lacuna.
- Toda tool em `TOOLS.md` corresponde a pelo menos um endpoint em `API.md` ou está marcada como uso interno (`get_patterns`, `get_routine_changes`).
- Todo módulo em `MODULES/` tem ao menos um fluxo relacionado em `FLOWS.md`, exceto Notícias e Relatórios, que são majoritariamente de leitura — tratados nos fluxos 8 (produtividade) e implicitamente cobertos pelo padrão de leitura das demais tools `get_*`.
- Nenhuma tabela foi criada em `DATABASE.md` sem uma tela ou tool correspondente documentada.

## Itens explicitamente fora desta auditoria

- Conformidade legal/LGPD (mencionada como necessária antes de publicação, mas fora do escopo técnico do V1 — ver `MEMORY.md`).
- Qualquer decisão de UI visual final (assets), que depende de material ainda não entregue a esta documentação.
