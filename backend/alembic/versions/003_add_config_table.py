"""add_config_table

Revision ID: 003_add_config_table
Revises: 002_register_apps
Create Date: 2026-05-05 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '003_add_config_table'
down_revision: Union[str, None] = '002_register_apps'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'config',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key'),
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
        mysql_collate='utf8mb4_general_ci'
    )


def downgrade() -> None:
    op.drop_table('config')
