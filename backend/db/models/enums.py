import enum
from typing import Type


def enum_values(enum_cls: Type[enum.Enum]) -> list[str]:
    """`values_callable` for `sa.Enum`: store/compare on `.value`, not `.name`."""
    return [member.value for member in enum_cls]


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCategory(str, enum.Enum):
    GENERAL = "general"
    STUDIES = "studies"
    HOUSE = "house"


class EventSource(str, enum.Enum):
    MANUAL = "manual"
    TEYO_NLU = "teyo_nlu"


class MarketItemStatus(str, enum.Enum):
    ACTIVE = "active"
    PURCHASED = "purchased"


class FinancialRecordType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class PatternStatus(str, enum.Enum):
    CANDIDATE = "candidate"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class MemoryCategory(str, enum.Enum):
    PREFERENCE = "preference"
    FACT = "fact"
    DECISION = "decision"


class MemorySource(str, enum.Enum):
    USER_STATED = "user_stated"
    SYSTEM_INFERRED = "system_inferred"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class PomodoroStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class JobApplicationStatus(str, enum.Enum):
    """Fluxo simples de candidatura (MODULES/CAREER.md, FASE 10). Valores em
    inglês minúsculo, no mesmo padrão de GoalStatus/TaskStatus; os rótulos
    em português ficam no frontend."""

    INTERESTED = "interested"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
