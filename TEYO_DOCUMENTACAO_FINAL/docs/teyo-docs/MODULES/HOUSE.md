# MODULES/HOUSE.md — Casa

Nota de nomenclatura: módulo chamado "Casa" no produto; arquivo nomeado `HOUSE.md` por consistência técnica em inglês (ver `DOCUMENTATION_AUDIT.md`).

1. **Objetivo**: organizar tarefas e responsabilidades domésticas.
2. **Funcionalidades**: gerenciamento de tarefas de casa (reutiliza o módulo Tarefas com categorização de "casa" — não há uma entidade de dados separada decidida no histórico).
3. **Telas** (DECIDIDO na FASE 10): visão filtrada de Tarefas por categoria "casa". `frontend/src/screens/house/HouseScreen.tsx` = `TasksScreen` com `categoryFilter="house"`. Sem tela própria, sem CRUD paralelo.
4. **Componentes**: reaproveita 100% de Tarefas.
5. **Dados** (DECIDIDO na FASE 10): usa `tasks.category = 'house'` (`TaskCategory.HOUSE`, já no enum desde a FASE 1). **Sem tabela própria.** O campo `category` em `tasks` já existe — nada a acrescentar ao schema.
6. **Ações**: reaproveita `create_task`/`update_task`/`complete_task`.
7. **Regras de negócio**: DECIDIDO e explícito — **não existe módulo de pets**; a ideia foi removida e não deve ser implementada sob nenhuma justificativa.
8. **Interação com TEYO**: criação de tarefas domésticas por conversa (ex.: "tarefas domésticas à noite" é o exemplo usado para o Motor de Padrões).
9. **Interação com outros módulos**: alimenta o Motor de Padrões (exemplo central usado no histórico para explicar exceção vs. mudança de rotina).
10. **V1**: tarefas de casa como categoria de Tarefas.
11. **Depois**: DECIDIDO — quando existir multiusuário, deverá ser possível indicar um responsável por uma tarefa de casa (campo de responsável). **FORA DO V1** (confirmado na FASE 10): `tasks` **não** ganha campo de responsável nesta versão; fica para V2/multiusuário (ver `ARCHITECTURE.md`).
