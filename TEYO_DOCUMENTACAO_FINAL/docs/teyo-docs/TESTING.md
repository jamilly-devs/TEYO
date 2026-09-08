# TESTING.md

## Estratégia por camada

- **Unitários**: regras de negócio isoladas (ex.: cálculo de confiança do Motor de Padrões, validação de parâmetros de cada tool, cálculo de progresso de objetivo).
- **Integração**: fluxo tool → banco (ex.: `create_task` grava corretamente em `tasks`); fluxo Orquestrador → LLM Adapter com um modelo mock/stub, sem depender do Qwen3.5-4B real para testes determinísticos.
- **Frontend**: renderização dos estados de tela (loading, vazio, erro, sucesso) por módulo (ver `UX.md`).
- **Backend**: endpoints de `API.md` com casos de sucesso e de erro (`ERROR_HANDLING.md`).
- **Banco**: migrações aplicam sem erro; constraints de FK e índices descritos em `DATABASE.md` existem de fato.
- **Tools**: cada tool de `TOOLS.md` testada isoladamente com parâmetros válidos, inválidos e ausentes.
- **LLM**: testes de contrato do Adapter (entrada/saída conforme `LLM.md`), usando um modelo real ou um stub determinístico para CI.
- **Memória**: entradas de `memory_entries` são criadas/atualizadas/removidas conforme `MEMORY.md`.
- **Motor de Padrões**: casos sintéticos replicando o exemplo do histórico (21 dias / 18 noite / 3 manhã → predominante noite; 7 dias recentes / 6 manhã / 1 noite → possível mudança) para validar que a lógica não promove padrão a partir de um evento isolado.
- **Planejador**: casos sintéticos cobrindo o algoritmo confirmado com Jams na FASE 8 (`PLANNER.md`) — eventos e tarefas com `due_date` como âncoras cronológicas por período do dia; tarefas sem `due_date` ordenadas por prioridade, com padrão `active` de `task_time_of_day` como critério adicional de período e `created_at` como desempate; tarefas sem período disponível ao final da lista; `reorganize_day` com `energy_level: "low"` adiando só tarefas sem horário de maior esforço (`priority = high` e/ou `pomodoro_enabled`), nunca tocando âncoras; sobreposição de `events` sinalizada (`conflict`/HTTP 409) e nunca criada sem `confirm_overlap`.
- **Fluxos críticos**: os 15 fluxos de `FLOWS.md`, cobrindo o caminho feliz e ao menos um caminho de erro/ambiguidade cada.
- **Regressão**: qualquer regra de `BUSINESS_RULES.md` violada por uma mudança futura deve falhar em teste automatizado antes de chegar à FASE seguinte do roadmap.

## Critérios de aceitação por funcionalidade

Ver `ACCEPTANCE_CRITERIA.md`.
