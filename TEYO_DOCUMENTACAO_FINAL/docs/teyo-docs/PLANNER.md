# PLANNER.md

DECIDIDO: existe um Plano do Dia, componente do sistema (não do LLM), que considera tarefas, compromissos, prioridades, horários, hábitos, objetivos, padrões de rotina, horários de maior produtividade, preferências e restrições informadas pelo usuário.

**Escopo real implementado na FASE 8** (decisão registrada em `DOCUMENTATION_AUDIT.md`, mesmo raciocínio da FASE 7 para o Motor de Padrões): só `tasks` + `events` + padrões `task_time_of_day` (único `pattern_type` real da FASE 7). Hábitos (`habits`/`habit_logs`, sem módulo construído), progresso de `goals` (nunca implementado desde a FASE 2) e um padrão `productivity_time` (nunca existiu — só `task_time_of_day` foi implementado) não são usados. Nenhuma tool/endpoint de fases anteriores foi alterada para alimentar dado novo; `tools/events.py`/`api/routers/events.py` foram tocados apenas para a sinalização de conflito, que já era responsabilidade explícita desta fase (ver abaixo).

## get_daily_plan

Monta a lista ordenada de tarefas/compromissos do dia combinando `events`/`tasks` de hoje (compromissos fixos, nunca movidos automaticamente) com tarefas sem `due_date`, priorizadas, e com padrões `active` de `task_time_of_day` para sugerir o período do dia de tarefas de determinada categoria — DECIDIDO como uso, não obrigatório.

### Algoritmo de ordenação (DECIDIDO com Jams em 2026-09-08 — Opção A, ver `DOCUMENTATION_AUDIT.md`)

1. Eventos e tarefas com `due_date` hoje são âncoras: cada um cai no período do dia (madrugada/manhã/tarde/noite, mesma divisão de `PATTERN_ENGINE.md`) da sua própria hora, em ordem cronológica dentro do período.
2. Tarefas sem `due_date` são ordenadas primariamente por `priority` (critério principal); quando existe um padrão `active` de `task_time_of_day` para a categoria da tarefa, ela é posicionada no período predominante desse padrão (critério adicional); dentro do mesmo período a ordem continua por prioridade, com `created_at` como desempate final. Tarefas sem `due_date` e sem padrão ativo para a categoria (ou sem categoria) formam um grupo "sem período" ao final da lista — não inventa um horário que nenhum dado sustenta.
3. Dentro de um mesmo período, as tarefas sem horário fixo aparecem antes dos itens-âncora daquele período (não há duração estimada em `tasks`/`events` para tentar encaixá-las entre compromissos).

Implementado em `backend/planner/daily_plan.py`.

## reorganize_day

DECIDIDO: acionado quando o usuário pede explicitamente (ex.: "estou cansado hoje, reorganiza meu dia"). O parâmetro estruturado da tool é `energy_level` (enum `low`/`medium`/`high`) — o próprio LLM já produz esse valor ao chamar a tool (mesmo mecanismo de tool-calling tipado usado por `create_event`), sem uma etapa separada de NLU no Orquestrador.

DECIDIDO (doc. 3, item 33): o TEYO sugere, não impõe. O resultado de `reorganize_day` é uma proposta; a aplicação definitiva das mudanças (`update_task`/`update_event` normais, chamada por chamada) só ocorre após confirmação do usuário (`FLOWS.md` item 5).

### Efeito de `energy_level` (DECIDIDO com Jams em 2026-09-08 — Opção A, ver `DOCUMENTATION_AUDIT.md`)

Só `energy_level = "low"` tem efeito: tarefas sem horário fixo consideradas de maior esforço (`priority = high` e/ou `pomodoro_enabled = true` — não existe estimativa de duração/esforço no schema, então só esses dois campos já existentes são usados) são movidas para o fim da lista de hoje, com uma sugestão (não aplicada) de adiar para amanhã (`suggested_due_date`). Eventos fixos e tarefas já com horário marcado nunca são tocados. `medium`/`high`/ausente devolvem o mesmo plano de `get_daily_plan` — nenhum efeito foi inventado para esses valores sem uma métrica real para sustentá-lo. Implementado em `backend/planner/daily_plan.py`.

## Relação com o Motor de Padrões

O planejador consome os padrões `active` de `task_time_of_day` (reconsultando `pattern_engine.task_time_of_day.refresh_patterns_for_user` — nunca recalcula a lógica de padrões) para sugerir o período do dia de tarefas sem horário fixo, por categoria. Não existe padrão `productivity_time` na FASE 7 implementada; a ideia original de "evitar horários de baixa produtividade" fica para quando (e se) esse padrão existir.

## Sobreposição de compromissos (DECIDIDO com Jams em 2026-09-08, ver `DOCUMENTATION_AUDIT.md`)

Adotada a OPÇÃO RECOMENDADA: sinalizar o conflito ao usuário e pedir confirmação, nunca bloquear silenciosamente nem criar por conta própria. Mecanismo técnico (`backend/planner/daily_plan.py:find_overlapping_events`, usado por `tools/events.py` e `api/routers/events.py`): `create_event`/`update_event` que sobrepõem um compromisso existente não criam/alteram nada por padrão — devolvem `conflict: true` com os compromissos conflitantes (tool) ou HTTP 409 (REST); só criam/alteram mesmo assim quando o parâmetro `confirm_overlap: true` é passado explicitamente, depois da confirmação do usuário.

## Escopo de frontend (DECIDIDO com Jams em 2026-09-08)

FASE 8 ficou backend-only (Planejador, tools `get_daily_plan`/`reorganize_day`, endpoints `GET /planner/daily-plan`/`POST /planner/reorganize`), mesmo padrão das FASES 5-7 (`ROADMAP.md` não menciona nenhuma tela para esta fase). `frontend/src/screens/home/HomeScreen.tsx` mantém seu bloco `DailyPlanBlock` atual (filtro client-side ingênuo por "é hoje?", sem ordenação por prioridade/padrão, construído na FASE 3 antes do Planejador existir) — **pendência registrada explicitamente**: esse bloco fica divergente do plano real assim que `get_daily_plan` for usado pela conversa, e precisa ser religado ao endpoint `GET /planner/daily-plan` numa fase/ajuste futuro de frontend dedicado a isso.
