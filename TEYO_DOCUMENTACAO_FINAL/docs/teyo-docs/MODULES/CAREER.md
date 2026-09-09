# MODULES/CAREER.md — Carreira

1. **Objetivo**: acompanhar a trajetória de carreira do usuário e ajudar na busca de vagas.
2. **Funcionalidades**: DECIDIDO — existe interesse do usuário em o TEYO ajudar a buscar vagas, mantendo o produto sem custo de API de LLM paga.
3. **Telas** (DECIDIDO na FASE 10): uma tela simples de acompanhamento manual de candidaturas — `frontend/src/screens/career/CareerScreen.tsx` (listar, criar, atualizar status). Sem tela de busca de vagas.
4. **Componentes**: formulário de candidatura + lista com seletor de status. Reaproveita `ScreenStates` e o padrão de `GoalsScreen`.
5. **Dados** (DECIDIDO na FASE 10): tabela **`job_applications`** (ver `DATABASE.md`). Campos: `company`, `role`, `applied_on` (data da candidatura, nullable), `status`, `notes`, `created_at`, `updated_at`.
6. **Ações** (DECIDIDO na FASE 10): endpoints `GET/POST /career/applications`, `PATCH /career/applications/{id}` (sem DELETE, como Objetivos) e tools equivalentes `create_job_application`, `update_job_application`, `list_job_applications`. **Nenhuma** tool/endpoint de busca de vagas.
7. **Regras de negócio**: DECIDIDO — **não** usar API paga de LLM para busca; **não** implementar busca automatizada de vagas no V1. O status segue um fluxo simples: `interested` → `applied` → `interviewing` → `offer` / `rejected` (valores em inglês, mesmo padrão de `GoalStatus`; rótulos PT no frontend). Busca automatizada continua **FUTURO**, mecanismo A DEFINIR.
8. **Interação com TEYO**: usuário pode conversar sobre carreira/progresso de estudo relacionado a QA.
9. **Interação com outros módulos**: Estudos (preparação), Objetivos (meta de conseguir vaga), Relatórios.
10. **V1** (DECIDIDO na FASE 10): acompanhamento **manual** de candidaturas (registrar, listar, atualizar status/observações). Sem busca automatizada. Relaciona-se conceitualmente com Estudos, Objetivos e Tarefas, mas **sem automações** entre módulos nesta fase.
11. **Depois**: busca automatizada de vagas via fontes próprias/ferramentas gratuitas — FUTURO, mecanismo A DEFINIR.
