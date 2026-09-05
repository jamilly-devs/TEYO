# CLAUDE_CODE_INSTRUCTIONS.md

Este documento é dirigido especificamente a você, Claude Code, ao receber a instrução "Construa o TEYO V1 seguindo a documentação".

## Ordem de leitura

1. `CLAUDE_CODE_CONTEXT.md`
2. `PRODUCT.md`
3. `V1_SCOPE.md`
4. `ARCHITECTURE.md`
5. `DATABASE.md`, `API.md`, `LLM.md`, `TOOLS.md`, `MEMORY.md`, `PATTERN_ENGINE.md`, `PLANNER.md`
6. `BUSINESS_RULES.md`
7. `UX.md`, `NAVIGATION.md`, `MASCOT.md`, `GAMIFICATION.md`
8. Cada arquivo em `MODULES/` correspondente ao módulo que você for implementar naquele momento
9. `FLOWS.md`, `ERROR_HANDLING.md`
10. `TESTING.md`, `ACCEPTANCE_CRITERIA.md`
11. `ROADMAP.md`, `DEFINITION_OF_DONE.md`
12. `DOCUMENTATION_AUDIT.md` (pendências conhecidas)

## Regras que nunca podem ser violadas

- O LLM nunca acessa banco, calcula números, decide regras de negócio ou executa ação sem passar por uma tool (`ARCHITECTURE.md`).
- Nenhum item listado como "NÃO INCLUI NO V1" ou "FORA DO V1" é implementado, mesmo que pareça simples.
- Nenhum item "A DEFINIR" vira decisão definitiva sem registrar a pendência e a OPÇÃO RECOMENDADA usada.
- Módulo de pets nunca é criado, sob nenhuma justificativa.
- O mascote nunca recebe personalização além de cor.
- Toda ação destrutiva exige confirmação do usuário antes da execução.
- O sistema nunca afirma ter executado uma ação sem confirmação de sucesso da tool.

## Decisões congeladas (não reabrir sem pedido explícito de Jams)

- LLM local: Qwen3.5-4B, via camada de abstração (Adapter).
- Nome e grafia do produto/mascote: TEYO.
- Uma única conversa principal (sem chats separados).
- Hierarquia da Home: conversa com TEYO → progresso → tarefas/plano do dia → resto.
- Personalização do mascote: apenas cor.
- Sem módulo de pets.
- Sem dependência de API paga de LLM em produção.
- V1 começa com um usuário ativo; o modelo de dados e o isolamento por `user_id` são preparados para multiusuário desde a V1. A experiência completa multiusuário fica fora da V1.

## Como lidar com "A DEFINIR"

Ao encontrar um item "A DEFINIR" que bloqueia uma implementação:
1. Procure se o documento correspondente já traz uma "OPÇÃO RECOMENDADA".
2. Se sim, você pode usá-la como implementação provisória, mas deve registrar isso explicitamente (ex.: comentário no código apontando para o documento e a seção, e uma entrada no changelog/pendências do projeto).
3. Se não houver OPÇÃO RECOMENDADA, pare e pergunte a Jams antes de inventar um valor.
4. Nunca escolha silenciosamente entre duas interpretações possíveis de uma regra ambígua.

## Como implementar incrementalmente

Siga a ordem de `ROADMAP.md`. Ao final de cada FASE, rode os testes relevantes de `TESTING.md` antes de avançar para a próxima fase.

## Como testar cada etapa

Cada FASE do roadmap tem documentos e critérios correspondentes em `TESTING.md` e `ACCEPTANCE_CRITERIA.md`. Nenhuma FASE é considerada concluída sem os testes da camada correspondente passando.

## Como evitar regressões

Toda regra de `BUSINESS_RULES.md` deve ter um teste automatizado que falha se a regra for violada. Ao alterar código de uma FASE anterior, rode os testes dessa fase antes de prosseguir.

## Como saber se uma funcionalidade já está pronta

Uma funcionalidade está pronta quando atende ao critério correspondente em `ACCEPTANCE_CRITERIA.md`, não quando "parece funcionar" na interface.

## Como registrar decisões novas

Se, durante a implementação, uma decisão nova for tomada (inclusive resolução de um "A DEFINIR"), registre-a como uma entrada datada em `DOCUMENTATION_AUDIT.md`, citando o documento e a seção afetados, para manter a documentação como fonte da verdade atualizada.

## Como não sair do escopo V1

Antes de implementar qualquer funcionalidade não descrita explicitamente nesta documentação, verifique `V1_SCOPE.md`. Se não estiver em "INCLUI NO V1", não implemente — mesmo que pareça uma melhoria óbvia.
