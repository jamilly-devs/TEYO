"""Tool só-leitura de gamificação (TOOLS.md, FASE 9).

O LLM nunca calcula nem concede XP (`ARCHITECTURE.md`,
`BUSINESS_RULES.md` #6/#7). Esta tool devolve o estado já calculado pelo
sistema para o TEYO comentar nível/streak/conquistas com números reais
(`GAMIFICATION.md`: "o número/XP em si vem do sistema via tool")."""

from typing import Any

from sqlalchemy.orm import Session

from gamification.service import get_state
from llm.base import ToolSpec
from tools.base import ToolDefinition


def get_gamification_state(
    db: Session, user_id: int, arguments: dict[str, Any]
) -> dict[str, Any]:
    return get_state(db, user_id)


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="get_gamification_state",
            description=(
                "Consulta o progresso de gamificação do usuário, já "
                "calculado pelo sistema: nível, XP total, XP acumulado "
                "dentro do nível atual e quanto o nível exige, streak (dias "
                "seguidos com atividade) e conquistas desbloqueadas. Use "
                "quando o usuário perguntar sobre nível/XP/streak/conquistas, "
                "ou quando for comentar uma evolução na conversa. NUNCA "
                "estime nem calcule esses números por conta própria — eles "
                "vêm só daqui."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=get_gamification_state,
    ),
]
