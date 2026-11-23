"""Synchronisation 0002 — permissions du domaine (données, EF-AUT-07).

Envoyer un lot demande CREER sur la synchronisation ; chaque événement exige
en plus le droit de l'opération qu'il porte (mouvement, déclaration…).
Consulter et traiter les anomalies (EF-SYN-05) demande LIRE et MODIFIER.
L'administrateur les reçoit (amorçage). Les permissions d'écran
(« ecran.synchronisation », « mobile.synchro ») restent celles d'identite 0004.
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [
    ("api", "synchronisation", "CREER", "Envoyer les opérations faites hors ligne"),
    ("api", "anomalies", "LIRE", "Consulter les anomalies de synchronisation"),
    ("api", "anomalies", "MODIFIER", "Traiter les anomalies de synchronisation"),
]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [
        ("synchronisation", "0001_initial"),
        ("avancement", "0003_permissions"),
    ]

    operations = [migrations.RunPython(declarer, retirer)]
