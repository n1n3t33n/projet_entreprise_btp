"""Décision sur un mouvement à valider (EF-STK-09, RG-S6, RG-D8, RG-D11).

ET-2 : un mouvement « à valider » ou « en alerte » reçoit une décision
ACCEPTE ou REFUSE, inscrite dans ``evenement_validation`` (immuable) ; le
mouvement lui-même ne change jamais (RG-S8). Un refus ne remet pas le stock
en place : la sortie a bien eu lieu physiquement ; la correction, si elle est
justifiée, passe par un contre-mouvement (annulation.py).

Séparation des tâches : celui qui a saisi le mouvement ne peut pas le valider
(RG-D8) ; le contrôle porte sur l'auteur de l'événement (RG-D11, extension non
ratifiée de RG-D8, à tracer en v0.2).

Concurrence : deux décisions simultanées sur le même mouvement sont
sérialisées par un verrou consultatif PostgreSQL ; un ``SELECT … FOR UPDATE``
est impossible, le rôle applicatif n'ayant pas le droit UPDATE sur ce journal.
"""

from typing import Any
from uuid import UUID

from django.db import connection, transaction
from django.utils import timezone

from domaines.referentiels.models import RegleValidation
from domaines.stock import selecteurs
from domaines.stock.constantes import (
    DECISION_REFUSE,
    EVENEMENT_ECART_INVENTAIRE,
    EVENEMENT_MOUVEMENT,
    OBJET_MOUVEMENT,
    STATUT_A_VALIDER,
    STATUT_EN_ALERTE,
)
from domaines.stock.models import EvenementValidation, MouvementStock
from domaines.stock.services import (
    acces,
    inventaires,
    parametres,
    publications,
    regles,
    relance,
)
from socle.api_outils import conflit, donnee_invalide
from socle.erreurs import ErreurApi
from socle.journalisation import contexte


def verrouiller_mouvement(uuid_mouvement: Any) -> None:
    """Verrou consultatif propre à un mouvement, libéré en fin de transaction."""
    with connection.cursor() as curseur:
        curseur.execute(
            "SELECT pg_advisory_xact_lock(hashtext(%s))", [f"mouvement:{uuid_mouvement}"]
        )


def mouvement_autorise(utilisateur: Any, uuid_mouvement: Any, action: str) -> MouvementStock:
    """Le mouvement (annoté pour le statut dérivé) s'il est dans la
    couverture du droit ; sinon 404."""
    couverts = acces.magasins_couverts(utilisateur, "mouvements", action)
    mouvement = selecteurs.mouvements(couverts).filter(uuid=uuid_mouvement).first()
    if mouvement is None:
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Ce mouvement est introuvable.")
    return mouvement


def _regle(mouvement: MouvementStock) -> RegleValidation | None:
    """Règle qui a soumis le mouvement à validation, recalculée (le MPD la
    relie à l'événement, pas au mouvement). Un ajustement d'inventaire relève
    de la règle ECART_INVENTAIRE (RG-S9)."""
    if mouvement.ligne_inventaire_id:
        return regles.premiere_regle(EVENEMENT_ECART_INVENTAIRE)
    return regles.regle_declenchee(EVENEMENT_MOUVEMENT, {"quantite_base": mouvement.quantite_base})


@transaction.atomic
def decider(
    valideur: Any,
    uuid_mouvement: Any,
    decision: str,
    motif: str | None,
    uuid_evenement: UUID | None = None,
) -> MouvementStock:
    if uuid_evenement is not None:
        deja = EvenementValidation.objects.filter(uuid=uuid_evenement).first()
        if deja is not None:  # rejeu d'une décision déjà reçue (I-17)
            return mouvement_autorise(valideur, deja.mouvement_stock_id, "VALIDER")
    verrouiller_mouvement(uuid_mouvement)
    mouvement = mouvement_autorise(valideur, uuid_mouvement, "VALIDER")
    delai = parametres.delai_relance_h(mouvement.magasin.chantier_id)
    statut = selecteurs.statut_derive(mouvement, delai, timezone.now())
    if statut not in (STATUT_A_VALIDER, STATUT_EN_ALERTE):
        raise conflit("DECISION_IMPOSSIBLE", "Ce mouvement n'attend pas de décision.")
    if mouvement.utilisateur_id == valideur.pk:
        raise ErreurApi(
            statut=403,
            motif="SEPARATION_DES_TACHES",
            message="Vous avez saisi ce mouvement : une autre personne doit le valider.",
        )
    if mouvement.ligne_inventaire_id:
        # Double validation d'un écart d'inventaire (RG-S9) : le compteur est
        # exclu lui aussi (RG-D11).
        inventaires.controler_valideur(mouvement.ligne_inventaire_id, valideur)
    if decision == DECISION_REFUSE and not motif:
        raise donnee_invalide("motif", "Indiquez le motif du refus.")
    valeurs: dict[str, Any] = {
        "type_objet": OBJET_MOUVEMENT,
        "decision": decision,
        "motif": motif or None,
        "mouvement_stock": mouvement,
        "regle_validation": _regle(mouvement),
        "utilisateur": valideur,
    }
    if uuid_evenement is not None:
        valeurs["uuid"] = uuid_evenement
    EvenementValidation.objects.create(**valeurs, **contexte.champs_appareil())
    relance.actualiser_alerte(mouvement.stock_courant)
    if decision == DECISION_REFUSE:
        publications.sortie_refusee(mouvement, valideur, motif)
    return mouvement_autorise(valideur, uuid_mouvement, "VALIDER")
