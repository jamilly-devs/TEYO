# MODULES/HOUSE.md — Casa

Nota de nomenclatura: módulo chamado "Casa" no produto; arquivo nomeado `HOUSE.md` por consistência técnica em inglês (ver `DOCUMENTATION_AUDIT.md`).

1. **Objetivo**: organizar tarefas e responsabilidades domésticas.
2. **Funcionalidades**: gerenciamento de tarefas de casa (reutiliza o módulo Tarefas com categorização de "casa" — não há uma entidade de dados separada decidida no histórico).
3. **Telas**: A DEFINIR se existe tela própria ou se é uma visão filtrada de Tarefas por categoria "casa". OPÇÃO RECOMENDADA: tratar como categoria de `tasks` no V1, sem tabela própria, até decisão de funcionalidades específicas de Casa.
4. **Componentes**: reaproveita componentes de Tarefas.
5. **Dados**: reaproveita `tasks` com categoria; nenhum campo de categoria foi formalmente decidido no schema — NECESSÁRIO PARA IMPLEMENTAÇÃO adicionar um campo de categoria/módulo em `tasks` se essa abordagem for confirmada.
6. **Ações**: reaproveita `create_task`/`update_task`/`complete_task`.
7. **Regras de negócio**: DECIDIDO e explícito — **não existe módulo de pets**; a ideia foi removida e não deve ser implementada sob nenhuma justificativa.
8. **Interação com TEYO**: criação de tarefas domésticas por conversa (ex.: "tarefas domésticas à noite" é o exemplo usado para o Motor de Padrões).
9. **Interação com outros módulos**: alimenta o Motor de Padrões (exemplo central usado no histórico para explicar exceção vs. mudança de rotina).
10. **V1**: tarefas de casa como categoria de Tarefas.
11. **Depois**: DECIDIDO — quando existir multiusuário, deverá ser possível indicar um responsável por uma tarefa de casa (campo de responsável). FORA DO V1 a implementação completa, mas o schema de `tasks` deve deixar espaço para um campo de responsável futuro (ver `ARCHITECTURE.md`, preparação multiusuário).
