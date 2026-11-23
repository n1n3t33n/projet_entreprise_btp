"""Événements du stock rejouables par lot (EF-SYN-02, SQ-2).

La charge utile est le corps de la route REST correspondante (Q-AE) :
  * ``MOUVEMENT_STOCK`` — corps de ``POST /mouvements`` ; l'``uuid`` de
    l'événement devient celui du mouvement (idempotence, 6.4) ;
  * ``DECISION_MOUVEMENT`` — ``uuid_mouvement`` et corps de
    ``POST /mouvements/{uuid}/validation`` ; l'``uuid`` de l'événement devient
    celui de l'événement de validation.
Déclarés par ``stock/apps.py`` auprès de ``socle/synchronisation.py``.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from domaines.stock.api import entrees
from domaines.stock.api import serialiseurs as s
from domaines.stock.models import EvenementValidation
from domaines.stock.services import mouvements, validation
from domaines.synchronisation.constantes import ECART_QUANTITE
from socle.synchronisation import Traitement, TypeEvenement


def _valider(classe: Any, donnees: Any) -> dict[str, Any]:
    entree = classe(data=donnees)
    entree.is_valid(raise_exception=True)
    return dict(entree.validated_data)


def mouvement(
    utilisateur: Any, uuid: UUID, horodatage: datetime | None, charge: dict[str, Any]
) -> Traitement:
    corps = {**charge, "uuid": str(uuid)}
    if horodatage is not None and "horodatage_appareil" not in charge:
        corps["horodatage_appareil"] = horodatage.isoformat()
    donnees = _valider(s.MouvementEntreeSerializer, corps)
    inscrit, cree = mouvements.enregistrer(
        utilisateur, entrees.saisie_mouvement(utilisateur, donnees)
    )
    anomalies: tuple[tuple[str, str], ...] = ()
    inscrit.stock_courant.refresh_from_db()
    if cree and inscrit.stock_courant.quantite < 0:
        article = inscrit.article
        anomalies = (
            (
                ECART_QUANTITE,
                f"Stock négatif après synchronisation : {article.designation} "
                f"({article.code}) à {inscrit.stock_courant.quantite} au magasin "
                f"{inscrit.magasin.code}.",
            ),
        )
    return Traitement(cree=cree, anomalies=anomalies)


def decision(
    utilisateur: Any, uuid: UUID, horodatage: datetime | None, charge: dict[str, Any]
) -> Traitement:
    donnees = _valider(s.DecisionEntreeSerializer, {**charge, "uuid": str(uuid)})
    deja = EvenementValidation.objects.filter(uuid=uuid).exists()
    validation.decider(
        utilisateur, charge.get("uuid_mouvement"), donnees["decision"], donnees.get("motif"), uuid
    )
    return Traitement(cree=not deja)


TYPES = (
    TypeEvenement("MOUVEMENT_STOCK", mouvement, "mouvements", "CREER"),
    TypeEvenement("DECISION_MOUVEMENT", decision, "mouvements", "VALIDER"),
)
