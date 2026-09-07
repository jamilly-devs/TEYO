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
11. **RESOLVIDO na FASE 5 (ver `DOCUMENTATION_AUDIT.md`)**: "tirar item da lista" tem dois mecanismos distintos e ambos existem: marcar como comprado (`status = purchased`, via `PATCH /market/items/{id}`, não remove a linha — disponível hoje só pela tela, não há tool de conversa para isso na FASE 5) e excluir definitivamente (`remove_market_item` / `DELETE /market/items/{id}`, hard delete — disponível pela tela e pela conversa). A contradição citada nas versões anteriores deste documento (doc. 1 vs. doc. 3, item 20) fica resolvida por essa distinção: exclusão definitiva é uma ação separada e destrutiva da marcação de "comprado", e exige confirmação explícita do usuário quando acionada pela conversa.
