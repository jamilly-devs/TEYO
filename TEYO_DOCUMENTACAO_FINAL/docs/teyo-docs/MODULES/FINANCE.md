# MODULES/FINANCE.md — Finanças

1. **Objetivo**: organizar finanças pessoais do usuário.
2. **Funcionalidades**: registro de dados financeiros, cálculos, acompanhamento — acessível diretamente pela tela e também via conversa com o TEYO (DECIDIDO, doc. 3, item 19).
3. **Telas**: tela de Finanças com lista/resumo de registros financeiros.
4. **Componentes**: item de registro financeiro (tipo, valor, categoria, data).
5. **Dados**: `financial_records` (ver `DATABASE.md`).
6. **Ações**: criação de registro financeiro — nome de tool específico (`create_financial_record` ou similar) não está na lista base de `TOOLS.md`; NECESSÁRIO PARA IMPLEMENTAÇÃO adicionar seguindo o mesmo contrato.
7. **Regras de negócio**: cálculos financeiros são feitos pelo sistema; o LLM apenas interpreta e conversa sobre os dados; DECIDIDO — não criar integrações bancárias no V1.
8. **Interação com TEYO**: usuário pode registrar/consultar dados financeiros conversando.
9. **Interação com outros módulos**: Relatórios (resumo financeiro).
10. **V1**: registro manual de dados financeiros + cálculos básicos + consulta via TEYO.
11. **Depois**: integrações bancárias — explicitamente FORA DO V1 (DECIDIDO).
