# ROADMAP.md

Ordem recomendada de construção, considerando dependências reais (não é uma decisão de produto — é uma proposta técnica, NECESSÁRIO PARA IMPLEMENTAÇÃO, pode ser ajustada somente quando uma dependência técnica real for demonstrada e registrada; nenhuma alteração pode ampliar o escopo de produto).

## FASE 0 — Estrutura
Criar estrutura de pastas (`ARCHITECTURE.md`), configuração de projeto, CI básico.

## FASE 1 — Banco
Implementar schema completo de `DATABASE.md`, migrações, seeds mínimos para desenvolvimento.

## FASE 2 — Backend base
Implementar endpoints de `API.md` para os módulos mais simples (Tarefas, Agenda, Objetivos, Mercado, Finanças) sem ainda envolver o LLM — CRUD direto.

## FASE 3 — Frontend base
Implementar Home (`MODULES/HOME.md`) e telas dos módulos da FASE 2, com os estados de `UX.md`.

## FASE 4 — TEYO + LLM
Implementar LLM Adapter (`LLM.md`), Orquestrador, integração com Qwen3.5-4B, tela de conversa principal.

## FASE 5 — Tools
Implementar a camada de Tools (`TOOLS.md`) conectando Orquestrador aos endpoints da FASE 2.

## FASE 6 — Memória
Implementar `MEMORY.md`: `memory_entries`, recuperação de contexto relevante para o LLM.

## FASE 7 — Motor de Padrões
Implementar `PATTERN_ENGINE.md` sobre o histórico já existente das FASES 2–6.

## FASE 8 — Planejador
Implementar `PLANNER.md` (`get_daily_plan`, `reorganize_day`), consumindo padrões da FASE 7.

## FASE 9 — Gamificação e Mascote
Implementar `GAMIFICATION.md` e `MASCOT.md`, incluindo expressões reativas e evolução — após validação das OPÇÕES RECOMENDADAS pendentes com Jams.

## FASE 10 — Estudos, Carreira e Casa
Implementar os módulos V1 restantes que ainda não tenham sido construídos. Notícias e Relatórios NÃO entram nesta fase porque são V2+.

## FASE 11 — Testes e auditoria final
Executar `TESTING.md` e `ACCEPTANCE_CRITERIA.md` de ponta a ponta; revisar `DOCUMENTATION_AUDIT.md`.

## Regra entre fases
Nenhuma fase posterior deve ser iniciada com pendências de "A DEFINIR" que bloqueiem sua própria implementação sem antes registrar a pendência e propor a OPÇÃO RECOMENDADA correspondente (ver `CLAUDE_CODE_INSTRUCTIONS.md`).
