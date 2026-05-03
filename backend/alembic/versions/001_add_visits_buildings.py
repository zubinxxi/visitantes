"""Add visits_buildings pivot table

Revision ID: 001_add_visits_buildings
Revises:
Create Date: 2026-04-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_add_visits_buildings"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "visits_buildings",
        sa.Column("id_visits", sa.Integer(), nullable=False),
        sa.Column("id_building", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_visits"], ["visits.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["id_building"], ["building.id"]
        ),
        sa.PrimaryKeyConstraint("id_visits", "id_building"),
    )


def downgrade() -> None:
    op.drop_table("visits_buildings")
