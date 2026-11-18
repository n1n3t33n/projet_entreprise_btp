"""Identité 0003 — journal d'audit immuable et partitionné par mois.

Références : MPD-1 table ``journal_audit`` « partitionnée par mois » et
contrainte ``IMMUABLE trg_journal_audit_immuable`` ; RG-S8 ; RG-D9 ;
README de modélisation § 6.5 ; rapport B0 § 4.4-4.5 ; arbitrage Q4.

Django ne sait ni partitionner une table ni poser un déclencheur : la table
est donc créée en SQL, tandis que l'état des modèles de Django reçoit la
définition équivalente (``SeparateDatabaseAndState``). Conséquence assumée :
toute évolution future de cette table s'écrira, elle aussi, à la main.

Ce que pose la partie SQL :
  1. la table parente, partitionnée par RANGE sur ``horodatage`` ; clé
     primaire composite (id_entree, horodatage) imposée par PostgreSQL ;
  2. l'index ``ix_journal_audit_utilisateur_id_utilisateur`` (MPD-1),
     propagé à chaque partition ;
  3. ``trg_journal_audit_immuable`` : BEFORE UPDATE OR DELETE, par ligne,
     cloné automatiquement sur chaque partition (PostgreSQL ≥ 13) ;
  4. ``trg_journal_audit_tronquer`` : BEFORE TRUNCATE, par instruction, sur
     le parent ; chaque partition reçoit le sien à sa création ;
  5. droits : SELECT et INSERT seulement pour le rôle applicatif (le droit
     par défaut UPDATE/DELETE posé par socle 0001 est retiré ici) ;
  6. partitions initiales : le mois précédent, le mois courant et
     ``PARTITIONS_MOIS_AVANCE`` mois futurs.

Retour arrière : suppression de la table et de toutes ses partitions. À ne
jamais faire en production sur un journal contenant des entrées réelles.
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

CREATION_TABLE = """
CREATE TABLE journal_audit (
    id_entree uuid NOT NULL,
    action varchar(120) NOT NULL,
    type_objet varchar(120) NOT NULL,
    horodatage timestamptz NOT NULL,
    adresse_ip varchar(120) NULL,
    utilisateur_id_utilisateur uuid NOT NULL
        CONSTRAINT journal_audit_utilisateur_fk
        REFERENCES utilisateur (id_utilisateur) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT journal_audit_pkey PRIMARY KEY (id_entree, horodatage)
) PARTITION BY RANGE (horodatage);

CREATE INDEX ix_journal_audit_utilisateur_id_utilisateur
    ON journal_audit (utilisateur_id_utilisateur);

CREATE TRIGGER trg_journal_audit_immuable
    BEFORE UPDATE OR DELETE ON journal_audit
    FOR EACH ROW EXECUTE FUNCTION socle_rejeter_modification();

CREATE TRIGGER trg_journal_audit_tronquer
    BEFORE TRUNCATE ON journal_audit
    FOR EACH STATEMENT EXECUTE FUNCTION socle_rejeter_modification();
"""

SUPPRESSION_TABLE = "DROP TABLE IF EXISTS journal_audit CASCADE;"


def restreindre_droits_et_partitionner(apps: object, schema_editor: object) -> None:
    """Retire UPDATE/DELETE au rôle applicatif puis crée les partitions."""
    application = role_application()
    executer(schema_editor, sql.SQL("REVOKE ALL ON journal_audit FROM {}").format(application))
    executer(
        schema_editor,
        sql.SQL("GRANT SELECT, INSERT ON journal_audit TO {}").format(application),
    )
    mois = mois_a_couvrir(timezone.localdate(), settings.PARTITIONS_MOIS_AVANCE)
    creer_partitions(schema_editor.connection, ["journal_audit"], mois)  # type: ignore[attr-defined]


class Migration(migrations.Migration):
    dependencies = [
        ("identite", "0002_retrait_index_hors_mpd"),
        ("socle", "0001_fonctions_et_droits"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="JournalAudit",
                    fields=[
                        (
                            "pk",
                            models.CompositePrimaryKey(
                                "id_entree",
                                "horodatage",
                                blank=True,
                                editable=False,
                                primary_key=True,
                                serialize=False,
                            ),
                        ),
                        ("id_entree", models.UUIDField(default=uuid.uuid4, editable=False)),
                        ("action", models.CharField(max_length=120)),
                        ("type_objet", models.CharField(max_length=120)),
                        (
                            "horodatage",
                            models.DateTimeField(default=django.utils.timezone.now),
                        ),
                        (
                            "adresse_ip",
                            models.CharField(blank=True, max_length=120, null=True),
                        ),
                        (
                            "utilisateur",
                            models.ForeignKey(
                                db_column="utilisateur_id_utilisateur",
                                db_index=False,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="entrees_audit",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "entrée du journal d'audit",
                        "db_table": "journal_audit",
                        "indexes": [
                            models.Index(
                                fields=["utilisateur"],
                                name="ix_journal_audit_utilisateur_id_utilisateur",
                            )
                        ],
                    },
                ),
            ],
            database_operations=[
                migrations.RunSQL(sql=CREATION_TABLE, reverse_sql=SUPPRESSION_TABLE),
                migrations.RunPython(restreindre_droits_et_partitionner, migrations.RunPython.noop),
            ],
        ),
    ]
