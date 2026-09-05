# PLANNER.md

DECIDIDO: existe um Plano do Dia, componente do sistema (não do LLM), que considera tarefas, compromissos, prioridades, horários, hábitos, objetivos, padrões de rotina, horários de maior produtividade, preferências e restrições informadas pelo usuário.

## get_daily_plan

Monta a lista ordenada de tarefas/compromissos do dia combinando:
- `events` do dia (compromissos fixos, não podem ser movidos automaticamente).
- `tasks` com `due_date` no dia ou sem data mas priorizadas.
- Padrões ativos de horário de produtividade (`routines` com `pattern_type = productivity_time`) para sugerir posicionamento de tarefas cognitivamente pesadas — DECIDIDO como uso, não obrigatório (doc. 3, item 11: "isso não significa que o sistema deve obrigatoriamente colocar tudo nesse horário").

## reorganize_day

DECIDIDO: acionado quando o usuário pede explicitamente (ex.: "estou cansado hoje, reorganiza meu dia"). O Orquestrador traduz a mensagem em restrições estruturadas (ex.: `energy_level: low`) antes de chamar a tool.

DECIDIDO (doc. 3, item 33): o TEYO sugere, não impõe. O resultado de `reorganize_day` é uma proposta; a aplicação definitiva das mudanças (ex.: alterar `due_date`/horário de várias tasks) só ocorre após confirmação do usuário, seguindo a mesma regra de ações destrutivas/impactantes de `BUSINESS_RULES.md`.

## Relação com o Motor de Padrões

O planejador consome `get_patterns` (padrões `active`) para: (1) evitar sobrecarregar horários que o histórico mostra como de baixa produtividade, (2) sugerir horário para tarefas de determinada categoria com base no padrão predominante.

## A DEFINIR

- Algoritmo exato de priorização/ordenação quando há conflito entre vários itens sem horário fixo (ex.: duas tarefas de mesma prioridade).
- Como o planejador lida com sobreposição de compromissos (`events` conflitantes) — se apenas sinaliza o conflito ou impede a criação. OPÇÃO RECOMENDADA: sinalizar o conflito ao usuário via TEYO e pedir confirmação antes de criar um evento sobreposto, nunca bloquear silenciosamente.
