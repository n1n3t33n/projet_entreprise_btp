"""Réception d'un lot de synchronisation (SQ-2, EF-SYN-01 à 06, ET-3).

Le téléphone envoie, dans l'ordre de saisie (Q-AG), les événements faits hors
ligne. Chaque événement est rejoué par le service du domaine qui en est
propriétaire, déclaré dans ``socle/synchronisation.py`` : la synchronisation
ne réécrit aucune règle métier (Q-AE).

  * un événement est traité dans son propre point de reprise : un rejet
    n'annule ni ne bloque les autres (Q-AF, EF-SYN-06) ;
  * l'identifiant de l'événement garantit qu'il n'est jamais appliqué deux
    fois : un événement déjà reçu (par un lot ou par la route REST) répond
    « déjà reçu » (ET-3) ; un événement rejeté peut être renvoyé ;
  * un lot renvoyé avec le même identifiant rend les résultats enregistrés,
    sans rien retraiter (Q-AH).
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from domaines.identite.models import Appareil
from domaines.identite.services import appareils as service_appareils
from domaines.identite.services.droits import a_le_droit
from domaines.synchronisation.constantes import ACCEPTE, DEJA_RECU, REJETE
from domaines.synchronisation.models import LotSynchronisation, ResultatEvenement
from domaines.synchronisation.services import anomalies
from socle.api_outils import conflit
from socle.erreurs import ErreurApi
from socle.synchronisation import TYPES

journal = logging.getLogger(__name__)

MESSAGE_DONNEES = "Certaines informations de l'opération sont manquantes ou incorrectes."
MESSAGE_ERREUR = "L'opération n'a pas pu être enregistrée. Elle pourra être renvoyée."


@dataclass(frozen=True)
class EvenementRecu:
    uuid: UUID
    type: str
    charge_utile: dict[str, Any]
    horodatage_appareil: datetime | None = None


@dataclass(frozen=True)
class Envoi:
    id_lot: UUID
    evenements: tuple[EvenementRecu, ...]
    horodatage_envoi: datetime | None = None


@dataclass(frozen=True)
class _Issue:
    statut: str
    code_rejet: str | None = None
    motif_rejet: str | None = None
    anomalies: tuple[tuple[str, str], ...] = ()


def recevoir(utilisateur: Any, appareil: Appareil, envoi: Envoi) -> tuple[LotSynchronisation, bool]:
    """Rend (lot, nouveau ?). Un lot connu d'un autre appareil est refusé."""
    deja = _lot_existant(appareil, envoi.id_lot)
    if deja is not None:
        return deja, False
    debut = time.monotonic()
    try:
        with transaction.atomic():
            lot = LotSynchronisation.objects.create(pk=envoi.id_lot, appareil=appareil)
    except IntegrityError:  # envoi simultané du même lot
        existant = _lot_existant(appareil, envoi.id_lot)
        if existant is None:
            raise
        return existant, False
    acceptes = rejetes = 0
    for evenement in envoi.evenements:
        issue = _traiter(utilisateur, evenement)
        _enregistrer(lot, appareil, evenement, issue)
        if issue.statut == REJETE:
            rejetes += 1
        else:
            acceptes += 1
    lot.nombre_evenements = len(envoi.evenements)
    lot.nombre_acceptes = acceptes
    lot.nombre_rejetes = rejetes
    lot.duree_ms = int((time.monotonic() - debut) * 1000)
    lot.save(update_fields=["nombre_evenements", "nombre_acceptes", "nombre_rejetes", "duree_ms"])
    anomalies.verifier_horloge(appareil, envoi.horodatage_envoi)
    service_appareils.marquer_synchronisation(appareil)
    return lot, True


def _lot_existant(appareil: Appareil, id_lot: UUID) -> LotSynchronisation | None:
    lot = LotSynchronisation.objects.filter(pk=id_lot).first()
    if lot is not None and lot.appareil_id != appareil.pk:
        raise conflit("LOT_DEJA_UTILISE", "Cet identifiant de lot est déjà utilisé.")
    return lot


def _traiter(utilisateur: Any, evenement: EvenementRecu) -> _Issue:
    type_evenement = TYPES.get(evenement.type)
    if type_evenement is None:
        return _Issue(REJETE, "TYPE_INCONNU", f"Type d'opération inconnu : {evenement.type}.")
    if not a_le_droit(utilisateur, "api", type_evenement.ressource, type_evenement.action):
        return _Issue(
            REJETE, "DROIT_INSUFFISANT", "Vous n'avez pas le droit d'effectuer cette opération."
        )
    try:
        with transaction.atomic():
            traitement = type_evenement.traiter(
                utilisateur, evenement.uuid, evenement.horodatage_appareil, evenement.charge_utile
            )
    except ErreurApi as erreur:
        return _Issue(REJETE, erreur.motif, erreur.message)
    except ValidationError:
        return _Issue(REJETE, "DONNEES_INVALIDES", MESSAGE_DONNEES)
    except Exception:  # un événement défaillant ne fait pas échouer le lot (EF-SYN-06)
        journal.exception("Échec inattendu de l'événement %s (%s)", evenement.uuid, evenement.type)
        return _Issue(REJETE, "ERREUR_INTERNE", MESSAGE_ERREUR)
    return _Issue(ACCEPTE if traitement.cree else DEJA_RECU, anomalies=traitement.anomalies)


def _enregistrer(
    lot: LotSynchronisation, appareil: Appareil, evenement: EvenementRecu, issue: _Issue
) -> None:
    resultat = ResultatEvenement.objects.create(
        lot_synchronisation=lot,
        uuid_evenement=evenement.uuid,
        statut=issue.statut,
        code_rejet=issue.code_rejet,
        motif_rejet=issue.motif_rejet,
    )
    if issue.statut == REJETE:
        anomalies.signaler_rejet(appareil, resultat)
    for type_anomalie, description in issue.anomalies:
        anomalies.signaler(appareil, type_anomalie, description, resultat)
