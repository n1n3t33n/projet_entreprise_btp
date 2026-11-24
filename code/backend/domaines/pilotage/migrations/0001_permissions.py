"""Pilotage 0001 — permissions du domaine (données, EF-AUT-07).

Le rapport hebdomadaire (EF-DSH-06) et les indicateurs d'usage (EF-DSH-07).
L'administrateur les reçoit (amorçage) ; la direction et le responsable
technique reçoivent le rapport dans la démonstration.
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [
    ("api", "rapport-hebdomadaire", "LIRE", "Consulter le rapport hebdomadaire"),
    ("api", "usage", "LIRE", "Consulter les indicateurs d'usage du pilote"),
]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [("notifications", "0004_permissions")]

    operations = [migrations.RunPython(declarer, retirer)]
