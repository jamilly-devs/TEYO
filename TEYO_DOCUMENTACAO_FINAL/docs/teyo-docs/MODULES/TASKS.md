# MODULES/TASKS.md — Tarefas

1. **Objetivo**: gerenciar tarefas do usuário, um dos pilares do TEYO (DECIDIDO, doc. 3, item 9).
2. **Funcionalidades**: criar, editar, concluir, reagendar, excluir, organizar, associar a objetivos quando fizer sentido, planejar para períodos específicos.
3. **Telas**: lista de tarefas (tela própria), possivelmente com filtro por status/data. Formulário de criação/edição.
4. **Componentes**: item de tarefa (título, status, data, indicador de Pomodoro habilitado), formulário.
5. **Dados**: tabela `tasks` (ver `DATABASE.md`).
6. **Ações**: `create_task`, `update_task`, `delete_task`, `complete_task` (ver `TOOLS.md`).
7. **Regras de negócio**: tarefa única não vira recorrente automaticamente; exclusão exige confirmação; Pomodoro é opcional (ver `BUSINESS_RULES.md`).
8. **Interação com TEYO**: criação/edição/conclusão por linguagem natural (ex.: "joga essa tarefa para amanhã à noite" — o TEYO precisa resolver qual tarefa, nova data e horário antes de chamar `update_task`).
9. **Interação com outros módulos**: pode se associar a `goals` (objetivo); alimenta o Motor de Padrões (histórico de horários de conclusão); alimenta gamificação ao ser concluída; alimenta o Planejador.
10. **V1**: CRUD completo + Pomodoro opcional + associação a objetivo.
11. **Depois**: subtarefas, tags livres, dependências entre tarefas — não mencionadas no histórico, portanto A DEFINIR/FORA DO V1 até decisão explícita.
