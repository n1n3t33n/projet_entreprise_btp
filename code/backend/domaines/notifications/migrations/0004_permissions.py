"""Notifications 0004 — permissions du domaine (données, EF-AUT-07).

Consulter et marquer ses propres notifications : comme « api.session.lire »
(identite 0004), ces deux droits sont accordés à CHAQUE rôle existant, car
chacun peut recevoir des notifications. Les vues ne servent jamais que les
notifications de l'utilisateur connecté.
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [
    ("api", "notifications", "LIRE", "Consulter ses notifications"),
    ("api", "notifications", "MODIFIER", "Marquer ses notifications comme lues"),
]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)
    Role = apps.get_model("identite", "Role")
    DroitAccorde = apps.get_model("identite", "DroitAccorde")
    for code_role in Role.objects.values_list("code_role", flat=True):
        for module, ressource, action, _libelle in PERMISSIONS:
            DroitAccorde.objects.get_or_create(
                role_id=code_role,
                permission_id=permissions_donnees.code(module, ressource, action),
                defaults={"portee": "GLOBALE"},
            )


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0003_retrait_index_hors_mpd"),
        ("synchronisation", "0002_permissions"),
    ]

    operations = [migrations.RunPython(declarer, retirer)]
