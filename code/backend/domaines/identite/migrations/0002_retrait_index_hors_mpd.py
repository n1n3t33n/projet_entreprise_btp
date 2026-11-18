"""Identité 0002 — retrait des index ajoutés d'office par Django.

Sur PostgreSQL, Django crée automatiquement un second index
« varchar_pattern_ops » (suffixe « _like ») sur toute clé primaire varchar,
pour accélérer les recherches « LIKE ». Le MPD-1 n'en prévoit pas : il liste
exactement ses index (62 au total, MPD § 6.5). Le modèle faisant foi, on les
retire. Réversible : le retour arrière les recrée à l'identique.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("identite", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql=[
                'DROP INDEX IF EXISTS "role_code_role_111752c8_like"',
                'DROP INDEX IF EXISTS "permission_code_permission_e876315f_like"',
            ],
            reverse_sql=[
                'CREATE INDEX "role_code_role_111752c8_like" '
                'ON "role" ("code_role" varchar_pattern_ops)',
                'CREATE INDEX "permission_code_permission_e876315f_like" '
                'ON "permission" ("code_permission" varchar_pattern_ops)',
            ],
        ),
    ]
