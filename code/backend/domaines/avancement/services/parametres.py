"""Paramètres de chantier lus par le domaine avancement (EF-REF-07).

Comme pour le stock (Q-F, Q-R) : le paramètre du chantier d'abord ; à défaut
une valeur de repli et une alerte technique PARAMETRE_MANQUANT.
"""

from typing import Any

from domaines.avancement.constantes import CLE_TYPE_CYCLE, DEFAUT_TYPE_CYCLE, TYPES_CYCLE
from domaines.organisation import selecteurs as selecteurs_organisation
from socle import alertes


def type_cycle(id_chantier: Any) -> str:
    """Type de cycle des fiches de route du chantier (RG-A7, H9, Q-Z)."""
    parametre = selecteurs_organisation.valeur_parametre(str(id_chantier), CLE_TYPE_CYCLE)
    if parametre is not None and parametre.valeur.strip().upper() in TYPES_CYCLE:
        return parametre.valeur.strip().upper()
    alertes.parametre_manquant(
        id_chantier,
        CLE_TYPE_CYCLE,
        f"Le cycle « {DEFAUT_TYPE_CYCLE} » est appliqué aux fiches de route.",
    )
    return DEFAUT_TYPE_CYCLE
