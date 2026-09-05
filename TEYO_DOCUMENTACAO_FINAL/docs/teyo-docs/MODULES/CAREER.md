# MODULES/CAREER.md — Carreira

1. **Objetivo**: acompanhar a trajetória de carreira do usuário e ajudar na busca de vagas.
2. **Funcionalidades**: DECIDIDO — existe interesse do usuário em o TEYO ajudar a buscar vagas, mantendo o produto sem custo de API de LLM paga.
3. **Telas**: A DEFINIR — não há decisão sobre tela específica de busca de vagas além do módulo Carreira existir.
4. **Componentes**: A DEFINIR.
5. **Dados**: A DEFINIR (nenhuma tabela específica de vagas/carreira foi decidida; ver nota em `DATABASE.md`).
6. **Ações**: A DEFINIR — nenhuma tool de busca de vaga foi decidida.
7. **Regras de negócio**: DECIDIDO — não usar API paga de LLM para a busca; qualquer mecanismo concreto de busca (scraping próprio, feeds públicos, etc.) fica A DEFINIR.
8. **Interação com TEYO**: usuário pode conversar sobre carreira/progresso de estudo relacionado a QA.
9. **Interação com outros módulos**: Estudos (preparação), Objetivos (meta de conseguir vaga), Relatórios.
10. **V1**: A DEFINIR — o histórico registra apenas a intenção; a implementação concreta da busca de vagas não está detalhada o suficiente para ir ao V1 sem uma decisão adicional. OPÇÃO RECOMENDADA: no V1, o módulo Carreira funciona como acompanhamento manual (registro de candidaturas, status) sem busca automatizada; a busca de vagas fica marcada como FUTURO até haver decisão de mecanismo.
11. **Depois**: busca automatizada de vagas via fontes próprias/ferramentas gratuitas — FUTURO, mecanismo A DEFINIR.
