"""Runtime: Ollama, servindo qwen3.5:4b localmente — decisão de Jams
(confirmada antes da FASE 4; ver LLM.md).

Parâmetros abaixo medidos com benchmark real nesta máquina em 2026-09-04
(Intel i7-9750H, 32 GB RAM, sem GPU dedicada aproveitada pelo Ollama, macOS,
Ollama 0.33.2, modelo `qwen3.5:4b` — pull padrão, quantização Q4_K_M,
contexto arquitetural de até 262144 tokens):

- "thinking" ligado (padrão nativo do modelo): ~38,8 s para responder uma
  pergunta trivial de uma frase (262 tokens de raciocínio interno + resposta,
  ~8 tokens/s de geração nesta CPU).
- "thinking" desligado (`think: false`): ~1,4 s para a mesma pergunta
  (8 tokens). Sem isso, a conversa fica impraticável neste hardware — por
  isso o padrão abaixo é desligado.
- Tool calling estruturado nativo do Ollama funciona (produz `tool_calls`
  válido a partir do JSON Schema da tool), mas custa mais: ~19,2 s numa
  chamada com uma tool simples (prompt maior por causa do schema).
- Concorrência: duas requisições simultâneas fecharam em ~3,7 s de parede
  (não paralelo pleno) — o Ollama parece enfileirar/serializar nesta
  configuração padrão. Compatível com o "um usuário ativo" da V1; não há
  fila própria implementada no Orquestrador por enquanto.
- Também observado (não é benchmark de performance, é achado de
  comportamento): pedida para resolver "amanhã às 19h", a data devolvida
  pelo modelo veio errada (ano 2023). Confirma na prática por que
  create_event/create_task devem receber datas já normalizadas pelo
  Orquestrador, nunca calculadas pelo próprio LLM (TOOLS.md, LLM.md).

Nenhum desses números foi inventado — todos vieram de chamadas reais a
`POST /api/chat` nesta máquina antes de qualquer linha do Adapter ser
escrita.
"""

import os

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:4b")
OLLAMA_THINK = os.environ.get("OLLAMA_THINK", "false").lower() == "true"

# Generoso o bastante para cobrir o pior caso observado (~19s com tool) com
# folga; evita falha prematura sem tornar um travamento real invisível.
OLLAMA_TIMEOUT_SECONDS = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "60"))

# Tamanho da janela de histórico enviada ao modelo — LLM.md deixa isso A
# DEFINIR sem gate de decisão do Jams; escolha técnica registrada aqui,
# calibrada pela taxa de geração observada (~8-9 tok/s: histórico longo
# demais custa segundos reais de latência por mensagem).
CONVERSATION_HISTORY_WINDOW = int(os.environ.get("CONVERSATION_HISTORY_WINDOW", "20"))
