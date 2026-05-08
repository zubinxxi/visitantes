"""add_sc_log_table

Revision ID: 9854d513fdc6
Revises: 003_add_config_table
Create Date: 2026-05-05 10:30:17.432129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9854d513fdc6'
down_revision: Union[str, None] = '003_add_config_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sc_log',
        sa.Column('id', sa.Integer(), nullable=True),
        sa.Column('inserted_date', sa.DateTime(), nullable=True),
        sa.Column('username', sa.String(length=90), nullable=False),
        sa.Column('application', sa.String(length=255), nullable=False),
        sa.Column('creator', sa.String(length=30), nullable=False),
        sa.Column('ip_user', sa.String(length=255), nullable=False),
        sa.Column('action', sa.String(length=30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    pass
