"""Évaluation des règles de validation (EF-REF-08, RG-S6, RG-S9).

Une règle compare un champ (``champ_teste``) à un seuil (``valeur_seuil``)
avec un opérateur. Le domaine stock fournit les valeurs qu'il sait calculer :
pour un mouvement, ``quantite_base`` et ``quantite_saisie`` (RG-S6 : le MPD
n'a pas de prix, un seuil « de valeur » ne peut pas être évalué, Q-M) ; pour
un écart d'inventaire, ``ecart_pourcent`` (RG-S9). Une règle qui teste un
champ inconnu est ignorée et signalée dans les journaux.
"""

import logging
import operator
from collections.abc import Callable
from decimal import Decimal

from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.referentiels.models import RegleValidation

journal = logging.getLogger("chantiersync.stock")

OPERATEURS: dict[str, Callable[[Decimal, Decimal], bool]] = {
    "INFERIEUR_EGAL": operator.le,
    "SUPERIEUR_EGAL": operator.ge,
    "EGAL": operator.eq,
    "INFERIEUR": operator.lt,
    "SUPERIEUR": operator.gt,
}


def regle_declenchee(type_evenement: str, valeurs: dict[str, Decimal]) -> RegleValidation | None:
    """Première règle du type d'événement dont la condition est vraie."""
    for regle in selecteurs_referentiels.regles_de(type_evenement):
        if regle.valeur_seuil is None:
            continue
        comparer = OPERATEURS.get(regle.operateur)
        valeur = valeurs.get(regle.champ_teste)
        if comparer is None or valeur is None:
            journal.warning(
                "règle de validation non évaluable",
                extra={"detail": f"{regle.type_evenement} / {regle.champ_teste}"},
            )
            continue
        if comparer(valeur, regle.valeur_seuil):
            return regle
    return None


def premiere_regle(type_evenement: str) -> RegleValidation | None:
    """Première règle d'un type d'événement, pour la relier à un événement."""
    return selecteurs_referentiels.regles_de(type_evenement).first()
