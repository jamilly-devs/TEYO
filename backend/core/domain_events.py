"""Ganchos de domínio — o único ponto onde a FASE 9 (Gamificação e
Mascote) se liga a acontecimentos do usuário.

Decisão de integração FASE 8/FASE 9: em vez de a FASE 9 ter que reabrir
`tools/tasks.py`, `api/routers/tasks.py`, `tools/planner.py` e o
Orquestrador para plugar XP/expressão do mascote, esses fluxos já chamam
os ganchos abaixo agora. Nesta fase os ganchos **não têm efeito** — só
registram log. NÃO implementar XP, nível, conquista, `gamification_*` ou
`mascot_*` aqui: isso é FASE 9 (GAMIFICATION.md, MASCOT.md).

Contrato para a FASE 9: os ganchos recebem `db` para poderem persistir
sem mudar a assinatura, mas **não devem** dar `commit`/`rollback` — quem
chama é dono da transação (mesma regra das tools em ARCHITECTURE.md)."""

import logging
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

if TYPE_CHECKING:  # evita import circular em runtime; só para type hints
    from db.models.pomodoro import PomodoroSession
    from db.models.task import Task

logger = logging.getLogger(__name__)


def on_task_completed(db: Session, user_id: int, task: "Task") -> None:
    """Ponto único de "tarefa concluída" (chamado por
    `core.task_completion.complete_task`, que por sua vez cobre os quatro
    caminhos: tools e REST, `complete_task` e `update_task` com
    `status=done`).

    FASE 8: sem efeito. FASE 9 liga aqui o evento de XP
    (`gamification_events`) e a possível reação do mascote citados em
    TOOLS.md."""
    logger.info("domain_event=task_completed user_id=%s task_id=%s", user_id, task.id)


def on_pomodoro_completed(
    db: Session, user_id: int, session: "PomodoroSession"
) -> None:
    """Ponto único de "sessão de Pomodoro concluída".

    Definido agora para a FASE 9 não precisar reabrir o fluxo, mas **ainda
    sem chamador**: não existe módulo de Pomodoro (`pomodoro_sessions` não
    tem escritor no código). Quando o Pomodoro for construído, é este o
    gancho que a conclusão da sessão deve chamar. FASE 8: sem efeito."""
    logger.info(
        "domain_event=pomodoro_completed user_id=%s session_id=%s", user_id, session.id
    )


def on_low_energy_reported(db: Session, user_id: int) -> None:
    """Sinal observável de que o usuário relatou baixa energia — disparado
    por `reorganize_day` (tool e endpoint) quando `energy_level == "low"`.

    FASE 8: sem efeito, sem gravar nada (não há tabela de energia e
    `gamification_*` está fora de escopo) — só log. FASE 9 usa este sinal
    para a expressão acolhedora do mascote (MASCOT.md: "usuário cansado →
    expressão acolhedora")."""
    logger.info("domain_event=low_energy_reported user_id=%s", user_id)
