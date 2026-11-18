"""Organisation 0003 — retrait de l'index « _like » ajouté d'office par Django
sur la clé primaire varchar de ``type_logement``. Le MPD-2 n'en prévoit pas
(même raison que identite 0002). Réversible."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("organisation", "0002_organisation_complete")]

    operations = [
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS "type_logement_code_type_d1c72d27_like"',
            reverse_sql='CREATE INDEX "type_logement_code_type_d1c72d27_like" '
            'ON "type_logement" ("code_type" varchar_pattern_ops)',
        ),
    ]
