"""Paramètres de chantier lus par le domaine stock (EF-REF-07).

Règle commune (Q-F, Q-R) : la valeur la plus précise gagne. Le paramètre du
chantier d'abord ; à défaut, la valeur prévue par le cahier des charges ou la
règle de validation, et une alerte technique PARAMETRE_MANQUANT pour que
l'administrateur complète le paramétrage (une alerte par quart d'heure au
plus, socle/alertes.py).
"""

from datetime import datetime
from functools import cache
from typing import Any

from django.utils import timezone

from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.organisation.constantes import CLE_DELAI_RELANCE_VALIDATION
from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.stock.constantes import (
    CLE_DERIVE_HORLOGE_MAX,
    CLE_STOCK_NEGATIF,
    DEFAUT_DERIVE_HORLOGE_MAX_MIN,
    EVENEMENT_MOUVEMENT,
)
from socle import alertes


def _signaler_absence(id_chantier: Any, cle: str, repli: str) -> None:
    alertes.alerter(
        alertes.PARAMETRE_MANQUANT,
        "Paramètre de chantier manquant",
        f"Le paramètre « {cle} » n'est pas défini pour le chantier {id_chantier}. "
        f"{repli} Renseignez-le dans l'écran Paramétrage.",
    )


def entier(id_chantier: Any, cle: str, defaut: int) -> int:
    """Paramètre entier ; valeur du cahier des charges s'il manque."""
    parametre = selecteurs_organisation.valeur_parametre(str(id_chantier), cle)
    if parametre is not None:
        try:
            return int(parametre.valeur)
        except ValueError:
            pass
    _signaler_absence(id_chantier, cle, f"La valeur {defaut} du cahier des charges est appliquée.")
    return defaut


def stock_negatif_autorise(id_chantier: Any) -> bool:
    """RG-S7 : un stock négatif est autorisé (anomalie signalée) sauf si le
    chantier l'interdit explicitement."""
    parametre = selecteurs_organisation.valeur_parametre(str(id_chantier), CLE_STOCK_NEGATIF)
    return parametre is None or parametre.valeur.strip().lower() != "false"


def delai_relance_h(id_chantier: Any) -> int | None:
    """Délai avant relance d'un mouvement sans décision (ET-2, Q-F) :
    paramètre ``delai_relance_validation_h`` du chantier, sinon
    ``delai_heures`` d'une règle MOUVEMENT_STOCK, sinon aucune relance et une
    alerte technique."""
    parametre = selecteurs_organisation.valeur_parametre(
        str(id_chantier), CLE_DELAI_RELANCE_VALIDATION
    )
    if parametre is not None:
        try:
            return int(parametre.valeur)
        except ValueError:
            pass
    regle = (
        selecteurs_referentiels.regles_de(EVENEMENT_MOUVEMENT).exclude(delai_heures=None).first()
    )
    if regle is not None:
        return int(regle.delai_heures)  # type: ignore[arg-type]
    _signaler_absence(
        id_chantier,
        CLE_DELAI_RELANCE_VALIDATION,
        "Aucune règle de validation ne fixe de délai : les mouvements à valider ne sont pas relancés.",
    )
    return None


class ParametresParChantier:
    """Paramètres lus une seule fois par chantier pendant une requête, pour
    servir une liste de mouvements sans relire la base à chaque ligne."""

    def __init__(self) -> None:
        self.maintenant: datetime = timezone.now()
        self.delai_relance_h = cache(delai_relance_h)
        self.derive_max_min = cache(
            lambda id_chantier: entier(
                id_chantier, CLE_DERIVE_HORLOGE_MAX, DEFAUT_DERIVE_HORLOGE_MAX_MIN
            )
        )
