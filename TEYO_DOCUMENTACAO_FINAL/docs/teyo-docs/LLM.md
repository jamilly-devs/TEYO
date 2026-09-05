# LLM.md

## Modelo (DECIDIDO)

LLM local: **Qwen3.5-4B**. Não usar Claude API, OpenAI API, Gemini API ou qualquer API paga de LLM em produção. Claude/Claude Code é usado apenas para desenvolver o TEYO, não como cérebro remoto em produção.

## Camada de abstração (DECIDIDO)

```mermaid
flowchart LR
    ORQ[Orquestrador] --> ADAPTER[LLM Provider / Adapter]
    ADAPTER --> QWEN[Qwen3.5-4B local]
```

O Orquestrador nunca chama o runtime do modelo diretamente. Ele chama uma interface fixa do Adapter, por exemplo (contrato ilustrativo, não implementação):

```
LLMProvider.generate(
  system_prompt: str,
  context: Context,
  available_tools: list[ToolSpec],
  conversation: list[Message]
) -> LLMResponse  # texto e/ou tool_calls
```

Trocar de modelo no futuro significa escrever um novo Adapter que implementa essa mesma interface, sem alterar Orquestrador, Tools ou banco.

## Runtime de hospedagem

A DEFINIR — OPÇÃO RECOMENDADA: servir o Qwen3.5-4B via um runtime local com suporte a tool calling / structured output (ex.: llama.cpp com servidor HTTP local, ou Ollama). Decisão final pendente de confirmação por Jams antes da FASE 4 do roadmap.

## O que é enviado como contexto ao LLM (DECIDIDO no nível conceitual)

- System prompt do TEYO (ver `PROMPT` abaixo).
- Memória relevante recuperada pelo sistema (não toda a memória — ver `MEMORY.md`).
- Padrões relevantes recuperados pelo Motor de Padrões (não todos — ver `PATTERN_ENGINE.md`).
- Preferências do usuário.
- Lista de tools disponíveis no momento (pode variar por tela/contexto — A DEFINIR quais tools ficam sempre disponíveis vs. contextuais).
- Histórico recente da conversa (janela — tamanho A DEFINIR).

## Structured output / tool calling

NECESSÁRIO PARA IMPLEMENTAÇÃO: o Adapter deve normalizar a saída do modelo para um formato único de tool call (nome + argumentos tipados), independente de como o Qwen3.5-4B formata nativamente sua saída. Se a saída não for um JSON válido conforme o contrato da tool, o Adapter trata como erro (ver `ERROR_HANDLING.md`), nunca tenta "adivinhar" o argumento faltante.

## Limites

A DEFINIR: tamanho de contexto efetivo, quantização do modelo, tempo máximo de resposta aceitável, comportamento sob concorrência (mais de uma requisição simultânea). Precisam ser confirmados com base em benchmark real do hardware disponível.

## Fallback

DECIDIDO (regra de produto): se o LLM estiver indisponível ou a resposta for inválida, o TEYO não deve fingir que executou uma ação. Ver comportamento detalhado em `ERROR_HANDLING.md`.

## System Prompt do TEYO (especificação de comportamento)

O system prompt deve instruir o modelo a:

1. Manter personalidade de "amigão": informal, tranquilo, sem tom corporativo, respostas curtas quando possível (ver `MASCOT.md`/tom em `MODULES/HOME.md` não aplica — tom fica centralizado aqui).
2. Nunca afirmar que executou uma ação sem ter recebido confirmação de sucesso de uma tool.
3. Nunca inventar dados (números, datas, tarefas) que não vieram do sistema.
4. Sempre que uma ação for destrutiva ou ambígua, pedir confirmação antes de chamar a tool (ver `BUSINESS_RULES.md`).
5. Usar apenas as tools da lista fornecida, com os parâmetros exigidos.
6. Quando não houver informação suficiente para executar uma ação, perguntar ao usuário em vez de assumir um valor.
7. Reconhecer quando o pedido do usuário não exige nenhuma tool (conversa livre) e responder diretamente.

NECESSÁRIO PARA IMPLEMENTAÇÃO: o texto literal final do system prompt (string exata) é responsabilidade do Claude Code na FASE 4, seguindo estritamente as regras acima e as regras de `BUSINESS_RULES.md`.
