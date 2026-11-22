"""Stock 0003 — permissions du domaine (données, EF-AUT-07).

Une permission par ressource et par action exigée par les vues de
``stock/api/vues.py``. Valider une sortie ou un écart d'inventaire demande
VALIDER (RG-S6, RG-S9). L'administrateur les reçoit (amorçage).
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [
    ("api", "stock", "LIRE", "Consulter le stock et ses alertes"),
    ("api", "mouvements", "LIRE", "Consulter l'historique des mouvements"),
    ("api", "mouvements", "CREER", "Enregistrer un mouvement de stock"),
    ("api", "mouvements", "VALIDER", "Valider ou refuser une sortie, annuler un mouvement"),
    ("api", "seuils", "MODIFIER", "Définir les seuils de stock"),
    ("api", "inventaires", "LIRE", "Consulter les inventaires"),
    ("api", "inventaires", "CREER", "Ouvrir un inventaire"),
    ("api", "inventaires", "MODIFIER", "Saisir un comptage d'inventaire"),
    ("api", "inventaires", "VALIDER", "Valider les écarts d'inventaire"),
]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [
        ("stock", "0002_journaux_immuables"),
        ("identite", "0006_permission_metriques"),
        ("referentiels", "0004_types_mouvement_systeme"),
    ]

    operations = [migrations.RunPython(declarer, retirer)]
