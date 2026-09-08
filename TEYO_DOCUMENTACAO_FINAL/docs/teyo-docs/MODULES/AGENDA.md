# MODULES/AGENDA.md — Agenda

1. **Objetivo**: gerenciar compromissos, horários e datas do usuário.
2. **Funcionalidades**: criar/editar/excluir compromisso, visualizar conflitos, integrar com planejamento.
3. **Telas**: tela de Agenda (calendário/lista de compromissos).
4. **Componentes**: item de compromisso (título, início, fim).
5. **Dados**: `events` (ver `DATABASE.md`).
6. **Ações**: `create_event`, `update_event`, `delete_event` (ver `TOOLS.md`).
7. **Regras de negócio**: exclusão exige confirmação; conflito de horário sinalizado ao usuário antes de confirmar criação — DECIDIDO com Jams na FASE 8 (ver `PLANNER.md`, `TOOLS.md`, `ACCEPTANCE_CRITERIA.md`): nunca bloqueia silenciosamente nem cria por conta própria; só cria/altera mesmo com sobreposição depois de confirmação explícita (`confirm_overlap`).
8. **Interação com TEYO**: DECIDIDO — exemplo "amanhã tenho reunião às duas" deve ser interpretado pelo Orquestrador e virar um `create_event` com data/hora estruturadas.
9. **Interação com outros módulos**: alimenta o Planejador (Plano do Dia).
10. **V1**: CRUD de compromissos + criação por linguagem natural + integração com plano do dia.
11. **Depois**: sincronização com calendários externos (Google Calendar, etc.) — não mencionada no histórico, FORA DO V1.
