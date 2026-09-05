# MODULES/MARKET.md — Mercado

1. **Objetivo**: lista de compras simples e prática.
2. **Funcionalidades**: adicionar item, organizar por categoria (ex.: hortifruti, limpeza), itens recorrentes, sugestões baseadas em histórico.
3. **Telas**: lista de mercado agrupada por categoria.
4. **Componentes**: item de mercado (nome, categoria).
5. **Dados**: `market_items` (ver `DATABASE.md`).
6. **Ações**: `add_market_item`, `remove_market_item` (ver `TOOLS.md`).
7. **Regras de negócio**: DECIDIDO — não mostrar quem adicionou o item nem quantidade detalhada; não deixar o módulo complexo.
8. **Interação com TEYO**: exemplo do histórico — "coloca café no mercado" / "na verdade tira o café e coloca arroz" (o TEYO precisa entender substituição em uma única frase).
9. **Interação com outros módulos**: sugestões podem usar Motor de Padrões (histórico de compras recorrentes).
10. **V1**: adicionar item, categorizar, marcar itens recorrentes, sugestão por histórico.
11. **A DEFINIR (contradição a resolver, ver `DOCUMENTATION_AUDIT.md`)**: o briefing de documentação (doc. 1) menciona que "não queremos a funcionalidade de simplesmente 'remover da lista' como conceito principal anteriormente discutido", mas o histórico consolidado (doc. 3, item 20) não registra essa decisão de forma explícita — só reforça simplicidade e categorização. A mecânica exata de "tirar item da lista" (excluir vs. marcar como comprado) fica A DEFINIR até esclarecimento; a tool `remove_market_item` existe no contrato, mas seu comportamento exato depende dessa decisão.
