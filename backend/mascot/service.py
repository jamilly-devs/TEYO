"""Leitura/escrita do estado do mascote para a API.

`get_state` = `engine.resolve_state`. `set_color` é a única
personalização permitida ao usuário (`BUSINESS_RULES.md` #10,
`ACCEPTANCE_CRITERIA.md`). A validação de formato também está no schema
Pydantic da API (retorno 422); aqui fica a rede de segurança para
qualquer outro chamador.
"""

import re
from typing import Any

from sqlalchemy.orm import Session

from mascot import engine

_HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def _validate_color(color: str) -> str:
    if not isinstance(color, str) or not _HEX_COLOR.match(color.strip()):
        raise ValueError("cor inválida: use um hex como '#7C5CFF' ou '#abc'.")
    return color.strip()


def get_state(db: Session, user_id: int) -> dict[str, Any]:
    return engine.resolve_state(db, user_id)


def set_color(db: Session, user_id: int, color: str) -> dict[str, Any]:
    return engine.set_color(db, user_id, _validate_color(color))
