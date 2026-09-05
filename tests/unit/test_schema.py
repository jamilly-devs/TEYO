import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.base import Base
from db import models  # noqa: F401  (registers every model on Base.metadata)


EXPECTED_TABLES = {
    "users",
    "sessions",
    "tasks",
    "habits",
    "habit_logs",
    "goals",
    "events",
    "market_items",
    "financial_records",
    "patterns",
    "pattern_events",
    "memory_entries",
    "conversations",
    "messages",
    "productivity_logs",
    "gamification_state",
    "gamification_events",
    "mascot_state",
    "pomodoro_sessions",
}

FORBIDDEN_TABLES = {"pets", "news_preferences", "reports", "career", "studies", "house"}


@pytest.fixture()
def engine(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_expected_tables_exist_and_forbidden_tables_do_not(engine):
    table_names = set(Base.metadata.tables.keys())
    assert EXPECTED_TABLES <= table_names
    assert table_names.isdisjoint(FORBIDDEN_TABLES)


def test_task_defaults_match_documented_contract(engine):
    with Session(engine) as session:
        session.execute(
            text("INSERT INTO users (email, password_hash) VALUES ('a@b.com', 'x')")
        )
        session.execute(text("INSERT INTO tasks (user_id, title) VALUES (1, 'lavar louça')"))
        session.commit()

        row = session.execute(
            text("SELECT status, priority, category, is_recurring FROM tasks")
        ).one()
        assert row.status == "pending"
        assert row.priority == "medium"
        assert row.category is None
        assert row.is_recurring == 0


def test_user_gets_default_timezone(engine):
    with Session(engine) as session:
        session.execute(
            text("INSERT INTO users (email, password_hash) VALUES ('b@c.com', 'x')")
        )
        session.commit()
        timezone = session.execute(text("SELECT timezone FROM users")).scalar_one()
        assert timezone == "America/Sao_Paulo"


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO tasks (user_id, title, priority) VALUES (1, 'x', 'urgent')",
        "INSERT INTO tasks (user_id, title, category) VALUES (1, 'x', 'career')",
        "INSERT INTO habits (user_id, title, frequency_target) VALUES (1, 'h', 8)",
        "INSERT INTO goals (user_id, title, status) VALUES (1, 'g', 'archived')",
        "INSERT INTO financial_records (user_id, type, amount, date) "
        "VALUES (1, 'transfer', 1, '2026-01-01')",
    ],
)
def test_check_constraints_reject_undocumented_values(engine, sql):
    with Session(engine) as session:
        session.execute(
            text("INSERT INTO users (email, password_hash) VALUES ('c@d.com', 'x')")
        )
        session.commit()
        with pytest.raises(IntegrityError):
            session.execute(text(sql))
            session.commit()


def test_duplicate_email_is_rejected(engine):
    with Session(engine) as session:
        session.execute(
            text("INSERT INTO users (email, password_hash) VALUES ('dup@e.com', 'x')")
        )
        session.commit()
        with pytest.raises(IntegrityError):
            session.execute(
                text("INSERT INTO users (email, password_hash) VALUES ('dup@e.com', 'y')")
            )
            session.commit()
