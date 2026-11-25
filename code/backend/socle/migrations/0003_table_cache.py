"""Socle 0003 — table du cache partagé (Q-BE, B7).

Table technique de Django (comme django_migrations), hors MPD : elle porte
les compteurs de limitation du taux, l'anti-répétition des alertes et le
cache des droits, partagés par tous les processus. Créée sous le rôle
propriétaire ; les privilèges par défaut (socle 0001) l'ouvrent au rôle
applicatif.
"""

from typing import Any

from django.core.management import call_command
from django.db import migrations

TABLE = "django_cache"


def creer(apps: Any, schema_editor: Any) -> None:
    call_command("createcachetable", TABLE, database=schema_editor.connection.alias, verbosity=0)


def supprimer(apps: Any, schema_editor: Any) -> None:
    schema_editor.execute(f'DROP TABLE IF EXISTS "{TABLE}"')


class Migration(migrations.Migration):
    dependencies = [("socle", "0002_execution_traitement")]

    operations = [migrations.RunPython(creer, supprimer)]
