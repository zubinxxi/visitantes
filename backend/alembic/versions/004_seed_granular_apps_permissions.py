"""Seed granular apps and group permissions

Revision ID: 004_seed_granular_apps
Revises: 9854d513fdc6
Create Date: 2026-05-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_seed_granular_apps"
down_revision: Union[str, None] = "9854d513fdc6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Nuevas apps granulares (las existentes se mantienen)
NEW_APPS = [
    ("profile", "page", "Editar perfil"),
    ("checkin", "page", "Registro de visitas (Check-in)"),
    ("checkout", "page", "Checkout rápido"),
    ("active_visits", "page", "Visitas activas"),
    ("visit_history", "page", "Historial de visitas"),
    ("maint_provinces", "crud", "Mantenimiento: Provincias"),
    ("maint_institutions", "crud", "Mantenimiento: Instituciones"),
    ("maint_type_uadm", "crud", "Mantenimiento: Tipos de UADM"),
    ("maint_buildings", "crud", "Mantenimiento: Edificios"),
    ("maint_procedures", "crud", "Mantenimiento: Tipo de trámite"),
    ("maint_uadms", "crud", "Mantenimiento: Unidades Administrativas"),
    ("sec_users", "crud", "Seguridad: Usuarios"),
    ("sec_groups", "crud", "Seguridad: Grupos"),
    ("sec_apps", "crud", "Seguridad: Aplicaciones"),
    ("sec_permissions", "page", "Seguridad: Permisos por grupo"),
    ("sec_members", "page", "Seguridad: Miembros por grupo"),
    ("config", "page", "Configuración del sistema"),
]

# Permisos del Grupo 2 - Usuarios
GROUP_2_PERMS = [
    # (app_name, access, insert, delete, update, export, print)
    ("dashboard", "Y", "N", "N", "N", "N", "N"),
    ("profile", "Y", "N", "N", "Y", "N", "N"),
]

# Permisos del Grupo 3 - Seguridad
GROUP_3_PERMS = [
    ("dashboard", "Y", "N", "N", "N", "N", "N"),
    ("visitors", "Y", "Y", "Y", "Y", "Y", "Y"),
    ("checkin", "Y", "Y", "N", "N", "N", "N"),
    ("checkout", "Y", "N", "N", "Y", "N", "N"),
    ("active_visits", "Y", "N", "N", "N", "N", "N"),
    ("visit_history", "Y", "N", "N", "N", "Y", "Y"),
]

# Permisos del Grupo 4 - Admin-Seguridad (hereda de Seguridad + usuarios)
GROUP_4_PERMS = [
    ("dashboard", "Y", "N", "N", "N", "N", "N"),
    ("visitors", "Y", "Y", "Y", "Y", "Y", "Y"),
    ("checkin", "Y", "Y", "N", "N", "N", "N"),
    ("checkout", "Y", "N", "N", "Y", "N", "N"),
    ("active_visits", "Y", "N", "N", "N", "N", "N"),
    ("visit_history", "Y", "N", "N", "N", "Y", "Y"),
    ("sec_users", "Y", "Y", "Y", "Y", "N", "N"),
    ("sec_members", "Y", "N", "N", "N", "N", "N"),
]


def upgrade() -> None:
    # Insertar nuevas apps
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
            for a in NEW_APPS
        ],
    )

    # Insertar permisos por grupo
    sec_groups_apps = sa.table(
        "sec_groups_apps",
        sa.column("group_id", sa.Integer),
        sa.column("app_name", sa.String),
        sa.column("priv_access", sa.String),
        sa.column("priv_insert", sa.String),
        sa.column("priv_delete", sa.String),
        sa.column("priv_update", sa.String),
        sa.column("priv_export", sa.String),
        sa.column("priv_print", sa.String),
    )

    def _perm_rows(group_id: int, perms: list) -> list[dict]:
        return [
            {
                "group_id": group_id,
                "app_name": p[0],
                "priv_access": p[1],
                "priv_insert": p[2],
                "priv_delete": p[3],
                "priv_update": p[4],
                "priv_export": p[5],
                "priv_print": p[6],
            }
            for p in perms
        ]

    op.bulk_insert(sec_groups_apps, _perm_rows(2, GROUP_2_PERMS))
    op.bulk_insert(sec_groups_apps, _perm_rows(3, GROUP_3_PERMS))
    op.bulk_insert(sec_groups_apps, _perm_rows(4, GROUP_4_PERMS))


def downgrade() -> None:
    # Eliminar permisos de grupos 2, 3, 4
    sec_groups_apps = sa.table(
        "sec_groups_apps",
        sa.column("group_id", sa.Integer),
    )
    op.execute(
        sec_groups_apps.delete().where(
            sec_groups_apps.c.group_id.in_([2, 3, 4])
        )
    )

    # Eliminar apps nuevas
    sec_apps = sa.table(
        "sec_apps",
        sa.column("app_name", sa.String),
    )
    op.execute(
        sec_apps.delete().where(
            sec_apps.c.app_name.in_([a[0] for a in NEW_APPS])
        )
    )
