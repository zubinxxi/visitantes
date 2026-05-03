"""Register applications in sec_apps

Revision ID: 002_register_apps
Revises: 001_add_visits_buildings
Create Date: 2026-04-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_register_apps"
down_revision: Union[str, None] = "001_add_visits_buildings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

APPS = [
    ("dashboard", "page", "Panel principal"),
    ("visitors", "module", "Gestión de visitantes"),
    ("visits", "module", "Gestión de visitas"),
    ("maintenance", "module", "Tablas de mantenimiento"),
    ("reports", "module", "Reportes"),
    ("settings", "module", "Configuración del sistema"),
]


def upgrade() -> None:
    sec_apps = sa.table(
        "sec_apps",
        sa.column("app_name", sa.String),
        sa.column("app_type", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        sec_apps,
        [
            {"app_name": a[0], "app_type": a[1], "description": a[2]}
            for a in APPS
        ],
    )


def downgrade() -> None:
    sec_apps = sa.table(
        "sec_apps",
        sa.column("app_name", sa.String),
    )
    op.execute(
        sec_apps.delete().where(
            sec_apps.c.app_name.in_([a[0] for a in APPS])
        )
    )
