"""Ganchos de domínio + despachante síncrono de eventos.

É o único ponto onde a FASE 9 (Gamificação e Mascote) se liga a
acontecimentos do usuário. A FASE 8 criou as três funções `on_*` como
costura (só logavam); a FASE 9 ativa um despachante: cada `on_*`
distribui o evento para os *subscribers* registrados (gamificação,
mascote). Assim os fluxos de tarefa/planejador/etc. **não** precisam
conhecer XP/mascote — continuam só chamando `on_*`.

Regras (mantidas da FASE 8):
- As assinaturas de `on_task_completed` / `on_pomodoro_completed` /
  `on_low_energy_reported` **não mudam**.
- Nenhum subscriber deve dar `commit`/`rollback` — quem originou a ação é
  dono da transação (ARCHITECTURE.md).
- Um subscriber que levanta exceção **nunca** quebra a ação de origem:
  `_dispatch` isola cada um com try/except + log `WARNING`. Trade-off
  registrado em DOCUMENTATION_AUDIT.md: falha de gamificação é silenciosa
  para o usuário (aceitável no V1 — gamificação não é crítica)."""

import logging
from typing import TYPE_CHECKING, Any, Callable

from sqlalchemy.orm import Session

if TYPE_CHECKING:  # evita import circular em runtime; só para type hints
    from db.models.pomodoro import PomodoroSession
    from db.models.task import Task

logger = logging.getLogger(__name__)

# Nomes de evento distribuídos pelo despachante. Os três primeiros são os
# eventos "crus" (origem: tools/endpoints); os demais são derivados,
# emitidos pela própria gamificação para o mascote reagir já com o
# nível/conquista persistidos.
TASK_COMPLETED = "task_completed"
POMODORO_COMPLETED = "pomodoro_completed"
LOW_ENERGY_REPORTED = "low_energy_reported"
LEVEL_UP = "level_up"
ACHIEVEMENT_UNLOCKED = "achievement_unlocked"

Subscriber = Callable[..., None]

_subscribers: dict[str, list[Subscriber]] = {}


def subscribe(event_name: str, fn: Subscriber) -> None:
    """Registra `fn` para `event_name`. Idempotente por identidade de
    função — importar o módulo de subscribers duas vezes não duplica."""
    handlers = _subscribers.setdefault(event_name, [])
    if fn not in handlers:
        handlers.append(fn)


def clear_subscribers() -> None:
    """Só para testes que precisam isolar o registro."""
    _subscribers.clear()


def emit(event_name: str, **payload: Any) -> None:
    """Distribui um evento para todos os subscribers registrados. Cada
    subscriber roda isolado: sua falha é logada e não interrompe os
    demais nem a ação de origem."""
    for fn in list(_subscribers.get(event_name, ())):
        try:
            fn(**payload)
        except Exception:  # noqa: BLE001 — isolamento deliberado (ver docstring do módulo)
            logger.warning(
                "subscriber %s falhou para o evento '%s'",
                getattr(fn, "__qualname__", repr(fn)),
                event_name,
                exc_info=True,
            )


_dispatch = emit


def on_task_completed(db: Session, user_id: int, task: "Task") -> None:
    """Ponto único de "tarefa concluída" (chamado por
    `core.task_completion.complete_task`, que cobre os quatro caminhos:
    tools e REST, `complete_task` e `update_task` com `status=done`)."""
    logger.info("domain_event=task_completed user_id=%s task_id=%s", user_id, task.id)
    _dispatch(TASK_COMPLETED, db=db, user_id=user_id, task=task)


def on_pomodoro_completed(
    db: Session, user_id: int, session: "PomodoroSession"
) -> None:
    """Ponto único de "sessão de Pomodoro concluída".

    A FASE 9 liga a gamificação a este gancho, mas **não cria um módulo de
    Pomodoro**: `pomodoro_sessions` continua sem escritor de produção. O
    caminho é exercitado por teste chamando o gancho direto; quando o
    módulo de Pomodoro existir, é aqui que a conclusão da sessão entra."""
    logger.info(
        "domain_event=pomodoro_completed user_id=%s session_id=%s", user_id, session.id
    )
    _dispatch(POMODORO_COMPLETED, db=db, user_id=user_id, session=session)


def on_low_energy_reported(db: Session, user_id: int) -> None:
    """Sinal de que o usuário relatou baixa energia — disparado por
    `reorganize_day` (tool e endpoint) quando `energy_level == "low"`.

    FASE 9: o subscriber do mascote entra em expressão acolhedora
    (MASCOT.md). Não concede XP (não é atividade nem conquista). Como o
    mascote persiste `mascot_state`, os pontos que chamam este gancho
    fazem `db.commit()` logo depois."""
    logger.info("domain_event=low_energy_reported user_id=%s", user_id)
    _dispatch(LOW_ENERGY_REPORTED, db=db, user_id=user_id)
