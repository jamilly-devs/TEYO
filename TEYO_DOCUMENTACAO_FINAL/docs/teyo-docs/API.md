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
- `GET /habits`, `POST /habits`, `PATCH /habits/{id}`, `POST /habits/{id}/log`.

### Objetivos
- `GET /goals`, `POST /goals`, `PATCH /goals/{id}`.

### Agenda
- `GET /events`, `POST /events`, `PATCH /events/{id}`, `DELETE /events/{id}`.

### Mercado
- `GET /market`, `POST /market/items`, `PATCH /market/items/{id}` (status), `DELETE /market/items/{id}` — mecanismo exato de remoção A DEFINIR (ver `MODULES/MARKET.md`).

### Finanças
- `GET /finance/records`, `POST /finance/records`.

### Estudos, Carreira, Casa
- Endpoints equivalentes de CRUD conforme dados definidos em `MODULES/STUDIES.md`, `MODULES/CAREER.md`, `MODULES/HOUSE.md` (nome de módulo mantido como "Casa" conforme decisão de produto; arquivo de módulo nomeado `MODULES/HOUSE.md` neste pacote por consistência de nomenclatura técnica em inglês — ver nota em `DOCUMENTATION_AUDIT.md`).

### Planejamento
- `GET /planner/daily-plan`
- `POST /planner/reorganize`

### Padrões
- `GET /patterns` (uso interno do Orquestrador, não necessariamente exposto ao frontend no V1)

### Gamificação / Mascote
- `GET /gamification/state`
- `GET /mascot/state`
- `PATCH /mascot/color`

## Regra geral

Todo endpoint que altera dados corresponde a exatamente uma tool usada pelo LLM (ver `TOOLS.md`), para que a mesma ação seja possível tanto pela tela quanto pela conversa, com a mesma validação de regras de negócio.

## Fora do V1

Não criar endpoints de Notícias ou Relatórios na V1. Esses módulos são V2+.
