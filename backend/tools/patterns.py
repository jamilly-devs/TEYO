"""Tools de Padrões (PATTERN_ENGINE.md, TOOLS.md).

Só tools de leitura — o LLM nunca decide nem escreve um padrão
(ARCHITECTURE.md, PATTERN_ENGINE.md: "a promoção definitiva de rotina
segue as regras do sistema, não uma inferência livre do LLM")."""

from typing import Any

from sqlalchemy.orm import Session

from db.models.enums import PatternStatus
from db.models.pattern import Pattern
from llm.base import ToolSpec
from pattern_engine.task_time_of_day import ComputedPattern, refresh_patterns_for_user
from tools.base import ToolDefinition


def _serialize(row: Pattern, computed: ComputedPattern) -> dict[str, Any]:
    return {
        "pattern_type": row.pattern_type,
        "category": computed.category,
        "description": row.description,
        "predominant_period": computed.historical_predominant_period,
        "frequency": round(computed.historical_frequency, 2),
        "status": row.status.value,
        "evidence_count": row.evidence_count,
        "recent_change": computed.recent_change,
        "recent_change_confidence": (
            round(computed.recent_frequency, 2) if computed.recent_change else None
        ),
    }


def get_patterns(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    pattern_type = arguments.get("pattern_type")
    pairs = refresh_patterns_for_user(db, user_id)

    items = []
    # Um padrão que estava seria `active` pela janela histórica, mas cuja
    # janela recente diverge de forma sustentada, é despromovido para
    # `deprecated` na mesma computação (task_time_of_day.py) — por isso
    # `items` pode vir vazio justo no momento em que há mais a dizer sobre
    # a categoria. `routine_changes_detected` existe para que esse `items`
    # vazio nunca seja lido como "não há padrão/mudança" (auditoria FASE 7):
    # sinaliza explicitamente que get_routine_changes tem informação
    # relevante, sem duplicar aqui o que aquela tool já retorna em detalhe.
    routine_changes_detected = False
    for row, computed in pairs:
        if pattern_type is not None and not row.pattern_type.startswith(pattern_type):
            continue
        if computed.recent_change:
            routine_changes_detected = True
        if row.status == PatternStatus.ACTIVE:
            items.append(_serialize(row, computed))
        elif row.status == PatternStatus.CANDIDATE and pattern_type is not None:
            items.append(_serialize(row, computed))
        # deprecated nunca é retornado por get_patterns (TOOLS.md).
    return {"items": items, "routine_changes_detected": routine_changes_detected}


def get_routine_changes(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    pairs = refresh_patterns_for_user(db, user_id)
    items = [_serialize(row, computed) for row, computed in pairs if computed.recent_change]
    return {"items": items}


def select_relevant_patterns(db: Session, user_id: int) -> list[str]:
    """Chamada pelo Orquestrador a cada turno (não é uma tool, o LLM nunca
    a chama diretamente) para preencher `Context.patterns` — padrões
    ativos moldam o comportamento do TEYO de forma consistente (mesmo
    raciocínio de `tools/memory.py:select_relevant_context` para
    preferências); mudanças recentes entram também, para permitir o
    comentário proativo de `FLOWS.md` item 7."""
    pairs = refresh_patterns_for_user(db, user_id)
    lines: list[str] = []
    for row, computed in pairs:
        if row.status == PatternStatus.ACTIVE:
            lines.append(row.description)
        if computed.recent_change:
            lines.append(
                f"Possível mudança de rotina em '{computed.category}': tendência "
                f"recente para {computed.recent_predominant_period} "
                f"(confiança {computed.recent_frequency:.0%}), diferente do "
                f"padrão de {computed.historical_predominant_period}."
            )
    return lines


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="get_patterns",
            description=(
                "Consulta os padrões de rotina ATUAIS já confirmados pelo "
                "sistema (ex.: horário em que o usuário costuma concluir "
                "tarefas de uma categoria). Retorna só padrões confirmados "
                "(`active`) por padrão; passe pattern_type para também ver "
                "candidatos ainda em observação daquele tipo específico. Os "
                "números vêm todos do sistema — nunca invente um padrão que "
                "não veio daqui. `items` vazio NÃO significa que não existe "
                "padrão nem mudança de rotina — um padrão pode ter acabado "
                "de ser despromovido justamente por causa de uma mudança "
                "recente; nesse caso `routine_changes_detected` vem `true`. "
                "Para perguntas sobre MUDANÇA de rotina, use get_routine_changes "
                "em vez desta, ou além dela."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "pattern_type": {
                        "type": "string",
                        "description": (
                            "Filtra por tipo, ex.: 'task_time_of_day' (todas "
                            "as categorias) ou 'task_time_of_day:studies' "
                            "(uma categoria específica)."
                        ),
                    },
                },
            },
        ),
        execute=get_patterns,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="get_routine_changes",
            description=(
                "Consulta mudanças de rotina detectadas recentemente, com "
                "confiança suficiente para você comentar proativamente "
                "(ex.: 'percebi que ultimamente você tem...'). É a tool certa "
                "para qualquer pergunta sobre MUDANÇA de rotina (ex.: "
                "'percebeu alguma mudança em mim?', 'eu mudei de horário?') "
                "— use-a mesmo que get_patterns tenha vindo vazio ou só com "
                "padrões antigos. Não aplica nenhuma mudança sozinho — é só "
                "informação para conversar."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=get_routine_changes,
    ),
]
