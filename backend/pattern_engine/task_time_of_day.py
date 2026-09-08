"""Motor de Padrões — padrão de horário de conclusão de tarefa por
categoria (PATTERN_ENGINE.md).

Única fonte de histórico real disponível desde as FASES 2-6: `tasks`.
`habit_logs`, `pattern_events` e `productivity_logs` seguem sem nenhum
escritor no código (não existe módulo de Hábitos nem de Pomodoro ainda) —
por decisão registrada na auditoria da FASE 7 (`DOCUMENTATION_AUDIT.md`),
as tools/endpoints das fases anteriores não foram alteradas para
começarem a alimentar essas tabelas; o Motor de Padrões lê `tasks`
diretamente.

Cálculo sob demanda (decisão registrada em `DOCUMENTATION_AUDIT.md`,
`FLOWS.md` item 7 deixava o gatilho A DEFINIR sem OPÇÃO RECOMENDADA e sem
gate de aprovação — não há worker/scheduler no projeto): toda chamada de
`get_patterns`/`get_routine_changes`, ou montagem de contexto do
Orquestrador, recomputa a janela e sincroniza (upsert) a tabela
`patterns` — não existe job periódico.

`tasks` não tem uma coluna `completed_at` dedicada (schema fixo da
FASE 1) — usamos `updated_at` no momento em que `status` é `done` como
proxy da conclusão. Limitação conhecida: se a tarefa for editada depois
de concluída, `updated_at` passa a refletir a última edição, não o
instante real da conclusão."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from db.models.enums import PatternStatus, TaskCategory, TaskStatus
from db.models.pattern import Pattern
from db.models.task import Task

PATTERN_TYPE_PREFIX = "task_time_of_day"

# DECIDIDO com Jams em 2026-09-07 (ver DOCUMENTATION_AUDIT.md) — valores da
# OPÇÃO RECOMENDADA de PATTERN_ENGINE.md, iguais ao exemplo do próprio
# documento e de TESTING.md.
HISTORICAL_WINDOW_DAYS = 21
RECENT_WINDOW_DAYS = 7
PROMOTION_THRESHOLD = 0.80
CHANGE_CONFIDENCE_THRESHOLD = 0.70

# NECESSÁRIO PARA IMPLEMENTAÇÃO (fora do que precisava de aprovação —
# PATTERN_ENGINE.md só travava janelas/limiares de frequência): número
# mínimo de ocorrências antes de qualquer padrão ser sequer considerado,
# para nunca promover a partir de um evento isolado (BUSINESS_RULES.md #3).
MIN_EVIDENCE = 3

_PERIODS: tuple[tuple[range, str], ...] = (
    (range(0, 6), "madrugada"),
    (range(6, 12), "manhã"),
    (range(12, 18), "tarde"),
    (range(18, 24), "noite"),
)


def _period_for_hour(hour: int) -> str:
    for hours, label in _PERIODS:
        if hour in hours:
            return label
    raise AssertionError(f"hora fora do intervalo 0-23: {hour}")


@dataclass
class _WindowStats:
    predominant_period: Optional[str]
    predominant_count: int
    total_count: int

    @property
    def frequency(self) -> float:
        return self.predominant_count / self.total_count if self.total_count else 0.0


def _window_stats(timestamps: list[datetime]) -> _WindowStats:
    if not timestamps:
        return _WindowStats(None, 0, 0)
    counts = Counter(_period_for_hour(ts.hour) for ts in timestamps)
    period, count = counts.most_common(1)[0]
    return _WindowStats(period, count, len(timestamps))


@dataclass
class ComputedPattern:
    category: str
    pattern_type: str
    status: PatternStatus
    description: str
    confidence: float
    evidence_count: int
    window_start: datetime
    window_end: datetime
    historical_predominant_period: Optional[str]
    historical_frequency: float
    recent_change: bool
    recent_predominant_period: Optional[str] = None
    recent_frequency: float = 0.0


def _completion_timestamps(
    db: Session, user_id: int, category: TaskCategory, since: datetime
) -> list[datetime]:
    rows = (
        db.query(Task.updated_at)
        .filter(
            Task.user_id == user_id,
            Task.category == category,
            Task.status == TaskStatus.DONE,
            Task.updated_at >= since,
        )
        .all()
    )
    return [row[0] for row in rows]


def _describe(category: str, period: Optional[str]) -> str:
    return f"Tarefas de categoria '{category}' geralmente concluídas no período: {period}."


def compute_pattern_for_category(
    db: Session, user_id: int, category: TaskCategory, now: Optional[datetime] = None
) -> Optional[ComputedPattern]:
    """Recomputa o padrão de uma categoria a partir de `tasks`. Retorna
    `None` quando não há evidência mínima — nesse caso nenhum registro é
    criado nem alterado em `patterns` (BUSINESS_RULES.md #3)."""
    now = now or datetime.utcnow()
    window_start = now - timedelta(days=HISTORICAL_WINDOW_DAYS)
    recent_start = now - timedelta(days=RECENT_WINDOW_DAYS)

    historical_timestamps = _completion_timestamps(db, user_id, category, window_start)
    if len(historical_timestamps) < MIN_EVIDENCE:
        return None

    hist = _window_stats(historical_timestamps)
    recent_timestamps = [ts for ts in historical_timestamps if ts >= recent_start]
    recent = _window_stats(recent_timestamps)

    would_be_active = hist.frequency >= PROMOTION_THRESHOLD
    diverges = (
        recent.total_count >= MIN_EVIDENCE
        and recent.predominant_period is not None
        and recent.predominant_period != hist.predominant_period
        and recent.frequency >= CHANGE_CONFIDENCE_THRESHOLD
    )

    category_value = category.value
    pattern_type = f"{PATTERN_TYPE_PREFIX}:{category_value}"

    if diverges and would_be_active:
        # Rebaixamento (PATTERN_ENGINE.md): a janela recente diverge de
        # forma sustentada do padrão que, pela janela histórica, seria
        # ativo — despromovido, sem criar automaticamente um novo padrão
        # `active` para o período emergente (só sinalizado via
        # `recent_change`/get_routine_changes, nunca promovido sozinho).
        status = PatternStatus.DEPRECATED
        description = (
            f"{_describe(category_value, hist.predominant_period)} Percebi uma "
            f"mudança recente para o período: {recent.predominant_period}."
        )
    elif would_be_active:
        status = PatternStatus.ACTIVE
        description = _describe(category_value, hist.predominant_period)
    else:
        status = PatternStatus.CANDIDATE
        description = _describe(category_value, hist.predominant_period)

    return ComputedPattern(
        category=category_value,
        pattern_type=pattern_type,
        status=status,
        description=description,
        confidence=hist.frequency,
        evidence_count=hist.total_count,
        window_start=window_start,
        window_end=now,
        historical_predominant_period=hist.predominant_period,
        historical_frequency=hist.frequency,
        recent_change=diverges,
        recent_predominant_period=recent.predominant_period if diverges else None,
        recent_frequency=recent.frequency if diverges else 0.0,
    )


def _upsert_pattern_row(db: Session, user_id: int, computed: ComputedPattern) -> Pattern:
    row = (
        db.query(Pattern)
        .filter_by(user_id=user_id, pattern_type=computed.pattern_type)
        .first()
    )
    if row is None:
        row = Pattern(user_id=user_id, pattern_type=computed.pattern_type)
        db.add(row)
    row.description = computed.description
    row.confidence = computed.confidence
    row.status = computed.status
    row.window_start = computed.window_start
    row.window_end = computed.window_end
    row.evidence_count = computed.evidence_count
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row


def refresh_patterns_for_user(
    db: Session, user_id: int, now: Optional[datetime] = None
) -> list[tuple[Pattern, ComputedPattern]]:
    """Ponto de entrada único do Motor de Padrões: recomputa sob demanda e
    sincroniza `patterns`. Chamado pelas tools de leitura e pelo
    Orquestrador ao montar o contexto do turno — nunca pelo LLM
    diretamente."""
    categories = (
        db.query(Task.category)
        .filter(
            Task.user_id == user_id,
            Task.status == TaskStatus.DONE,
            Task.category.isnot(None),
        )
        .distinct()
        .all()
    )

    results = []
    for (category,) in categories:
        computed = compute_pattern_for_category(db, user_id, category, now=now)
        if computed is None:
            continue
        row = _upsert_pattern_row(db, user_id, computed)
        results.append((row, computed))
    return results
