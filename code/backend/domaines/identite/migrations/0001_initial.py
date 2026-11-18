"""Identité 0001 — tables du MPD-1 hors journal d'audit (générée par Django
5.2.19 depuis les modèles, puis relue contre le MPD-1).

Tables : utilisateur (écarts Q7-1 « mot_de_passe » et Q7-2
« uq_utilisateur_identifiant »), equipe, role, permission, perimetre,
appareil, membre_equipe, droit_accorde, affectation_role (ces trois dernières
à clé primaire composite). Contraintes et index aux noms exacts du MPD-1.
Le journal d'audit, partitionné, est créé à la main en 0003.
"""

import django.db.models.deletion
import django.utils.timezone
import domaines.identite.models.utilisateur
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organisation", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("code_role", models.CharField(max_length=32, primary_key=True, serialize=False)),
                ("libelle", models.CharField(max_length=120)),
                ("systeme", models.BooleanField(default=False)),
                ("actif", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "rôle",
                "db_table": "role",
            },
        ),
        migrations.CreateModel(
            name="Utilisateur",
            fields=[
                (
                    "id_utilisateur",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("identifiant", models.CharField(max_length=120)),
                ("nom", models.CharField(max_length=120)),
                ("prenom", models.CharField(max_length=120)),
                ("fonction", models.CharField(blank=True, default="", max_length=120)),
                ("statut", models.CharField(default="ACTIF", max_length=32)),
                ("date_creation", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "password",
                    models.CharField(
                        db_column="mot_de_passe", max_length=128, verbose_name="mot de passe"
                    ),
                ),
            ],
            options={
                "verbose_name": "utilisateur",
                "db_table": "utilisateur",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("identifiant",), name="uq_utilisateur_identifiant"
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("statut__in", ("ACTIF", "INACTIF"))),
                        name="ck_utilisateur_statut",
                    ),
                ],
            },
            managers=[
                ("objects", domaines.identite.models.utilisateur.GestionnaireUtilisateurs()),
            ],
        ),
        migrations.CreateModel(
            name="Equipe",
            fields=[
                (
                    "id_equipe",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("code", models.CharField(max_length=32)),
                ("libelle", models.CharField(max_length=120)),
                ("actif", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "équipe",
                "db_table": "equipe",
                "constraints": [models.UniqueConstraint(fields=("code",), name="uq_equipe_code")],
            },
        ),
        migrations.CreateModel(
            name="MembreEquipe",
            fields=[
                (
                    "pk",
                    models.CompositePrimaryKey(
                        "utilisateur_id",
                        "equipe_id",
                        blank=True,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("est_chef_equipe", models.BooleanField(default=False)),
                ("date_debut", models.DateField(default=django.utils.timezone.localdate)),
                ("date_fin", models.DateField(blank=True, null=True)),
                (
                    "equipe",
                    models.ForeignKey(
                        db_column="equipe_id_equipe",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="membres",
                        to="identite.equipe",
                    ),
                ),
                (
                    "utilisateur",
                    models.ForeignKey(
                        db_column="utilisateur_id_utilisateur",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="appartenances",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "membre d'équipe",
                "db_table": "membre_equipe",
            },
        ),
        migrations.CreateModel(
            name="Perimetre",
            fields=[
                (
                    "id_perimetre",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("libelle", models.CharField(max_length=120)),
                (
                    "chantier",
                    models.ForeignKey(
                        blank=True,
                        db_column="chantier_id_chantier",
                        db_index=False,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="perimetres",
                        to="organisation.chantier",
                    ),
                ),
                (
                    "magasin",
                    models.ForeignKey(
                        blank=True,
                        db_column="magasin_id_magasin",
                        db_index=False,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="perimetres",
                        to="organisation.magasin",
                    ),
                ),
            ],
            options={
                "verbose_name": "périmètre",
                "db_table": "perimetre",
            },
        ),
        migrations.CreateModel(
            name="Permission",
            fields=[
                (
                    "code_permission",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("module", models.CharField(max_length=120)),
                ("ressource", models.CharField(max_length=120)),
                ("action", models.CharField(max_length=32)),
                ("libelle", models.CharField(max_length=120)),
            ],
            options={
                "verbose_name": "permission",
                "db_table": "permission",
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            ("action__in", ("LIRE", "CREER", "MODIFIER", "VALIDER"))
                        ),
                        name="ck_permission_action",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="DroitAccorde",
            fields=[
                (
                    "pk",
                    models.CompositePrimaryKey(
                        "permission_id",
                        "role_id",
                        blank=True,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("portee", models.CharField(max_length=32)),
                (
                    "permission",
                    models.ForeignKey(
                        db_column="permission_code_permission",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="droits_accordes",
                        to="identite.permission",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        db_column="role_code_role",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="droits_accordes",
                        to="identite.role",
                    ),
                ),
            ],
            options={
                "verbose_name": "droit accordé",
                "db_table": "droit_accorde",
            },
        ),
        migrations.CreateModel(
            name="AffectationRole",
            fields=[
                (
                    "pk",
                    models.CompositePrimaryKey(
                        "role_id",
                        "perimetre_id",
                        "utilisateur_id",
                        blank=True,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("id_affectation", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("date_debut", models.DateField(default=django.utils.timezone.localdate)),
                ("date_fin", models.DateField(blank=True, null=True)),
                (
                    "utilisateur",
                    models.ForeignKey(
                        db_column="utilisateur_id_utilisateur",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="affectations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "perimetre",
                    models.ForeignKey(
                        db_column="perimetre_id_perimetre",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="affectations",
                        to="identite.perimetre",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        db_column="role_code_role",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="affectations",
                        to="identite.role",
                    ),
                ),
            ],
            options={
                "verbose_name": "affectation de rôle",
                "db_table": "affectation_role",
            },
        ),
        migrations.CreateModel(
            name="Appareil",
            fields=[
                (
                    "id_appareil",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("empreinte_materiel", models.CharField(max_length=120)),
                ("plateforme", models.CharField(max_length=120)),
                ("version_application", models.CharField(max_length=120)),
                ("derniere_synchronisation", models.DateTimeField(blank=True, null=True)),
                ("statut", models.CharField(default="ACTIF", max_length=32)),
                (
                    "utilisateur",
                    models.ForeignKey(
                        db_column="utilisateur_id_utilisateur",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="appareils",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "appareil",
                "db_table": "appareil",
                "indexes": [
                    models.Index(
                        fields=["utilisateur"], name="ix_appareil_utilisateur_id_utilisateur"
                    )
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("statut__in", ("ACTIF", "REVOQUE", "INACTIF"))),
                        name="ck_appareil_statut",
                    )
                ],
            },
        ),
        migrations.AddIndex(
            model_name="perimetre",
            index=models.Index(fields=["chantier"], name="ix_perimetre_chantier_id_chantier"),
        ),
        migrations.AddIndex(
            model_name="perimetre",
            index=models.Index(fields=["magasin"], name="ix_perimetre_magasin_id_magasin"),
        ),
        migrations.AddConstraint(
            model_name="droitaccorde",
            constraint=models.CheckConstraint(
                condition=models.Q(("portee__in", ("GLOBALE", "PERIMETRE"))),
                name="ck_droit_accorde_portee",
            ),
        ),
    ]
