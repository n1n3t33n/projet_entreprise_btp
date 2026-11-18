"""Cadre des traitements planifiés (exigence 6.5).

Un traitement est une fonction sans argument qui rend un bilan lisible
(« 4 partition(s) vérifiée(s) »). Un domaine le déclare dans son
``apps.ready()`` avec ``declarer_traitement`` ; la tâche planifiée de la
plateforme le lance par ``python manage.py lancer_traitement <nom>``.

Pour chaque passage, ``executer`` :
  * refuse de démarrer si le même traitement tourne déjà (verrou consultatif
    PostgreSQL : le passage quotidien et une étape de publication peuvent se
    chevaucher) ;
  * inscrit une ligne ``execution_traitement`` EN_COURS, puis REUSSI avec le
    bilan, ou ECHEC avec la cause (masquée : jamais de secret) ;
  * envoie une alerte technique en cas d'échec (6.7) et relève l'erreur, pour
    que la plateforme voie un code de sortie non nul.

Contrat d'un traitement : il doit être IDEMPOTENT (le relancer ne produit
pas de double effet) et gérer lui-même ses transactions. Une ligne restée
EN_COURS signale un passage interrompu ; il suffit de relancer.
"""

import logging
from collections.abc import Callable

from django.db import connection
from django.utils import timezone

from socle import alertes
from socle.journalisation.masquage import masquer_texte
from socle.models import (
    STATUT_ECHEC,
    STATUT_REUSSI,
    ExecutionTraitement,
)

journal = logging.getLogger("chantiersync.traitements")

Traitement = Callable[[], str]

TRAITEMENTS: dict[str, Traitement] = {}

LONGUEUR_MAXIMALE_DETAIL = 2000


class TraitementDejaEnCours(Exception):
    """Un autre passage du même traitement n'est pas terminé."""


def declarer_traitement(nom: str, fonction: Traitement) -> None:
    """Appelé par un domaine au démarrage. Redéclarer remplace."""
    TRAITEMENTS[nom] = fonction


def _verrouiller(nom: str) -> bool:
    with connection.cursor() as curseur:
        curseur.execute("SELECT pg_try_advisory_lock(hashtext(%s))", [f"traitement:{nom}"])
        return bool(curseur.fetchone()[0])


def _deverrouiller(nom: str) -> None:
    with connection.cursor() as curseur:
        curseur.execute("SELECT pg_advisory_unlock(hashtext(%s))", [f"traitement:{nom}"])


def executer(nom: str, fonction: Traitement | None = None) -> ExecutionTraitement:
    """Lance le traitement ``nom`` (déclaré, ou ``fonction`` si fournie, pour
    une commande qui passe ses propres options) et trace son passage."""
    a_lancer = fonction or TRAITEMENTS[nom]
    if not _verrouiller(nom):
        raise TraitementDejaEnCours(f"Le traitement « {nom} » est déjà en cours.")
    try:
        execution = ExecutionTraitement.objects.create(nom_traitement=nom)
        try:
            bilan = a_lancer()
        except Exception as erreur:
            cause = masquer_texte(f"{type(erreur).__name__} : {erreur}")[:LONGUEUR_MAXIMALE_DETAIL]
            _clore(execution, STATUT_ECHEC, cause)
            journal.exception("traitement en échec", extra={"nom_traitement": nom, "detail": cause})
            alertes.alerter(
                alertes.TRAITEMENT_EN_ECHEC,
                f"Traitement « {nom} » en échec",
                f"Le traitement « {nom} » a échoué : {cause}\nIl peut être relancé sans risque.",
            )
            raise
        _clore(execution, STATUT_REUSSI, bilan[:LONGUEUR_MAXIMALE_DETAIL])
        journal.info("traitement réussi", extra={"nom_traitement": nom, "detail": bilan})
        return execution
    finally:
        _deverrouiller(nom)


def _clore(execution: ExecutionTraitement, statut: str, detail: str) -> None:
    execution.statut = statut
    execution.detail = detail
    execution.fin = timezone.now()
    execution.save(update_fields=["statut", "detail", "fin"])
