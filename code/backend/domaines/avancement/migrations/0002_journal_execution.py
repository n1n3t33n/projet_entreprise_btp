"""Avancement 0002 — journal d'exécution immuable et partitionné (RG-A5).

Références : MPD-5 table ``evenement_execution`` (« partitionnée par mois »,
``IMMUABLE trg_evenement_execution_immuable``) ; README de modélisation
§ 6.5 ; même procédé que ``identite 0003`` et ``stock 0002``.

Partition par RANGE mensuel sur ``horodatage_serveur`` (arbitrage Q-U, I-16 :
l'heure du téléphone peut être fausse ou arriver très en retard ; elle reste
conservée dans ``horodatage_appareil``). Clé primaire composite (uuid,
horodatage_serveur) imposée par PostgreSQL ; aucune clé étrangère ne vise
cette table. Déclencheurs UPDATE/DELETE/TRUNCATE ; rôle applicatif réduit à
SELECT et INSERT ; partitions initiales, puis traitement ``creer_partitions``.

Écart Q-W : colonne ``pour_le_compte_de_id_utilisateur`` et son index.
Retour arrière : suppression de la table ; jamais sur des données réelles.
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

STATUTS = "('A_FAIRE', 'EN_COURS', 'TERMINEE_DECLAREE', 'BLOQUEE', 'VALIDEE')"

CREATION = f"""
CREATE TABLE evenement_execution (
    uuid uuid NOT NULL,
    statut_avant varchar(32) NULL
        CONSTRAINT ck_evenement_execution_statut_avant CHECK (statut_avant IN {STATUTS}),
    statut_apres varchar(32) NOT NULL
        CONSTRAINT ck_evenement_execution_statut_apres CHECK (statut_apres IN {STATUTS}),
    horodatage_appareil timestamptz NOT NULL,
    horodatage_serveur timestamptz NOT NULL,
    commentaire varchar(120) NULL,
    etape_travaux_id_etape uuid NOT NULL
        CONSTRAINT evenement_execution_etape_fk
        REFERENCES etape_travaux (id_etape) DEFERRABLE INITIALLY DEFERRED,
    utilisateur_id_utilisateur uuid NOT NULL
        CONSTRAINT evenement_execution_utilisateur_fk
        REFERENCES utilisateur (id_utilisateur) DEFERRABLE INITIALLY DEFERRED,
    pour_le_compte_de_id_utilisateur uuid NULL
        CONSTRAINT evenement_execution_pour_le_compte_de_fk
        REFERENCES utilisateur (id_utilisateur) DEFERRABLE INITIALLY DEFERRED,
    motif_blocage_code_motif varchar(32) NULL
        CONSTRAINT evenement_execution_motif_fk
        REFERENCES motif_blocage (code_motif) DEFERRABLE INITIALLY DEFERRED,
    article_id_article uuid NULL
        CONSTRAINT evenement_execution_article_fk
        REFERENCES article (id_article) DEFERRABLE INITIALLY DEFERRED,
    avancement_agrege_id_avancement uuid NOT NULL
        CONSTRAINT evenement_execution_avancement_fk
        REFERENCES avancement_agrege (id_avancement) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT evenement_execution_pkey PRIMARY KEY (uuid, horodatage_serveur)
) PARTITION BY RANGE (horodatage_serveur);

CREATE INDEX ix_evenement_execution_etape_travaux_id_etape
    ON evenement_execution (etape_travaux_id_etape);
CREATE INDEX ix_evenement_execution_utilisateur_id_utilisateur
    ON evenement_execution (utilisateur_id_utilisateur);
CREATE INDEX ix_evenement_execution_motif_blocage_code_motif
    ON evenement_execution (motif_blocage_code_motif);
CREATE INDEX ix_evenement_execution_article_id_article
    ON evenement_execution (article_id_article);
CREATE INDEX ix_evenement_execution_avancement_agrege_id_avancement
    ON evenement_execution (avancement_agrege_id_avancement);
CREATE INDEX ix_evenement_execution_pour_le_compte_de_id_utilisateur
    ON evenement_execution (pour_le_compte_de_id_utilisateur);

CREATE TRIGGER trg_evenement_execution_immuable
    BEFORE UPDATE OR DELETE ON evenement_execution
    FOR EACH ROW EXECUTE FUNCTION socle_rejeter_modification();

CREATE TRIGGER trg_evenement_execution_tronquer
    BEFORE TRUNCATE ON evenement_execution
    FOR EACH STATEMENT EXECUTE FUNCTION socle_rejeter_modification();
"""

SUPPRESSION = "DROP TABLE IF EXISTS evenement_execution CASCADE;"


def restreindre_droits_et_partitionner(apps: object, schema_editor: object) -> None:
    application = role_application()
    executer(
        schema_editor, sql.SQL("REVOKE ALL ON evenement_execution FROM {}").format(application)
    )
    executer(
        schema_editor,
        sql.SQL("GRANT SELECT, INSERT ON evenement_execution TO {}").format(application),
    )
    mois = mois_a_couvrir(timezone.localdate(), settings.PARTITIONS_MOIS_AVANCE)
    creer_partitions(
        schema_editor.connection, ["evenement_execution"], mois  # type: ignore[attr-defined]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("avancement", "0001_initial"),
        ("socle", "0001_fonctions_et_droits"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="EvenementExecution",
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
                        ("statut_avant", models.CharField(blank=True, max_length=32, null=True)),
                        ("statut_apres", models.CharField(max_length=32)),
                        (
                            "horodatage_appareil",
                            models.DateTimeField(default=django.utils.timezone.now),
                        ),
                        (
                            "horodatage_serveur",
                            models.DateTimeField(default=django.utils.timezone.now),
                        ),
                        ("commentaire", models.CharField(blank=True, max_length=120, null=True)),
                        (
                            "article",
                            models.ForeignKey(
                                blank=True,
                                db_column="article_id_article",
                                db_index=False,
                                null=True,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements_execution",
                                to="referentiels.article",
                            ),
                        ),
                        (
                            "avancement_agrege",
                            models.ForeignKey(
                                db_column="avancement_agrege_id_avancement",
                                db_index=False,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements",
                                to="avancement.avancementagrege",
                            ),
                        ),
                        (
                            "etape_travaux",
                            models.ForeignKey(
                                db_column="etape_travaux_id_etape",
                                db_index=False,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements",
                                to="avancement.etapetravaux",
                            ),
                        ),
                        (
                            "motif_blocage",
                            models.ForeignKey(
                                blank=True,
                                db_column="motif_blocage_code_motif",
                                db_index=False,
                                null=True,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements_execution",
                                to="referentiels.motifblocage",
                            ),
                        ),
                        (
                            "pour_le_compte_de",
                            models.ForeignKey(
                                blank=True,
                                db_column="pour_le_compte_de_id_utilisateur",
                                db_index=False,
                                null=True,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements_delegues",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                        (
                            "utilisateur",
                            models.ForeignKey(
                                db_column="utilisateur_id_utilisateur",
                                db_index=False,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="evenements_execution",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "événement d'exécution",
                        "db_table": "evenement_execution",
                    },
                ),
                migrations.AddIndex(
                    model_name="evenementexecution",
                    index=models.Index(
                        fields=["etape_travaux"],
                        name="ix_evenement_execution_etape_travaux_id_etape",
                    ),
                ),
                migrations.AddIndex(
                    model_name="evenementexecution",
                    index=models.Index(
                        fields=["utilisateur"],
                        name="ix_evenement_execution_utilisateur_id_utilisateur",
                    ),
                ),
                migrations.AddIndex(
                    model_name="evenementexecution",
                    index=models.Index(
                        fields=["motif_blocage"],
                        name="ix_evenement_execution_motif_blocage_code_motif",
                    ),
                ),
                migrations.AddIndex(
                    model_name="evenementexecution",
                    index=models.Index(
                        fields=["article"], name="ix_evenement_execution_article_id_article"
                    ),
                ),
                migrations.AddIndex(
                    model_name="evenementexecution",
                    index=models.Index(
                        fields=["avancement_agrege"],
                        name="ix_evenement_execution_avancement_agrege_id_avancement",
                    ),
                ),
                migrations.AddIndex(
                    model_name="evenementexecution",
                    index=models.Index(
                        fields=["pour_le_compte_de"],
                        name="ix_evenement_execution_pour_le_compte_de_id_utilisateur",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="evenementexecution",
                    constraint=models.CheckConstraint(
                        condition=models.Q(
                            (
                                "statut_avant__in",
                                ("A_FAIRE", "EN_COURS", "TERMINEE_DECLAREE", "BLOQUEE", "VALIDEE"),
                            ),
                            ("statut_avant__isnull", True),
                            _connector="OR",
                        ),
                        name="ck_evenement_execution_statut_avant",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="evenementexecution",
                    constraint=models.CheckConstraint(
                        condition=models.Q(
                            (
                                "statut_apres__in",
                                ("A_FAIRE", "EN_COURS", "TERMINEE_DECLAREE", "BLOQUEE", "VALIDEE"),
                            )
                        ),
                        name="ck_evenement_execution_statut_apres",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(sql=CREATION, reverse_sql=SUPPRESSION),
            ],
        ),
        migrations.RunPython(restreindre_droits_et_partitionner, migrations.RunPython.noop),
    ]
