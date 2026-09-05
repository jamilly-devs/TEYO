# V1_SCOPE.md

## INCLUI NO V1

- Conversa principal com TEYO (uma única conversa, sem chats separados).
- Módulos: Tarefas, Hábitos, Objetivos, Estudos, Carreira, Finanças, Mercado, Casa, Agenda e Pomodoro.
- Gamificação e Mascote como sistemas transversais da experiência V1.
- Home com hierarquia: 1) conversa com TEYO, 2) progresso, 3) tarefas/plano do dia, depois agenda e demais blocos gerais.
- LLM local: Qwen3.5-4B, via camada de abstração (LLM Provider/Adapter). Esta é decisão fechada para a V1.
- Motor de Padrões, com valores numéricos ainda pendentes.
- Planejamento diário com reorganização sob comando do usuário.
- Tool calling para ações que alteram dados.
- Modelo de dados preparado para multiusuário desde a V1: dados de usuário isolados por `user_id`, mesmo com apenas um usuário ativo inicialmente. A experiência completa de multiusuário não faz parte da V1.
- Mascote com expressões reativas controladas pelo sistema, evolução por progresso/nível e cor customizável pelo usuário.

## NÃO INCLUI NO V1 (FORA DO V1)

- Módulo Notícias.
- Módulo Relatórios como módulo de produto independente.
- Módulo de pets (DECIDIDO — removido explicitamente).
- Experiência multiusuário completa (convites, permissões granulares, administração de contas e fluxos completos de compartilhamento).
- Personalização de mascote além de cor (expressões, acessórios, skins alternativas).
- Apps nativos iOS/Android (V1 é Web/PWA).
- Qualquer integração com API paga de LLM em produção.

## A DEFINIR

- Stack específica de frontend/backend/banco.
- Runtime exato de produção/hospedagem do Qwen3.5-4B.
- Valores numéricos do Motor de Padrões.
- Mecanismo concreto de busca de vagas em Carreira.
- Regras exatas de XP, níveis e conquistas.
- Estágios exatos de evolução visual do mascote.
- Algoritmo de priorização do Planejador em conflitos.
- Regras de segurança/privacidade ainda não especificadas.
- Schemas e detalhes técnicos que não estejam definidos em `DATABASE.md`/documentos específicos.

## Regra para o Claude Code

Nenhum item de `NÃO INCLUI NO V1` deve ser implementado. Um item `A DEFINIR` não pode ser transformado silenciosamente em decisão. Se bloquear a implementação, o Claude Code deve parar e reportar a pendência antes de escolher por conta própria.
