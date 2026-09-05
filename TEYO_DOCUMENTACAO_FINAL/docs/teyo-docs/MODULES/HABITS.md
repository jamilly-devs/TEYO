# MODULES/HABITS.md — Hábitos

1. **Objetivo**: acompanhar hábitos recorrentes do usuário.
2. **Funcionalidades**: criar hábito, registrar ocorrência (log), acompanhar sequência (streak).
3. **Telas**: lista de hábitos com indicação de progresso/sequência.
4. **Componentes**: item de hábito, indicador de streak.
5. **Dados**: `habits`, `habit_logs` (ver `DATABASE.md`).
6. **Ações**: criar hábito, registrar log — nomes de tool específicos não estão na lista base de `TOOLS.md` (que cobre principalmente tasks/events/goals/market); A DEFINIR se hábitos usam tools próprias (`create_habit`, `log_habit`) ou se são tratados via tools genéricas. OPÇÃO RECOMENDADA: criar `create_habit` e `log_habit` seguindo o mesmo contrato das demais tools.
7. **Regras de negócio**: um log isolado fora do padrão é exceção, não quebra o hábito (ver `PATTERN_ENGINE.md`).
8. **Interação com TEYO**: usuário pode registrar cumprimento de hábito conversando.
9. **Interação com outros módulos**: alimenta Motor de Padrões e gamificação (streak).
10. **V1**: criação e registro de log, visualização de streak.
11. **Depois**: lembretes automáticos programados, hábitos compartilhados entre usuários — não mencionados no histórico, FORA DO V1.
