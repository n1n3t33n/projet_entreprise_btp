"""Socle 0002 — table technique ``execution_traitement`` (hors MPD, écart
Q9/Q-G, dette v0.2) : trace de chaque passage des traitements ordonnancés
(exigences 6.5 et 6.6). Générée par Django 5.2.19 depuis ``socle/models.py``.
"""

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("socle", "0001_fonctions_et_droits"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExecutionTraitement",
            fields=[
                (
                    "id_execution",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("nom_traitement", models.CharField(max_length=120)),
                ("debut", models.DateTimeField(default=django.utils.timezone.now)),
                ("fin", models.DateTimeField(blank=True, null=True)),
                ("statut", models.CharField(default="EN_COURS", max_length=32)),
                ("detail", models.TextField(blank=True, default="")),
            ],
            options={
                "verbose_name": "exécution de traitement",
                "db_table": "execution_traitement",
                "indexes": [
                    models.Index(
                        fields=["nom_traitement", "-debut"],
                        name="ix_execution_traitement_nom_debut",
                    )
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("statut__in", ("EN_COURS", "REUSSI", "ECHEC"))),
                        name="ck_execution_traitement_statut",
                    )
                ],
            },
        ),
    ]
