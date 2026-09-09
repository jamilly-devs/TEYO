# API.md

## Camadas (DECIDIDO em ARCHITECTURE.md)

Frontend → Backend (API) → Orquestrador → LLM Adapter / Tools / Motor de Padrões → Banco.

O frontend nunca acessa o banco ou o LLM diretamente. Toda comunicação passa pelo backend.

## Endpoints necessários (NECESSÁRIO PARA IMPLEMENTAÇÃO — nível de especificação, não implementação)

### Conversa
- `POST /conversation/message` — envia mensagem do usuário, retorna resposta do TEYO (texto + efeitos colaterais já aplicados via tools).
- `GET /conversation/history` — histórico paginado da conversa principal.

### Tarefas
- `GET /tasks`, `POST /tasks`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}`, `POST /tasks/{id}/complete`.

### Hábitos
- `GET /habits`, `POST /habits`, `PATCH /habits/{id}`, `POST /habits/{id}/log`. Implementados na FASE 10. `GET`/`POST`/`PATCH` retornam o hábito com `streak` (semanas seguidas batendo a frequência-alvo). `POST /{id}/log` é idempotente por dia. Sem DELETE.

### Objetivos
- `GET /goals`, `POST /goals`, `PATCH /goals/{id}`.

### Agenda
- `GET /events`, `POST /events`, `PATCH /events/{id}`, `DELETE /events/{id}`.

### Mercado
- `GET /market`, `POST /market/items`, `PATCH /market/items/{id}` (status, ex.: marcar como comprado — não remove a linha), `DELETE /market/items/{id}` (exclusão definitiva — ver `MODULES/MARKET.md`, resolvido na FASE 5).

### Finanças
- `GET /finance/records`, `POST /finance/records`.

### Estudos, Casa
- **Sem endpoints próprios** (DECIDIDO na FASE 10). São visões filtradas de Tarefas por `category` (`studies` / `house`); o frontend consome `GET /tasks` e filtra. Nenhum CRUD paralelo.

### Carreira
- `GET /career/applications`, `POST /career/applications`, `PATCH /career/applications/{id}`. Implementados na FASE 10 — acompanhamento manual de candidaturas. Sem DELETE (como Objetivos). Sem endpoint de busca de vagas.

### Planejamento
- `GET /planner/daily-plan`
- `POST /planner/reorganize`

### Padrões
- `GET /patterns` (uso interno do Orquestrador, não necessariamente exposto ao frontend no V1)

### Gamificação / Mascote
- `GET /gamification/state` — implementado na FASE 9 (nível, XP, streak, conquistas).
- `GET /mascot/state` — estágio (derivado do nível), expressão, cor, `unlocked_features`.
- `PATCH /mascot/color` — única personalização visual do usuário; valida hex, 422 se inválido.

### Pomodoro
- Implementado na FASE 10 (ver `MODULES/POMODORO.md`): `POST /pomodoro/sessions`, `GET /pomodoro/sessions/active`, `POST /pomodoro/sessions/{id}/pause`, `.../resume`, `.../complete`.
- **Exceção à regra geral abaixo**: Pomodoro **não** tem tool de LLM 1:1 (DT-9) — é experiência de timer/UI. Registrado no `DOCUMENTATION_AUDIT.md` (FASE 10).

## Regra geral

Todo endpoint que altera dados corresponde a exatamente uma tool usada pelo LLM (ver `TOOLS.md`), para que a mesma ação seja possível tanto pela tela quanto pela conversa, com a mesma validação de regras de negócio. **Exceção documentada:** os endpoints de Pomodoro (FASE 10) não têm tool correspondente.

## Fora do V1

Não criar endpoints de Notícias ou Relatórios na V1. Esses módulos são V2+.
