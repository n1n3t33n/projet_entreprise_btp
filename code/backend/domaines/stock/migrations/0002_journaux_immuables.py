"""Stock 0002 — journaux immuables du stock (RG-S8).

Références : MPD-4 tables ``mouvement_stock`` (« partitionnement différé »,
``IMMUABLE trg_mouvement_stock_immuable``) et ``evenement_validation``
(« partitionnée par mois », ``IMMUABLE trg_evenement_validation_immuable``) ;
README de modélisation § 6.5 ; même procédé que ``identite 0003`` pour le
journal d'audit.

1. ``mouvement_stock`` (créée par 0001, NON partitionnée : elle est
   référencée par ``evenement_validation``, son partitionnement est différé
   au MPD) :
   * ``trg_mouvement_stock_immuable`` BEFORE UPDATE OR DELETE, par ligne ;
   * ``trg_mouvement_stock_tronquer`` BEFORE TRUNCATE ;
   * rôle applicatif réduit à SELECT et INSERT.
2. ``evenement_validation`` créée en SQL, partitionnée par RANGE mensuel sur
   ``horodatage_serveur`` ; clé primaire composite (uuid,
   horodatage_serveur) imposée par PostgreSQL ; index du MPD propagés aux
   partitions ; déclencheurs d'immuabilité ; SELECT et INSERT seulement ;
   partitions initiales (mois précédent, courant, ``PARTITIONS_MOIS_AVANCE``
   mois futurs). Les suivantes sont créées par le traitement planifié
   ``creer_partitions`` (le domaine déclare la table dans ``apps.ready``).

Django ne sait ni partitionner ni poser de déclencheur : d'où
``SeparateDatabaseAndState`` pour ``evenement_validation``. Retour arrière :
suppression des déclencheurs et de la table d'événements ; à ne jamais faire
sur des données réelles.
"""

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone
from psycopg import sql

from socle.base_de_donnees.partitions import creer_partitions, mois_a_couvrir
from socle.base_de_donnees.sql import executer, role_application

IMMUABILITE_MOUVEMENT = """
CREATE TRIGGER trg_mouvement_stock_immuable
    BEFORE UPDATE OR DELETE ON mouvement_stock
    FOR EACH ROW EXECUTE FUNCTION socle_rejeter_modification();

CREATE TRIGGER trg_mouvement_stock_tronquer
    BEFORE TRUNCATE ON mouvement_stock
    FOR EACH STATEMENT EXECUTE FUNCTION socle_rejeter_modification();
"""

RETRAIT_IMMUABILITE_MOUVEMENT = """
DROP TRIGGER IF EXISTS trg_mouvement_stock_immuable ON mouvement_stock;
DROP TRIGGER IF EXISTS trg_mouvement_stock_tronquer ON mouvement_stock;
"""

CREATION_EVENEMENT = """
CREATE TABLE evenement_validation (
    uuid uuid NOT NULL,
    type_objet varchar(120) NOT NULL,
    decision varchar(32) NOT NULL
        CONSTRAINT ck_evenement_validation_decision
        CHECK (decision IN ('ACCEPTE', 'REFUSE')),
    motif text NULL,
    horodatage_serveur timestamptz NOT NULL,
    mouvement_stock_uuid uuid NOT NULL
        CONSTRAINT evenement_validation_mouvement_fk
        REFERENCES mouvement_stock (uuid) DEFERRABLE INITIALLY DEFERRED,
    regle_validation_id_regle uuid NULL
        CONSTRAINT evenement_validation_regle_fk
        REFERENCES regle_validation (id_regle) DEFERRABLE INITIALLY DEFERRED,
    utilisateur_id_utilisateur uuid NOT NULL
        CONSTRAINT evenement_validation_utilisateur_fk
        REFERENCES utilisateur (id_utilisateur) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT evenement_validation_pkey PRIMARY KEY (uuid, horodatage_serveur)
) PARTITION BY RANGE (horodatage_serveur);

CREATE INDEX ix_evenement_validation_mouvement_stock_uuid
    ON evenement_validation (mouvement_stock_uuid);
CREATE INDEX ix_evenement_validation_regle_validation_id_regle
    ON evenement_validation (regle_validation_id_regle);
CREATE INDEX ix_evenement_validation_utilisateur_id_utilisateur
    ON evenement_validation (utilisateur_id_utilisateur);

CREATE TRIGGER trg_evenement_validation_immuable
    BEFORE UPDATE OR DELETE ON evenement_validation
    FOR EACH ROW EXECUTE FUNCTION socle_rejeter_modification();

CREATE TRIGGER trg_evenement_validation_tronquer
    BEFORE TRUNCATE ON evenement_validation
    FOR EACH STATEMENT EXECUTE FUNCTION socle_rejeter_modification();
"""

SUPPRESSION_EVENEMENT = "DROP TABLE IF EXISTS evenement_validation CASCADE;"


def restreindre_droits_et_partitionner(apps: object, schema_editor: object) -> None:
    """Réduit le rôle applicatif à SELECT/INSERT sur les deux journaux, puis
    crée les partitions initiales des événements."""
    application = role_application()
    for table in ("mouvement_stock", "evenement_validation"):
        executer(
            schema_editor,
            sql.SQL("REVOKE ALL ON {} FROM {}").format(sql.Identifier(table), application),
        )
        executer(
            schema_editor,
            sql.SQL("GRANT SELECT, INSERT ON {} TO {}").format(sql.Identifier(table), application),
        )
    mois = mois_a_couvrir(timezone.localdate(), settings.PARTITIONS_MOIS_AVANCE)
    creer_partitions(
        schema_editor.connection, ["evenement_validation"], mois  # type: ignore[attr-defined]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("stock", "0001_initial"),
        ("socle", "0001_fonctions_et_droits"),
    ]

    operations = [
        migrations.RunSQL(sql=IMMUABILITE_MOUVEMENT, reverse_sql=RETRAIT_IMMUABILITE_MOUVEMENT),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="EvenementValidation",
                    fields=[
                        (
                            "pk",
                            models.CompositePrimaryKey(
                                "uuid",
                                "horodatage_serveur",
                                blank=True,
                                editable=False,
                                primary_key=True,
                                serialize=False,
                            ),
                        ),
                        ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                        ("type_objet", models.CharField(max_length=120)),
                        ("decision", models.CharField(max_length=32)),
                        ("motif", models.TextField(blank=True, null=True)),
                        (
                            "horodatage_serveur",
                            models.DateTimeField(default=django.utils.timezone.now),
                        ),
                        (
                            "regle_validation",
                            models.ForeignKey(
                                blank=True,
                                db_column="regle_validation_id_regle",
                                db_index=False,
                                null=True,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements_validation",
                                to="referentiels.reglevalidation",
                            ),
                        ),
                        (
                            "utilisateur",
                            models.ForeignKey(
                                db_column="utilisateur_id_utilisateur",
                                db_index=False,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements_validation",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                        (
                            "mouvement_stock",
                            models.ForeignKey(
                                db_column="mouvement_stock_uuid",
                                db_index=False,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements_validation",
                                to="stock.mouvementstock",
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "événement de validation",
                        "db_table": "evenement_validation",
                    },
                ),
                migrations.AddIndex(
                    model_name="evenementvalidation",
                    index=models.Index(
                        fields=["mouvement_stock"],
                        name="ix_evenement_validation_mouvement_stock_uuid",
                    ),
                ),
                migrations.AddIndex(
                    model_name="evenementvalidation",
                    index=models.Index(
                        fields=["regle_validation"],
                        name="ix_evenement_validation_regle_validation_id_regle",
                    ),
                ),
                migrations.AddIndex(
                    model_name="evenementvalidation",
                    index=models.Index(
                        fields=["utilisateur"],
                        name="ix_evenement_validation_utilisateur_id_utilisateur",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="evenementvalidation",
                    constraint=models.CheckConstraint(
                        condition=models.Q(("decision__in", ("ACCEPTE", "REFUSE"))),
                        name="ck_evenement_validation_decision",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(sql=CREATION_EVENEMENT, reverse_sql=SUPPRESSION_EVENEMENT),
            ],
        ),
        migrations.RunPython(restreindre_droits_et_partitionner, migrations.RunPython.noop),
    ]
