"""Acquéreur 0001 — permission de l'espace acquéreur (données, EF-AUT-07).

« api.acquereur.lire » : consulter SON logement et ses notifications
(EF-ACQ-01, 02). Accordée au rôle ACQUEREUR ; l'administrateur la reçoit
(amorçage).
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [("api", "acquereur", "LIRE", "Consulter l'avancement de son logement")]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)
    apps.get_model("identite", "DroitAccorde").objects.get_or_create(
        role_id="ACQUEREUR",
        permission_id=permissions_donnees.code("api", "acquereur", "LIRE"),
        defaults={"portee": "GLOBALE"},
    )


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [("pilotage", "0001_permissions")]

    operations = [migrations.RunPython(declarer, retirer)]
