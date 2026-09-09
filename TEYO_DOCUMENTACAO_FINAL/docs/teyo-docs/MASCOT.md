# MASCOT.md

## Identidade (DECIDIDO)

O mascote se chama TEYO — mesma identidade textual/conversacional do assistente. A grafia oficial é sempre "TEYO" (não usar "Teyo", "TEO", "Teo").

## Comportamento (DECIDIDO)

- Reage a acontecimentos do usuário (ex.: conclui muitas tarefas → expressão feliz/orgulhosa; usuário cansado → expressão acolhedora; conquista alcançada → comemoração).
- Possui expressões diferentes, controladas pelo sistema, não pelo usuário.
- Evolui visualmente conforme progresso do usuário (níveis/gamificação).

## Personalização (DECIDIDO)

Permitido: alterar a cor do TEYO.

Não permitido: escolher/personalizar expressões, adicionar acessórios livremente (fones, bonés, óculos), criar combinações, criar tipos diferentes de TEYO.

## Evolução (DECIDIDO — DECISÃO C, híbrida; estágios definidos na FASE 9)

Evolução pré-definida pelo sistema, não escolhida pelo usuário. **DECISÃO C (Jams):**

- O **nível do usuário** determina a evolução **estrutural/principal** do mascote.
- **Conquistas não substituem** o sistema de níveis; desbloqueiam **elementos complementares** (detalhes visuais, itens/acessórios, expressões extras).

**Estágios V1** (`backend/mascot/catalog.py` — `stage_for_level`, configurável):

| Estágio | Nível | Referência conceitual |
|---|---|---|
| 1 | 1–2 | nível inicial |
| 2 | 3–5 | cresce um pouco |
| 3 | 6–9 | roupa nova |
| 4 | 10–14 | evolui |
| 5 | 15+ | coroa |

**Elementos por conquista** (`catalog.ACHIEVEMENT_FEATURE`, extensível): cada conquista mapeia para uma `feature` (ex.: `streak_7 → item_scarf`, `streak_30 → item_crown`, `pomodoro_10 → item_headphones`). `GET /mascot/state` devolve `unlocked_features` derivado das conquistas do usuário — não é coluna nova em `mascot_state`.

## Expressões (catálogo V1 — FASE 9)

Determinadas pelo sistema, via os hooks de domínio da FASE 8 (`backend/mascot/subscribers.py` → `backend/mascot/engine.py`). Catálogo em `backend/mascot/catalog.py`, extensível:

| Expressão | Gatilho |
|---|---|
| `idle` | repouso; também o estado para o qual a expressão volta após `EXPRESSION_TTL_MIN` (90 min) sem novo evento — não é persistido, é resolvido na leitura |
| `happy` | tarefa concluída (comum) |
| `proud` | tarefa de maior esforço concluída; subida de nível (`level_up`) |
| `celebrating` | conquista desbloqueada (`achievement_unlocked`) |
| `caring` | usuário relatou baixa energia (`on_low_energy_reported`, disparado por `reorganize_day`) |
| `tired` | reservado (sem gatilho automático no V1) |

Limitação V1 (registrada em `DOCUMENTATION_AUDIT.md`): "último evento vence" — se uma conclusão de tarefa também sobe de nível na mesma transação, a expressão final pode ficar `happy` em vez de `proud`; o TTL traz de volta a `idle`.

## Relação com a personalidade textual (DECIDIDO)

O mascote deve parecer parte do TEYO, não um elemento visual separado — a expressão visual e o tom da mensagem de texto devem combinar (ex.: mascote com expressão de orgulho junto de uma mensagem como "Você mandou bem hoje.").

## Animações — risco técnico (DECIDIDO como requisito + regra de tratamento de risco)

As animações do mascote devem ser implementadas pelo Claude Code; o dono do produto não sabe criar animações manualmente. Se uma animação específica não for tecnicamente viável na stack escolhida, o Claude Code deve:
1. Identificar e registrar o problema explicitamente (não simplificar o mascote silenciosamente).
2. Propor uma alternativa técnica viável.

RISCO TÉCNICO IDENTIFICADO: a viabilidade de animações ricas (transições suaves entre expressões, evolução animada) depende da stack de frontend ainda A DEFINIR (`ARCHITECTURE.md`). Este é um risco a ser resolvido na FASE 3/FASE 8 do roadmap, não antes.

### Resolução na FASE 9

Stack real do frontend: React 19 + Vite, **sem** biblioteca de animação. Solução V1 (`frontend/src/components/Mascot.tsx` + `src/index.css`): **SVG inline + CSS puro** (`@keyframes`, `transition`), sem introduzir dependência pesada.

- **Repouso**: leve "bob" vertical em loop (`@keyframes mascot-bob`).
- **Comemoração**: pulso de escala curto sobre o bob.
- **Baixa energia**: leve inclinação.
- **`prefers-reduced-motion: reduce`**: todas as animações desligadas (troca instantânea).

**Limitação V1 registrada** (`DOCUMENTATION_AUDIT.md`): a troca de expressão é instantânea (novos olhos/boca), **sem morph/tween** entre estados; a mudança de estágio é scale+fade, sem transição morfológica; a comemoração é um pulso CSS, sem partículas. Assets visuais finais não foram entregues (`UX.md`) — o SVG atual é de trabalho, trocável sem mexer na lógica de estado (que está no backend).
