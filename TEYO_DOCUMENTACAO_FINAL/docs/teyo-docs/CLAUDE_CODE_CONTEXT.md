# CLAUDE_CODE_CONTEXT.md

## Contexto obrigatório do TEYO V1

TEYO é um assistente pessoal conversacional, não um gerenciador de tarefas comum. Existe uma única conversa principal. A personalidade é amigável, tranquila, natural, pouco formal, não invasiva e não julgadora.

### Decisões congeladas

- V1: Web/PWA. Apps nativos ficam para o futuro.
- LLM V1: Qwen3.5-4B local, via LLM Adapter. Decisão fechada.
- V1: Tarefas, Hábitos, Objetivos, Estudos, Carreira, Finanças, Mercado, Casa, Agenda e Pomodoro.
- V2+: Notícias e Relatórios. Não implementar esses módulos na V1.
- Home: 1) conversa, 2) progresso, 3) tarefas/plano do dia, 4) agenda e demais blocos gerais. A menção histórica a Notícias na Home não libera o módulo Notícias para V1.
- Pomodoro é opcional em qualquer tarefa; nunca obrigatório.
- Mascote: usuário personaliza somente a cor. Expressões são controladas pelo sistema. Evolução ocorre por progresso/nível.
- Multiusuário: arquitetura/modelo de dados preparados desde V1 por `user_id`, mas experiência completa de múltiplos usuários fica fora da V1.
- Pets não fazem parte do produto.

### Arquitetura

Usuário → Interface → Orquestrador → LLM local → Tools → Sistema/Banco/Motor de Padrões → Orquestrador → LLM → Usuário. O LLM não acessa banco diretamente, não executa ações sem tools, não calcula números de negócio e não decide regras.

### Regra de precedência

Documentação marcada como DECIDIDO prevalece sobre recomendações. Pendências não podem ser resolvidas silenciosamente. Se surgir uma lacuna não documentada, parar e reportar antes de inventar.
