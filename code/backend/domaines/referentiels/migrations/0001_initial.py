"""Référentiels 0001 — tables du MPD-3 (générée par Django 5.2.19 depuis les
modèles, relue contre le MPD-3).

Tables : categorie_article, unite_mesure, article, conditionnement (clé
composite), corps_etat, gamme, etape_modele, type_mouvement, motif_blocage,
regle_validation. ``gamme`` référence ``type_logement`` du domaine
organisation (sens du graphe des dépendances). Aucun CHECK sur
``regle_validation.type_evenement`` et ``operateur`` : le MPD les laisse libres.
"""

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organisation", "0002_organisation_complete"),
    ]

    operations = [
        migrations.CreateModel(
            name="CategorieArticle",
            fields=[
                (
                    "code_categorie",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("libelle", models.CharField(max_length=120)),
            ],
            options={
                "verbose_name": "famille d'articles",
                "db_table": "categorie_article",
            },
        ),
        migrations.CreateModel(
            name="CorpsEtat",
            fields=[
                (
                    "code_corps_etat",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("libelle", models.CharField(max_length=120)),
                ("ordre", models.IntegerField()),
                ("couleur", models.CharField(max_length=120)),
            ],
            options={
                "verbose_name": "corps d'état",
                "db_table": "corps_etat",
            },
        ),
        migrations.CreateModel(
            name="MotifBlocage",
            fields=[
                ("code_motif", models.CharField(max_length=32, primary_key=True, serialize=False)),
                ("libelle", models.CharField(max_length=120)),
                ("requiert_article", models.BooleanField(default=False)),
                ("actif", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "motif de blocage",
                "db_table": "motif_blocage",
            },
        ),
        migrations.CreateModel(
            name="RegleValidation",
            fields=[
                (
                    "id_regle",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("type_evenement", models.CharField(max_length=120)),
                ("champ_teste", models.CharField(max_length=120)),
                ("operateur", models.CharField(max_length=120)),
                (
                    "valeur_seuil",
                    models.DecimalField(blank=True, decimal_places=3, max_digits=14, null=True),
                ),
                ("delai_heures", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "règle de validation",
                "db_table": "regle_validation",
            },
        ),
        migrations.CreateModel(
            name="TypeMouvement",
            fields=[
                (
                    "code_type_mouvement",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("libelle", models.CharField(max_length=120)),
                ("sens", models.IntegerField()),
                ("motif_obligatoire", models.BooleanField(default=False)),
                ("destination_obligatoire", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "type de mouvement",
                "db_table": "type_mouvement",
            },
        ),
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "id_article",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("code", models.CharField(max_length=32)),
                ("designation", models.CharField(max_length=120)),
                ("origine", models.CharField(max_length=32)),
                ("code_barre", models.CharField(blank=True, max_length=32, null=True)),
                ("actif", models.BooleanField(default=True)),
                (
                    "categorie_article",
                    models.ForeignKey(
                        blank=True,
                        db_column="categorie_article_code_categorie",
                        db_index=False,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="articles",
                        to="referentiels.categoriearticle",
                    ),
                ),
            ],
            options={
                "verbose_name": "article",
                "db_table": "article",
            },
        ),
        migrations.CreateModel(
            name="Gamme",
            fields=[
                (
                    "id_gamme",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("version", models.IntegerField()),
                ("libelle", models.CharField(max_length=120)),
                ("statut", models.CharField(default="BROUILLON", max_length=32)),
                ("date_activation", models.DateTimeField(blank=True, null=True)),
                (
                    "type_logement",
                    models.ForeignKey(
                        db_column="type_logement_code_type",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="gammes",
                        to="organisation.typelogement",
                    ),
                ),
            ],
            options={
                "verbose_name": "gamme",
                "db_table": "gamme",
            },
        ),
        migrations.CreateModel(
            name="EtapeModele",
            fields=[
                (
                    "id_etape_modele",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("code", models.CharField(max_length=32)),
                ("libelle", models.CharField(max_length=120)),
                ("ordre", models.IntegerField()),
                ("poids", models.DecimalField(decimal_places=3, max_digits=14)),
                ("controle_requis", models.BooleanField(default=False)),
                (
                    "corps_etat",
                    models.ForeignKey(
                        db_column="corps_etat_code_corps_etat",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="etapes_modeles",
                        to="referentiels.corpsetat",
                    ),
                ),
                (
                    "gamme",
                    models.ForeignKey(
                        db_column="gamme_id_gamme",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="etapes",
                        to="referentiels.gamme",
                    ),
                ),
            ],
            options={
                "verbose_name": "étape modèle",
                "db_table": "etape_modele",
            },
        ),
        migrations.CreateModel(
            name="UniteMesure",
            fields=[
                ("code_unite", models.CharField(max_length=32, primary_key=True, serialize=False)),
                ("libelle", models.CharField(max_length=120)),
                ("type_unite", models.CharField(max_length=32)),
            ],
            options={
                "verbose_name": "unité de mesure",
                "db_table": "unite_mesure",
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            ("type_unite__in", ("MASSE", "VOLUME", "LONGUEUR", "UNITE", "SURFACE"))
                        ),
                        name="ck_unite_mesure_type_unite",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Conditionnement",
            fields=[
                (
                    "pk",
                    models.CompositePrimaryKey(
                        "article_id",
                        "unite_mesure_id",
                        blank=True,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("id_conditionnement", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("facteur_conversion", models.DecimalField(decimal_places=3, max_digits=14)),
                (
                    "article",
                    models.ForeignKey(
                        db_column="article_id_article",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conditionnements",
                        to="referentiels.article",
                    ),
                ),
                (
                    "unite_mesure",
                    models.ForeignKey(
                        db_column="unite_mesure_code_unite",
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conditionnements",
                        to="referentiels.unitemesure",
                    ),
                ),
            ],
            options={
                "verbose_name": "conditionnement",
                "db_table": "conditionnement",
            },
        ),
        migrations.AddField(
            model_name="article",
            name="unite_mesure",
            field=models.ForeignKey(
                db_column="unite_mesure_code_unite",
                db_index=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="articles",
                to="referentiels.unitemesure",
            ),
        ),
        migrations.AddIndex(
            model_name="gamme",
            index=models.Index(fields=["type_logement"], name="ix_gamme_type_logement_code_type"),
        ),
        migrations.AddConstraint(
            model_name="gamme",
            constraint=models.CheckConstraint(
                condition=models.Q(("statut__in", ("BROUILLON", "ACTIVE", "ARCHIVEE"))),
                name="ck_gamme_statut",
            ),
        ),
        migrations.AddIndex(
            model_name="etapemodele",
            index=models.Index(fields=["gamme"], name="ix_etape_modele_gamme_id_gamme"),
        ),
        migrations.AddIndex(
            model_name="etapemodele",
            index=models.Index(
                fields=["corps_etat"], name="ix_etape_modele_corps_etat_code_corps_etat"
            ),
        ),
        migrations.AddConstraint(
            model_name="etapemodele",
            constraint=models.UniqueConstraint(fields=("code",), name="uq_etape_modele_code"),
        ),
        migrations.AddIndex(
            model_name="article",
            index=models.Index(
                fields=["categorie_article"], name="ix_article_categorie_article_code_categorie"
            ),
        ),
        migrations.AddIndex(
            model_name="article",
            index=models.Index(fields=["unite_mesure"], name="ix_article_unite_mesure_code_unite"),
        ),
        migrations.AddConstraint(
            model_name="article",
            constraint=models.UniqueConstraint(fields=("code",), name="uq_article_code"),
        ),
        migrations.AddConstraint(
            model_name="article",
            constraint=models.UniqueConstraint(
                fields=("code_barre",), name="uq_article_code_barre"
            ),
        ),
        migrations.AddConstraint(
            model_name="article",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("origine__in", ("ACHAT", "PRODUCTION_INTERNE", "RECUPERATION"))
                ),
                name="ck_article_origine",
            ),
        ),
    ]
