import re
from typing import Optional

from pydantic import BaseModel, field_validator

_HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


class MascotStateOut(BaseModel):
    evolution_stage: int
    current_expression: str
    color: str
    unlocked_features: list[str]
    updated_at: Optional[str]


class MascotColorUpdate(BaseModel):
    color: str

    @field_validator("color")
    @classmethod
    def _hex(cls, value: str) -> str:
        value = value.strip()
        if not _HEX_COLOR.match(value):
            raise ValueError("cor inválida: use um hex como '#7C5CFF' ou '#abc'.")
        return value
