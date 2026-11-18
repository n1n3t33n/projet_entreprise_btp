"""Identité 0005 — colonne ``id_objet`` du journal d'audit (écart Q-C).

``journal_audit`` a été créée en SQL (0003) : la colonne est donc ajoutée en
SQL sur la table PARENTE, et PostgreSQL la propage à chaque partition
existante ; toute partition créée ensuite par ``socle_creer_partition_
mensuelle`` (« PARTITION OF ») hérite du schéma du parent. Ajout sans
réécriture des données : colonne nullable, sans valeur par défaut. Le test
``test_id_objet_existe_sur_chaque_partition`` le vérifie.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("identite", "0004_referentiel_droits")]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="journalaudit",
                    name="id_objet",
                    field=models.CharField(blank=True, max_length=120, null=True),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE journal_audit ADD COLUMN id_objet varchar(120) NULL",
                    reverse_sql="ALTER TABLE journal_audit DROP COLUMN id_objet",
                ),
            ],
        ),
    ]
