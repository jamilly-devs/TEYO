# NAVIGATION.md

## Estrutura V1

- **Home**: dashboard e ponto de entrada.
- **Conversa TEYO**: uma única conversa principal, acessível pela Home.
- **Módulos V1 com tela própria** (FASE 10): Tarefas, **Hábitos**, Objetivos, **Carreira**, Finanças, Mercado e Agenda.
- **Estudos e Casa** (DECIDIDO na FASE 10): **visões filtradas de Tarefas** por categoria (`studies` / `house`) — têm rota e atalho, mas não são telas/CRUD próprios.
- **Pomodoro**: experiência de timer associada a uma tarefa (`pomodoro_enabled`); **sem item de menu** e sem tool de LLM.
- **Gamificação/Mascote**: componentes transversais da experiência, não módulos equivalentes aos módulos de negócio.

## Hierarquia da Home

1. Conversa com TEYO
2. Progresso
3. Tarefas/plano do dia
4. Agenda e demais blocos gerais

A referência a Notícias em versões anteriores da descrição da Home não autoriza a implementação do módulo Notícias na V1, pois Notícias é V2+.

## Fora da navegação V1

Notícias e Relatórios não devem receber telas, blocos, rotas ou endpoints funcionais como parte da entrega V1.
