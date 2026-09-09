"""phase 9 — achievements table

Revision ID: 9a1c7f2b5e04
Revises: 411d53b0e447
Create Date: 2026-09-09 00:00:00.000000

FASE 9 (Gamificação e Mascote). Todas as outras tabelas de gamificação
(`gamification_state`, `gamification_events`, `mascot_state`) já existem
desde a migration inicial; a FASE 9 só acrescenta `achievements` para o
estado "conquista desbloqueada" (ver DATABASE.md, atualizado nesta fase).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9a1c7f2b5e04'
down_revision: Union[str, Sequence[str], None] = '411d53b0e447'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column(
            'unlocked_at',
            sa.DateTime(),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'code', name='uq_achievements_user_id_code'),
    )
    op.create_index('ix_achievements_user_id', 'achievements', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_achievements_user_id', table_name='achievements')
    op.drop_table('achievements')
