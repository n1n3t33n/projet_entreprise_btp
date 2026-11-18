"""Identité 0006 — permission « technique / metriques / LIRE » (données).

Exigée par ``GET /api/metriques`` (exigence 6.6). Elle rejoint les
permissions techniques posées par la migration 0004 (administration,
documentation) et l'administrateur la reçoit pour l'amorçage.
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [
    ("technique", "metriques", "LIRE", "Consulter les métriques d'exploitation"),
]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [("identite", "0005_journal_audit_id_objet")]

    operations = [migrations.RunPython(declarer, retirer)]
