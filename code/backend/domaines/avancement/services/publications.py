"""Événements de l'avancement annoncés aux autres domaines
(socle/evenements.py, I-19). Codes : ETAPE_A_CONTROLER, ETAPE_REJETEE,
ETAPE_BLOQUEE, MANQUE_MATERIEL, ETAPE_EN_RETARD."""

from typing import Any

from domaines.avancement.models import EtapeTravaux
from socle.evenements import EvenementMetier, publier

ETAPE_A_CONTROLER = "ETAPE_A_CONTROLER"
ETAPE_REJETEE = "ETAPE_REJETEE"
ETAPE_BLOQUEE = "ETAPE_BLOQUEE"
MANQUE_MATERIEL = "MANQUE_MATERIEL"
ETAPE_EN_RETARD = "ETAPE_EN_RETARD"
ETAPE_FRANCHIE = "ETAPE_FRANCHIE"


def _publier(code: str, etape: EtapeTravaux, **champs: Any) -> None:
    contexte = {
        "etape": etape.etape_modele.libelle,
        "logement": etape.logement.numero,
        "date_prevue": etape.date_prevue.strftime("%d/%m/%Y") if etape.date_prevue else "",
        **champs.pop("contexte", {}),
    }
    publier(
        EvenementMetier(
            code=code,
            id_objet=etape.pk,
            id_chantier=etape.logement.zone.chantier_id,
            id_logement=etape.logement_id,
            contexte=contexte,
            **champs,
        )
    )


def a_controler(etape: EtapeTravaux, auteur: Any) -> None:
    _publier(ETAPE_A_CONTROLER, etape, auteur=auteur, contexte={"auteur": auteur.nom_complet})


def rejetee(etape: EtapeTravaux, valideur: Any, declarant: Any, motif: str) -> None:
    _publier(ETAPE_REJETEE, etape, auteur=valideur, personne=declarant, contexte={"motif": motif})


def bloquee(etape: EtapeTravaux, auteur: Any, motif: str, article: Any = None) -> None:
    _publier(ETAPE_BLOQUEE, etape, auteur=auteur, contexte={"motif": motif})
    if article is not None:
        _publier(MANQUE_MATERIEL, etape, auteur=auteur, contexte={"article": article.designation})


def en_retard(etape: EtapeTravaux) -> None:
    """Un seul avis par étape (Q-AU), quel que soit le nombre de passages."""
    _publier(ETAPE_EN_RETARD, etape, unique=True)


def franchie(etape: EtapeTravaux) -> None:
    """EF-ACQ-02 : chaque étape validée est annoncée (à l'acquéreur du
    logement, selon les abonnements)."""
    _publier(ETAPE_FRANCHIE, etape)
