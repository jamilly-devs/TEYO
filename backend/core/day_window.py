"""Definição de "dia" do usuário: fronteira/rollover no fuso do usuário e
divisão do dia em períodos.

Extraído de `planner/daily_plan.py` na completude da FASE 8 para ser o
único ponto que responde "que dia é hoje para este usuário?" e "a que
período do dia esta hora pertence?". A FASE 9 (streak, contagem semanal,
gatilhos do mascote por período) precisa usar exatamente a mesma
fronteira — se cada camada calcular a sua, o plano do dia e o streak
discordam sobre o que ainda conta como "hoje".

Divisão de período IDÊNTICA à de `pattern_engine/task_time_of_day.py`
(FASE 7). A duplicação é intencional nesta fase: `pattern_engine` não é
tocado na FASE 8 (Motor de Padrões congelado). Se algum dia os dois
forem unificados, é aqui que a definição canônica fica."""

from datetime import date, datetime, time
from typing import Optional
from zoneinfo import ZoneInfo

from db.models.user import User

PERIOD_ORDER = ("madrugada", "manhã", "tarde", "noite")

_PERIOD_HOURS = {
    "madrugada": range(0, 6),
    "manhã": range(6, 12),
    "tarde": range(12, 18),
    "noite": range(18, 24),
}


def period_for_hour(hour: int) -> str:
    """Período do dia (madrugada/manhã/tarde/noite) de uma hora 0-23."""
    for period, hours in _PERIOD_HOURS.items():
        if hour in hours:
            return period
    raise AssertionError(f"hora fora do intervalo 0-23: {hour}")


def local_today(user: User, now: Optional[datetime] = None) -> date:
    """Data de "hoje" no fuso do usuário.

    `now` explícito (testes) é tratado como já estando no fuso do usuário
    — mesma convenção usada pelo restante do sistema para
    `due_date`/`start_at` (ACCEPTANCE_CRITERIA.md: horário resolvido "no
    fuso do usuário", sem conversão adicional para UTC em nenhum lugar do
    código atual). Sem `now`, usa a hora real no fuso salvo em
    `users.timezone`."""
    if now is not None:
        return now.date()
    return datetime.now(ZoneInfo(user.timezone)).date()


def day_bounds(
    user: User, now: Optional[datetime] = None
) -> tuple[datetime, datetime]:
    """Início (00:00:00) e fim (23:59:59.999999) do dia de hoje do usuário,
    como `datetime` ingênuos — mesma forma que `tasks.due_date` /
    `events.start_at` são gravados hoje (sem tz), para comparação direta
    em query."""
    today = local_today(user, now=now)
    return datetime.combine(today, time.min), datetime.combine(today, time.max)
