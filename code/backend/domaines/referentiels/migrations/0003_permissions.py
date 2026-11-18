"""Référentiels 0003 — permissions du domaine (données, EF-AUT-07).

Une permission par ressource et par action exigée par les vues de
``referentiels/api/vues.py``. Publier ou archiver une gamme demande VALIDER
(EF-REF-09). L'administrateur les reçoit (amorçage).
"""

from typing import Any

from django.db import migrations

from socle import permissions_donnees

PERMISSIONS = [
    ("api", "categories", "LIRE", "Consulter les familles d'articles"),
    ("api", "unites", "LIRE", "Consulter les unités de mesure"),
    ("api", "articles", "LIRE", "Consulter le catalogue d'articles"),
    ("api", "articles", "CREER", "Créer un article"),
    ("api", "articles", "MODIFIER", "Modifier un article"),
    ("api", "corps-etat", "LIRE", "Consulter les corps d'état"),
    ("api", "corps-etat", "CREER", "Créer un corps d'état"),
    ("api", "corps-etat", "MODIFIER", "Modifier un corps d'état"),
    ("api", "gammes", "LIRE", "Consulter les gammes"),
    ("api", "gammes", "CREER", "Préparer une nouvelle version de gamme"),
    ("api", "gammes", "MODIFIER", "Modifier les étapes d'un brouillon de gamme"),
    ("api", "gammes", "VALIDER", "Publier ou archiver une gamme"),
    ("api", "types-mouvement", "LIRE", "Consulter les types de mouvement"),
    ("api", "motifs-blocage", "LIRE", "Consulter les motifs de blocage"),
    ("api", "regles", "LIRE", "Consulter les règles de validation"),
    ("api", "regles", "CREER", "Créer une règle de validation"),
    ("api", "regles", "MODIFIER", "Modifier une règle de validation"),
    ("api", "import", "CREER", "Importer un référentiel en CSV"),
]


def declarer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.declarer(apps, PERMISSIONS)


def retirer(apps: Any, schema_editor: Any) -> None:
    permissions_donnees.retirer(apps, PERMISSIONS)


class Migration(migrations.Migration):
    dependencies = [
        ("referentiels", "0002_retrait_index_hors_mpd"),
        ("identite", "0004_referentiel_droits"),
    ]

    operations = [migrations.RunPython(declarer, retirer)]
