"""Cycle de vie des partitions mensuelles des journaux (rapport B0 § 4.5).

Trois journaux du MPD sont partitionnés par mois (RANGE) : journal_audit
(MPD-1, dès B1), evenement_validation (MPD-4, B3) et evenement_execution
(MPD-5, B4). Chaque domaine déclare ses tables partitionnées dans son
``AppConfig.ready`` ; la commande ``creer_partitions`` les parcourt toutes.
Le socle ne connaît ainsi aucun domaine (modularité).

Choix assumés :
  * aucune partition DEFAULT : elle empêcherait de créer plus tard la
    partition d'un mois déjà reçu dans DEFAULT ; une insertion sans partition
    échoue donc franchement, ce qui est voulu (alerte, rejet motivé) ;
  * les partitions sont créées d'avance (``PARTITIONS_MOIS_AVANCE`` mois) au
    déploiement et chaque jour par une tâche planifiée ;
  * la création passe par la fonction SQL ``socle_creer_partition_mensuelle``
    (SECURITY DEFINER, appartenant au propriétaire) : le rôle applicatif peut
    donc lancer la commande sans jamais posséder de table.
"""

from datetime import date

from django.conf import settings
from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.utils import timezone

TABLES_PARTITIONNEES: set[str] = set()


def declarer_table_partitionnee(nom_table: str) -> None:
    """Inscrit une table partitionnée par mois (appelé par les domaines)."""
    TABLES_PARTITIONNEES.add(nom_table)


def premier_du_mois(jour: date) -> date:
    """Ramène une date au premier jour de son mois."""
    return jour.replace(day=1)


def ajouter_mois(jour: date, nombre: int) -> date:
    """Premier jour du mois situé ``nombre`` mois après ``jour``."""
    index = jour.year * 12 + (jour.month - 1) + nombre
    return date(index // 12, index % 12 + 1, 1)


def mois_a_couvrir(aujourd_hui: date, mois_avance: int, mois_passes: int = 1) -> list[date]:
    """Mois dont la partition doit exister : un mois passé (événements
    arrivés en retard), le mois courant et ``mois_avance`` mois futurs."""
    debut = premier_du_mois(aujourd_hui)
    return [ajouter_mois(debut, decalage) for decalage in range(-mois_passes, mois_avance + 1)]


def creer_partitions(
    connexion: BaseDatabaseWrapper, tables: set[str] | list[str], mois: list[date]
) -> list[str]:
    """Crée (si besoin) les partitions des ``tables`` pour chaque ``mois``.

    Idempotent : une partition existante n'est pas recréée, ses droits sont
    simplement réaffirmés. Rend les noms des partitions concernées.
    """
    noms: list[str] = []
    with connexion.cursor() as curseur:
        for table in sorted(tables):
            for premier in mois:
                curseur.execute("SELECT socle_creer_partition_mensuelle(%s, %s)", [table, premier])
                noms.append(curseur.fetchone()[0])
    return noms


def preparer_partitions(mois_avance: int | None = None, alias: str = "default") -> str:
    """Traitement planifié « creer_partitions » (6.5) : prépare les partitions
    de toutes les tables déclarées et rend le bilan inscrit dans
    ``execution_traitement``."""
    avance = settings.PARTITIONS_MOIS_AVANCE if mois_avance is None else mois_avance
    mois = mois_a_couvrir(timezone.localdate(), avance)
    noms = creer_partitions(connections[alias], TABLES_PARTITIONNEES, mois)
    return f"{len(noms)} partition(s) vérifiée(s) : {', '.join(noms)}"
