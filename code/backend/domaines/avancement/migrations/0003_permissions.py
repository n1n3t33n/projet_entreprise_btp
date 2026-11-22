"""Avancement 0003 — permissions du domaine (données, EF-AUT-07).

Une permission par ressource et par action exigée par les vues de
``avancement/api/vues.py``. Déclarer une étape (terminée, bloquée, levée)
demande MODIFIER ; valider ou rejeter une étape à contrôle demande VALIDER
(RG-A4) ; affecter des étapes demande CREER sur les fiches de route.
L'administrateur les reçoit (amorçage).
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [
    ("api", "avancement", "LIRE", "Consulter l'avancement des travaux"),
    ("api", "etapes", "MODIFIER", "Déclarer une étape terminée ou bloquée"),
    ("api", "etapes", "VALIDER", "Valider ou rejeter une étape à contrôle"),
    ("api", "fiches-route", "LIRE", "Consulter les fiches de route"),
    ("api", "fiches-route", "CREER", "Affecter des étapes à un technicien"),
    ("api", "fiches-route", "MODIFIER", "Clôturer une fiche de route"),
]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [
        ("avancement", "0002_journal_execution"),
        ("identite", "0006_permission_metriques"),
    ]

    operations = [migrations.RunPython(declarer, retirer)]
