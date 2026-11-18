"""Référentiels 0002 — retrait des index « _like » ajoutés d'office par
Django sur les clés primaires varchar du MPD-3. Le MPD n'en prévoit pas
(même raison que identite 0002). Réversible."""

from django.db import migrations

INDEX = [
    ("categorie_article_code_categorie_94f64001_like", "categorie_article", "code_categorie"),
    ("corps_etat_code_corps_etat_fbed6819_like", "corps_etat", "code_corps_etat"),
    ("motif_blocage_code_motif_ec1109fd_like", "motif_blocage", "code_motif"),
    ("type_mouvement_code_type_mouvement_29e8b466_like", "type_mouvement", "code_type_mouvement"),
    ("unite_mesure_code_unite_410dded9_like", "unite_mesure", "code_unite"),
]


class Migration(migrations.Migration):
    dependencies = [("referentiels", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql=[f'DROP INDEX IF EXISTS "{nom}"' for nom, _table, _colonne in INDEX],
            reverse_sql=[
                f'CREATE INDEX "{nom}" ON "{table}" ("{colonne}" varchar_pattern_ops)'
                for nom, table, colonne in INDEX
            ],
        ),
    ]
