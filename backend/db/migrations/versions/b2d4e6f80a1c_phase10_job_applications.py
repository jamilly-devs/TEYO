"""phase 10 — job_applications table

Revision ID: b2d4e6f80a1c
Revises: 9a1c7f2b5e04
Create Date: 2026-09-09 12:00:00.000000

FASE 10 (Estudos, Casa, Carreira, Hábitos, Pomodoro). Único módulo com
persistência nova é Carreira (acompanhamento manual de candidaturas).
Estudos/Casa reutilizam `tasks.category`; Hábitos reutilizam `habits`/
`habit_logs`; Pomodoro reutiliza `pomodoro_sessions` — nenhuma outra
alteração de schema.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2d4e6f80a1c'
down_revision: Union[str, Sequence[str], None] = '9a1c7f2b5e04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'job_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('applied_on', sa.Date(), nullable=True),
        sa.Column(
            'status',
            sa.Enum(
                'interested',
                'applied',
                'interviewing',
                'offer',
                'rejected',
                name='jobapplicationstatus',
                native_enum=False,
                create_constraint=True,
            ),
            server_default='interested',
            nullable=False,
        ),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_job_applications_user_id', 'job_applications', ['user_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_job_applications_user_id', table_name='job_applications')
    op.drop_table('job_applications')
