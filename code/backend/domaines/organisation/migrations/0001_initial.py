"""Organisation 0001 — tables socles ``chantier`` et ``magasin`` (MPD-2),
générée par Django 5.2.19 puis relue contre le MPD-2. Ces deux tables
existent dès B1 parce que ``perimetre`` (MPD-1) les référence ; le reste du
MPD-2 arrive en B2 dans une migration suivante.
"""

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Chantier",
            fields=[
                (
                    "id_chantier",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("code", models.CharField(max_length=32)),
                ("nom", models.CharField(max_length=120)),
                ("programme", models.CharField(blank=True, default="", max_length=120)),
                ("date_debut", models.DateField(blank=True, null=True)),
                ("statut", models.CharField(default="ACTIF", max_length=32)),
            ],
            options={
                "verbose_name": "chantier",
                "db_table": "chantier",
                "constraints": [
                    models.UniqueConstraint(fields=("code",), name="uq_chantier_code"),
                    models.CheckConstraint(
                        condition=models.Q(("statut__in", ("ACTIF", "INACTIF", "OUVERT"))),
                        name="ck_chantier_statut",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Magasin",
            fields=[
                (
                    "id_magasin",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("code", models.CharField(max_length=32)),
                ("nom", models.CharField(max_length=120)),
                ("actif", models.BooleanField(default=True)),
                (
                    "chantier",
                    models.ForeignKey(
                        db_column="chantier_id_chantier",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="magasins",
                        to="organisation.chantier",
                    ),
                ),
            ],
            options={
                "verbose_name": "magasin",
                "db_table": "magasin",
                "indexes": [
                    models.Index(fields=["chantier"], name="ix_magasin_chantier_id_chantier")
                ],
                "constraints": [models.UniqueConstraint(fields=("code",), name="uq_magasin_code")],
            },
        ),
    ]
