"""Erros da camada de Tools (TOOLS.md, ERROR_HANDLING.md).

Nenhum destes erros vira uma resposta de sucesso: o Orquestrador sempre os
traduz em um resultado `status: error` devolvido ao LLM, nunca em uma
confirmação de ação concluída (BUSINESS_RULES.md #8)."""

from pydantic import ValidationError


class ToolError(Exception):
    """Base de todo erro de execução de uma tool."""


class ToolValidationError(ToolError):
    """Parâmetro obrigatório ausente ou inválido (TOOLS.md: 'toda tool
    valida os parâmetros recebidos antes de executar')."""


class ToolNotFoundError(ToolError):
    """Entidade referenciada (task_id, goal_id, item_id...) não existe ou
    não pertence ao usuário — mesmo tratamento de 404 dos endpoints REST,
    preservando o isolamento por user_id (ARCHITECTURE.md)."""


class UnknownToolError(ToolError):
    """LLM chamou uma tool que não existe no registro (ERROR_HANDLING.md:
    'Orquestrador rejeita a chamada, não executa nada, loga como
    anomalia')."""


def format_validation_error(exc: ValidationError) -> str:
    missing = [
        ".".join(str(part) for part in error["loc"])
        for error in exc.errors()
        if error["type"] == "missing"
    ]
    if missing:
        return f"parâmetro obrigatório ausente: {', '.join(missing)}"
    return "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    )


def require_id(arguments: dict, field: str) -> int:
    """Extrai um parâmetro obrigatório de id (ex.: task_id) já validado como
    inteiro — nunca inferido, nunca adivinhado (TOOLS.md)."""
    value = arguments.get(field)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ToolValidationError(f"parâmetro obrigatório ausente ou inválido: {field}")
    return value
