"""Organisation 0002 — reste du MPD-2 (générée par Django 5.2.19 depuis les
modèles, relue contre le MPD-2).

Tables : zone, type_logement, logement, parametre_chantier (avec la colonne
``libelle``, écart Q-D), acquereur. Contraintes et index aux noms du MPD.
``ck_chantier_statut`` passe à {ACTIF, INACTIF} (arbitrage Q-A). Nullité des
clés étrangères tirée du MCD-2 (règle I-32).
"""

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisation", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Acquereur",
            fields=[
                (
                    "id_acquereur",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("nom", models.CharField(max_length=120)),
                ("prenom", models.CharField(max_length=120)),
                ("telephone", models.CharField(blank=True, default="", max_length=120)),
                ("date_acquisition", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "acquéreur",
                "db_table": "acquereur",
            },
        ),
        migrations.CreateModel(
            name="Logement",
            fields=[
                (
                    "id_logement",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("numero", models.CharField(max_length=120)),
                ("statut", models.CharField(default="A_VENIR", max_length=32)),
                ("date_livraison_prevue", models.DateField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "logement",
                "db_table": "logement",
            },
        ),
        migrations.CreateModel(
            name="ParametreChantier",
            fields=[
                (
                    "id_parametre",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("cle", models.CharField(max_length=32)),
                ("valeur", models.CharField(max_length=120)),
                ("type_valeur", models.CharField(max_length=32)),
                ("libelle", models.CharField(blank=True, max_length=120, null=True)),
            ],
            options={
                "verbose_name": "paramètre de chantier",
                "db_table": "parametre_chantier",
            },
        ),
        migrations.CreateModel(
            name="TypeLogement",
            fields=[
                ("code_type", models.CharField(max_length=32, primary_key=True, serialize=False)),
                ("libelle", models.CharField(max_length=120)),
                (
                    "surface_reference",
                    models.DecimalField(blank=True, decimal_places=3, max_digits=14, null=True),
                ),
                ("actif", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "type de logement",
                "db_table": "type_logement",
            },
        ),
        migrations.CreateModel(
            name="Zone",
            fields=[
                (
                    "id_zone",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("code", models.CharField(max_length=32)),
                ("nom", models.CharField(max_length=120)),
                ("type_zone", models.CharField(max_length=32)),
            ],
            options={
                "verbose_name": "zone",
                "db_table": "zone",
            },
        ),
        migrations.RemoveConstraint(
            model_name="chantier",
            name="ck_chantier_statut",
        ),
        migrations.AddConstraint(
            model_name="chantier",
            constraint=models.CheckConstraint(
                condition=models.Q(("statut__in", ("ACTIF", "INACTIF"))), name="ck_chantier_statut"
            ),
        ),
        migrations.AddField(
            model_name="acquereur",
            name="logement",
            field=models.ForeignKey(
                db_column="logement_id_logement",
                db_index=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="acquereurs",
                to="organisation.logement",
            ),
        ),
        migrations.AddField(
            model_name="parametrechantier",
            name="chantier",
            field=models.ForeignKey(
                db_column="chantier_id_chantier",
                db_index=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="parametres",
                to="organisation.chantier",
            ),
        ),
        migrations.AddField(
            model_name="logement",
            name="type_logement",
            field=models.ForeignKey(
                db_column="type_logement_code_type",
                db_index=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="logements",
                to="organisation.typelogement",
            ),
        ),
        migrations.AddField(
            model_name="zone",
            name="chantier",
            field=models.ForeignKey(
                db_column="chantier_id_chantier",
                db_index=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="zones",
                to="organisation.chantier",
            ),
        ),
        migrations.AddField(
            model_name="logement",
            name="zone",
            field=models.ForeignKey(
                db_column="zone_id_zone",
                db_index=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="logements",
                to="organisation.zone",
            ),
        ),
        migrations.AddIndex(
            model_name="acquereur",
            index=models.Index(fields=["logement"], name="ix_acquereur_logement_id_logement"),
        ),
        migrations.AddIndex(
            model_name="parametrechantier",
            index=models.Index(
                fields=["chantier"], name="ix_parametre_chantier_chantier_id_chantier"
            ),
        ),
        migrations.AddConstraint(
            model_name="parametrechantier",
            constraint=models.CheckConstraint(
                condition=models.Q(("type_valeur__in", ("ENTIER", "DECIMAL", "BOOLEEN", "TEXTE"))),
                name="ck_parametre_chantier_type_valeur",
            ),
        ),
        migrations.AddIndex(
            model_name="zone",
            index=models.Index(fields=["chantier"], name="ix_zone_chantier_id_chantier"),
        ),
        migrations.AddConstraint(
            model_name="zone",
            constraint=models.UniqueConstraint(fields=("code",), name="uq_zone_code"),
        ),
        migrations.AddConstraint(
            model_name="zone",
            constraint=models.CheckConstraint(
                condition=models.Q(("type_zone__in", ("BATIMENT", "NIVEAU", "TRANCHE"))),
                name="ck_zone_type_zone",
            ),
        ),
        migrations.AddIndex(
            model_name="logement",
            index=models.Index(fields=["zone"], name="ix_logement_zone_id_zone"),
        ),
        migrations.AddIndex(
            model_name="logement",
            index=models.Index(
                fields=["type_logement"], name="ix_logement_type_logement_code_type"
            ),
        ),
        migrations.AddConstraint(
            model_name="logement",
            constraint=models.CheckConstraint(
                condition=models.Q(("statut__in", ("A_VENIR", "EN_COURS", "LIVRE"))),
                name="ck_logement_statut",
            ),
        ),
    ]
