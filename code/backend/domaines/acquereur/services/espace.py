"""Espace acquéreur en lecture seule (UC-5, EF-ACQ-01, EF-ACQ-02, H1).

La portée est déduite du compte (aucun identifiant transmis par le client,
EF-AUT-02) : le logement de l'acquéreur rattaché (écart Q-AY, RG-D10).

Ce que voit l'acquéreur (Q-BA) : les étapes de son logement, leur date de
franchissement (validation), les pourcentages et la livraison prévue.
Jamais les noms des intervenants, les commentaires ni les motifs ; une
étape bloquée lui apparaît « en cours ».
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from domaines.avancement import selecteurs as selecteurs_avancement
from domaines.avancement.constantes import BLOQUEE, EN_COURS
from domaines.notifications import selecteurs as selecteurs_notifications
from domaines.notifications.constantes import ETAPE_FRANCHIE
from socle.erreurs import ErreurApi

ZERO = Decimal("0.000")


@dataclass(frozen=True)
class EtapeVisible:
    id_etape: Any
    libelle_etape: str
    libelle_corps_etat: str
    couleur_corps_etat: str
    statut: str
    date_franchissement: date | None


@dataclass(frozen=True)
class LogementVisible:
    numero_logement: str
    libelle_zone: str
    libelle_type_logement: str
    pourcentage_valide: Decimal
    pourcentage_declare: Decimal
    date_livraison_prevue: date | None
    etapes: list[EtapeVisible]


@dataclass(frozen=True)
class NotificationVisible:
    id_notification: Any
    libelle_etape: str
    date_franchissement: Any
    lue: bool


def _logement(utilisateur: Any) -> Any:
    acquereur = getattr(utilisateur, "acquereur", None)
    if acquereur is None:
        raise ErreurApi(
            statut=404,
            motif="INTROUVABLE",
            message="Aucun logement n'est rattaché à ce compte.",
        )
    return acquereur.logement


def logement(utilisateur: Any) -> LogementVisible:
    lieu = _logement(utilisateur)
    agregat = selecteurs_avancement.agregat_logement(lieu.pk)
    etapes = [
        EtapeVisible(
            id_etape=etape.pk,
            libelle_etape=etape.etape_modele.libelle,
            libelle_corps_etat=etape.etape_modele.corps_etat.libelle,
            couleur_corps_etat=etape.etape_modele.corps_etat.couleur,
            statut=EN_COURS if etape.statut == BLOQUEE else etape.statut,
            date_franchissement=etape.date_validation.date() if etape.date_validation else None,
        )
        for etape in selecteurs_avancement.etapes_du_logement(lieu.pk)
    ]
    return LogementVisible(
        numero_logement=lieu.numero,
        libelle_zone=lieu.zone.nom,
        libelle_type_logement=lieu.type_logement.libelle,
        pourcentage_valide=agregat.pourcentage_valide if agregat else ZERO,
        pourcentage_declare=agregat.pourcentage_declare if agregat else ZERO,
        date_livraison_prevue=lieu.date_livraison_prevue,
        etapes=etapes,
    )


def notifications(utilisateur: Any) -> list[NotificationVisible]:
    """Les étapes franchies annoncées à l'acquéreur, les plus récentes
    d'abord ; elles se marquent lues par POST /api/notifications/{id}/lecture."""
    lieu = _logement(utilisateur)
    libelles = {
        str(etape.pk): etape.etape_modele.libelle
        for etape in selecteurs_avancement.etapes_du_logement(lieu.pk)
    }
    return [
        NotificationVisible(
            id_notification=notification.pk,
            libelle_etape=libelles.get(str(notification.id_objet), ""),
            date_franchissement=notification.date_creation,
            lue=notification.date_lecture is not None,
        )
        for notification in selecteurs_notifications.de(utilisateur).filter(
            type_notification_id=ETAPE_FRANCHIE
        )
    ]
