# PATTERN_ENGINE.md

DECIDIDO: o Motor de Padrões é código do próprio TEYO, executado localmente sobre os dados do usuário. Não é um LLM, não é uma API, não tem custo por uso.

## O que ele observa (DECIDIDO)

Frequência, horários, dias, recorrência, tendências, mudanças de comportamento, exceções, confiança do padrão — construído a partir do histórico bruto de cada módulo (`tasks`, `habit_logs`, `pattern_events`, etc.).

**Escopo real implementado na FASE 7** (ver `DOCUMENTATION_AUDIT.md`): só `tasks` (horário de conclusão por categoria) — única fonte com histórico de fato populado pelas FASES 2-6. `habit_logs`, `pattern_events` e `productivity_logs` seguem sem nenhum escritor no código (módulos de Hábitos e Pomodoro ainda não construídos); as tools/endpoints das fases anteriores não foram alteradas para começar a alimentá-las. Cálculo sob demanda (sem worker/job periódico — `FLOWS.md` item 7 deixava o gatilho A DEFINIR sem gate de aprovação nem OPÇÃO RECOMENDADA; decidido tecnicamente por não haver infraestrutura de scheduler no projeto).

## Regra fundamental (DECIDIDO)

Uma única alteração isolada NUNCA é tratada como mudança de rotina. Exemplo do histórico: se o usuário normalmente faz tarefas domésticas à noite e um dia faz de manhã, isso é registrado como **exceção**, não como mudança de padrão.

## Janela de observação (NECESSÁRIO PARA IMPLEMENTAÇÃO / A DEFINIR os números)

O sistema precisa de uma janela de dados históricos para calcular o "período predominante" de um comportamento, e uma janela mais curta e recente para detectar possível mudança de tendência.

Exemplo usado nas discussões (DECIDIDO como exemplo ilustrativo, NÃO como valor de produto):
- Janela histórica de referência: 21 dias — 18 ocorrências à noite, 3 pela manhã → período predominante: noite.
- Janela recente: últimos 7 dias — 6 ocorrências de manhã, 1 à noite → sistema registra "possível mudança de comportamento", mas não promove automaticamente a novo padrão.

DECIDIDO com Jams em 2026-09-07 (ver `DOCUMENTATION_AUDIT.md`): janela histórica de referência de 21 dias e janela recente de 7 dias, replicando o exemplo do histórico. Implementado em `pattern_engine/task_time_of_day.py`.

## Estados de um comportamento (DECIDIDO como taxonomia; NECESSÁRIO PARA IMPLEMENTAÇÃO os critérios numéricos exatos de transição)

1. Ação isolada.
2. Comportamento temporário (poucas ocorrências recentes, ainda sem confiança).
3. Padrão observado (`status = candidate` em `routines`).
4. Rotina aprendida (`status = active`).
5. Mudança de rotina (nova tendência com confiança suficiente para eventualmente substituir a rotina ativa).

## Cálculo de frequência e confiança

NECESSÁRIO PARA IMPLEMENTAÇÃO / A DEFINIR: fórmula exata de confiança (ex.: proporção de ocorrências no período predominante sobre o total da janela). O exemplo do histórico usa uma frequência de 82% associada a "rotina aprendida" e uma confiança de mudança de 76% — DECIDIDO como exemplo ilustrativo do formato de dado, não como limiar oficial.

DECIDIDO com Jams em 2026-09-07 (ver `DOCUMENTATION_AUDIT.md`): 80% de frequência na janela histórica como limiar para promover de "candidate" a "active", e 70% de confiança na janela recente para sinalizar "mudança possível" ao TEYO (para ele poder comentar proativamente). Implementado em `pattern_engine/task_time_of_day.py`. Número mínimo de ocorrências antes de qualquer padrão ser considerado (3, para nunca promover a partir de 1-2 eventos — `BUSINESS_RULES.md` #3) não fazia parte do que precisava de aprovação; decidido tecnicamente na implementação.

## Promoção e rebaixamento de padrão

- Promoção: candidate → active quando a frequência na janela histórica ultrapassa o limiar de confiança (A DEFINIR valor) de forma sustentada.
- Rebaixamento/remoção: quando a janela recente diverge de forma sustentada do padrão ativo (não por uma única exceção), o padrão é marcado como `deprecated`, e um novo `candidate` pode começar a ser observado.
- DECIDIDO: o TEYO não deve alterar automaticamente uma preferência consolidada — ele pode comentar a mudança percebida e perguntar se deve passar a considerar o novo horário (ver exemplo de diálogo em `MODULES/TEYO` / `LLM.md`), mas a promoção definitiva de rotina segue as regras do sistema, não uma inferência livre do LLM.

## Como os dados chegam ao LLM (DECIDIDO — formato conceitual do histórico)

O LLM recebe um resumo estruturado, não os dados brutos. Exemplo de formato:

```
Padrão: tarefas domésticas
Período predominante: noite
Frequência: 82%
Status: rotina aprendida
Mudança recente: sim
Confiança da mudança: 76%
```

O LLM interpreta esse resumo para conversar com o usuário; ele não recalcula os números.

## Uso pelo Planejador

Ver `PLANNER.md` — os horários de maior produtividade e os padrões ativos alimentam a sugestão de plano do dia, mas nunca de forma obrigatória (o sistema sugere, não impõe).
