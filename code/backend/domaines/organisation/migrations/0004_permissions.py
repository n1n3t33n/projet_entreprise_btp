"""Organisation 0004 — permissions du domaine (données, EF-AUT-07).

Une permission par ressource et par action exigée par les vues de
``organisation/api/vues.py``. L'administrateur les reçoit (amorçage) ; les
autres rôles les reçoivent par la matrice (écran ou démonstration).
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [
    ("api", "chantiers", "LIRE", "Consulter les chantiers"),
    ("api", "chantiers", "MODIFIER", "Modifier un chantier"),
    ("api", "magasins", "LIRE", "Consulter les magasins"),
    ("api", "magasins", "CREER", "Créer un magasin"),
    ("api", "magasins", "MODIFIER", "Modifier un magasin"),
    ("api", "zones", "CREER", "Créer une zone"),
    ("api", "zones", "MODIFIER", "Modifier une zone"),
    ("api", "logements", "LIRE", "Consulter les logements"),
    ("api", "logements", "CREER", "Créer un logement"),
    ("api", "logements", "MODIFIER", "Modifier un logement"),
    ("api", "types-logement", "LIRE", "Consulter les types de logement"),
    ("api", "parametres", "LIRE", "Consulter les paramètres de chantier"),
    ("api", "parametres", "CREER", "Créer un paramètre de chantier"),
    ("api", "parametres", "MODIFIER", "Modifier un paramètre de chantier"),
]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [
        ("organisation", "0003_retrait_index_hors_mpd"),
        ("identite", "0004_referentiel_droits"),
    ]

    operations = [migrations.RunPython(declarer, retirer)]
