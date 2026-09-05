# MODULES/HOME.md — Home

1. **Objetivo**: dashboard geral e ponto de entrada do usuário no TEYO.
2. **Funcionalidades**: saudação, visão rápida do dia, agenda, plano do dia, caixa de conversa com TEYO, blocos dos módulos V1 e progresso.
3. **Telas**: uma única tela Home.
4. **Componentes**: bloco de saudação; resumo do dia; lista/preview da agenda; preview do plano do dia; campo de entrada de conversa; blocos de módulo (ex.: bloco "Finanças"); indicador de progresso/dashboard de atividade.
5. **Dados**: agrega dados de vários módulos (não tem tabela própria além de eventuais preferências de layout, A DEFINIR).
6. **Ações**: nenhuma ação exclusiva; a Home aciona ações dos módulos e da conversa.
7. **Regras de negócio**: hierarquia obrigatória de prioridade — DECIDIDO (doc. 3, item 5): 1) conversa com TEYO, 2) progresso, 3) tarefas/plano do dia; demais blocos (agenda, notícias, blocos gerais) ficam abaixo dessa prioridade visual.
8. **Interação com TEYO**: a caixa de conversa da Home é a mesma conversa principal (ao abrir totalmente, vai para a tela de conversa do TEYO); não é um chat separado.
9. **Interação com outros módulos**: exibe atalhos/resumos dos módulos de negócio incluídos na V1 em `V1_SCOPE.md`.
10. **V1**: dashboard com a hierarquia decidida.
11. **Depois**: personalização de layout da Home pelo usuário — não mencionada no histórico, A DEFINIR/FORA DO V1.

## Dashboard de atividade (DECIDIDO, doc. 3, item 6)

Deve mostrar: dias mantendo a rotina, porcentagem de atividades realizadas, tarefas concluídas, progresso geral — combinando dados de tarefas de casa, carreira/vagas, estudos, hábitos, objetivos e outras atividades cadastradas. Os números vêm do sistema (Relatórios), nunca são estimados pelo LLM.
