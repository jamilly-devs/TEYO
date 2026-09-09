# MODULES/STUDIES.md — Estudos

1. **Objetivo**: organizar atividades de estudo do usuário (ex.: inglês, QA).
2. **Funcionalidades**: DECIDIDO no nível de exemplos de conversa (doc. 3, item 4): "quero estudar inglês por uma hora amanhã" deve virar uma tarefa/compromisso de estudo. Não há, no histórico, uma funcionalidade de Estudos estruturalmente diferente de Tarefas/Agenda além dessa associação temática.
3. **Telas** (DECIDIDO na FASE 10): **não** há tela própria nem CRUD paralelo. `frontend/src/screens/studies/StudiesScreen.tsx` é a tela de Tarefas (`TasksScreen`) filtrada pela categoria `studies` (`categoryFilter="studies"`), com atalho na navegação e na Home. O formulário de criação já vem com a categoria pré-selecionada.
4. **Componentes**: reaproveita 100% de Tarefas — nenhum componente novo.
5. **Dados** (DECIDIDO na FASE 10): **sem tabela própria**. Usa `tasks.category = 'studies'` (`TaskCategory.STUDIES`, já no enum). Um compromisso de estudo é um `event` normal, **sem categoria** — `events` não ganha campo de categoria no V1.
6. **Ações**: reaproveita `create_task`/`create_event`.
7. **Regras de negócio**: nenhuma regra específica adicional foi decidida além das de Tarefas/Agenda.
8. **Interação com TEYO**: criação de sessão de estudo por linguagem natural.
9. **Interação com outros módulos**: Carreira (ex.: estudar para QA), Motor de Padrões (horário de estudo recorrente, ex. "estudo → noite" no exemplo do histórico).
10. **V1** (FASE 10): estudo como tarefa categorizada (`studies`); tela = visão filtrada de Tarefas.
11. **Depois**: qualquer funcionalidade de trilha de estudo, flashcards, etc. — não mencionada, FORA DO V1.
