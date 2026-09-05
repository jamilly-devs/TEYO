# GAMIFICATION.md

## Decidido

- TEYO terá gamificação (XP, níveis, evolução, progresso, recompensas), relacionada às atividades do usuário nos módulos.
- Elementos de conquista considerados no histórico: sequência (streak), Pomodoro, foco total, produtividade, horas na semana.
- A evolução do mascote está ligada ao progresso de gamificação (ver `MASCOT.md`).
- Cálculo de XP e nível pertence ao sistema, nunca ao LLM (ver `ARCHITECTURE.md`).

## A DEFINIR (explicitamente registrado no histórico como pendente de documentação antes da implementação)

- Quais eventos concedem XP e em qual quantidade (ex.: completar tarefa, manter streak de hábito, sessão de Pomodoro concluída).
- Fórmula de progressão de nível (linear, exponencial, etc.).
- Lista final de conquistas e seus critérios exatos de desbloqueio.
- Relação numérica entre nível e estágio de evolução do mascote.

OPÇÃO RECOMENDADA (não é decisão oficial): começar o V1 com um conjunto mínimo de eventos de XP (completar tarefa, completar hábito do dia, completar sessão de Pomodoro) e uma progressão linear simples, deixando conquistas mais elaboradas para iteração futura — mas isso precisa ser confirmado por Jams antes da FASE 9 do roadmap (Gamificação), já que o histórico marca essas regras como pendentes.

## Persistência

Ver `gamification_state` e `gamification_events` em `DATABASE.md`.

## Interação com TEYO

O TEYO pode comentar eventos de gamificação na conversa (ex.: "Você concluiu 3 tarefas importantes hoje. Orgulho define!"), mas o número/XP em si vem do sistema via tool, nunca é estimado pelo LLM.
