# PRODUCT.md — Visão de Produto do TEYO

## O que é o TEYO

TEYO é um sistema pessoal conversacional para organizar a vida de um usuário (inicialmente Jams): tarefas, hábitos, objetivos, estudos, carreira, finanças, mercado, casa e agenda, com Pomodoro opcional, gamificação e mascote. O ponto de entrada principal é uma conversa com um assistente com personalidade própria, também chamado TEYO, representado por um mascote.

DECIDIDO: TEYO não é um gerenciador de tarefas comum. É um "amigão pessoal" conversacional que também tem telas dedicadas para módulos com complexidade própria.

## O que o TEYO NÃO é

- Não é um chatbot genérico. Ele opera sobre dados estruturados do usuário através de tools.
- Não tem dois chats separados (um "simples" e um "avançado"). Existe uma única conversa principal.
- Não depende de API paga de LLM em produção (DECIDIDO).
- Não personaliza o mascote livremente (DECIDIDO — ver `MASCOT.md`).

## Usuário do V1

DECIDIDO: V1 começa com um único usuário ativo, mas a arquitetura e o modelo de dados já devem ser preparados para multiusuário. Cada dado de usuário deve ser isolado por `user_id`. A experiência completa de múltiplas contas, convites e administração fica fora da V1.

FORA DO V1: experiência multiusuário completa (convites, permissões granulares, telas de gestão de usuários).

## Princípios de produto (DECIDIDO)

1. O LLM interpreta e conversa; o sistema TEYO calcula, guarda e decide regras de negócio.
2. Nenhuma mudança de rotina é assumida a partir de um único evento isolado.
3. O usuário nunca perde controle sobre ações destrutivas (exclusões, alterações relevantes exigem confirmação — ver `BUSINESS_RULES.md`).
4. A personalidade do TEYO é consistente em qualquer parte do produto onde ele fale com o usuário.
5. Cálculos e números apresentados ao usuário vêm do sistema, nunca são inventados pelo LLM.

## Inspiração de experiência

DECIDIDO: inspiração é a sensação de progresso e feedback do Duolingo (não o visual, o efeito de "dá vontade de abrir o app").

## Fora do V1 (produto, nível alto)

- Módulo Notícias.
- Módulo Relatórios como módulo de produto independente.
- Experiência multiusuário completa.
- Apps nativos (V1 é web/PWA).
- Qualquer dependência de LLM pago em produção.
