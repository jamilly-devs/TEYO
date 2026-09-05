# MODULES/GOALS.md — Objetivos

1. **Objetivo**: acompanhamento de objetivos de médio/longo prazo do usuário.
2. **Funcionalidades**: criação, acompanhamento, progresso, relação com tarefas.
3. **Telas**: lista de objetivos com progresso.
4. **Componentes**: card de objetivo com status/progresso.
5. **Dados**: `goals` (ver `DATABASE.md`); `tasks.goal_id` relaciona tarefas ao objetivo.
6. **Ações**: `create_goal`, `update_goal` (ver `TOOLS.md`).
7. **Regras de negócio**: progresso de objetivo é calculado pelo sistema a partir das tarefas associadas concluídas, nunca estimado pelo LLM.
8. **Interação com TEYO**: usuário pode conversar sobre mudar um objetivo ("quero mudar meu objetivo") e o TEYO deve identificar qual objetivo e o que muda antes de chamar `update_goal`.
9. **Interação com outros módulos**: tarefas associadas; relatórios usam progresso de objetivos.
10. **V1**: CRUD de objetivo + associação com tarefas + progresso calculado.
11. **Depois**: objetivos com sub-objetivos/hierarquia — não mencionado no histórico, A DEFINIR.
