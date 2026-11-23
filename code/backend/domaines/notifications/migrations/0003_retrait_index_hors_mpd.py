"""Notifications 0003 — retrait de l'index « _like » ajouté d'office par
Django sur la clé primaire varchar de ``type_notification``. Le MPD n'en
prévoit pas (même raison que referentiels 0002). Réversible."""

from django.db import migrations

INDEX = [
    ("type_notification_code_type_f6ef1430_like", "type_notification", "code_type"),
]


class Migration(migrations.Migration):
    dependencies = [("notifications", "0002_catalogue")]

    operations = [
        migrations.RunSQL(
            sql=[f'DROP INDEX IF EXISTS "{nom}"' for nom, _table, _colonne in INDEX],
            reverse_sql=[
                f'CREATE INDEX "{nom}" ON "{table}" ("{colonne}" varchar_pattern_ops)'
                for nom, table, colonne in INDEX
            ],
        ),
    ]
