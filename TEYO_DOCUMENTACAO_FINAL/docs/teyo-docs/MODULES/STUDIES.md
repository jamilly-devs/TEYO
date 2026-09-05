# MODULES/STUDIES.md — Estudos

1. **Objetivo**: organizar atividades de estudo do usuário (ex.: inglês, QA).
2. **Funcionalidades**: DECIDIDO no nível de exemplos de conversa (doc. 3, item 4): "quero estudar inglês por uma hora amanhã" deve virar uma tarefa/compromisso de estudo. Não há, no histórico, uma funcionalidade de Estudos estruturalmente diferente de Tarefas/Agenda além dessa associação temática.
3. **Telas**: A DEFINIR se existe tela própria de Estudos ou se estudos são apenas tarefas/eventos categorizados como "estudo". OPÇÃO RECOMENDADA: tratar Estudos como uma categoria/tag sobre `tasks`/`events`, sem tabela própria no V1, até haver decisão de funcionalidades específicas (ex.: trilhas de estudo).
4. **Componentes**: reaproveita componentes de Tarefas/Agenda.
5. **Dados**: reaproveita `tasks`/`events` com categorização — schema de categoria específica A DEFINIR.
6. **Ações**: reaproveita `create_task`/`create_event`.
7. **Regras de negócio**: nenhuma regra específica adicional foi decidida além das de Tarefas/Agenda.
8. **Interação com TEYO**: criação de sessão de estudo por linguagem natural.
9. **Interação com outros módulos**: Carreira (ex.: estudar para QA), Motor de Padrões (horário de estudo recorrente, ex. "estudo → noite" no exemplo do histórico).
10. **V1**: estudo como tarefa/compromisso categorizado.
11. **Depois**: qualquer funcionalidade de trilha de estudo, flashcards, etc. — não mencionada, FORA DO V1.
