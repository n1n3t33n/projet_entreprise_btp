"""Portée organisationnelle d'un droit : quels chantiers et quels magasins.

``ADroit`` dit si un utilisateur détient une permission ; ``droits.couverture``
dit si elle vaut pour tout le programme ou pour des périmètres. Ce module
traduit ces périmètres en chantiers et en magasins (MPD-1 ``perimetre`` : un
périmètre vise un chantier, ou un magasin). Les domaines métier s'en servent
pour filtrer ce qu'ils servent (stock par magasin, avancement par chantier).
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from domaines.identite.selecteurs import perimetres as selecteur_perimetres
from domaines.identite.services import droits


@dataclass(frozen=True)
class Portee:
    """``tout`` : droit de portée GLOBALE ; sinon les chantiers et magasins
    nommés par les périmètres de l'utilisateur."""

    tout: bool
    chantiers: frozenset[UUID] = field(default_factory=frozenset)
    magasins: frozenset[UUID] = field(default_factory=frozenset)


def portee(utilisateur: Any, module: str, ressource: str, action: str) -> Portee:
    couverture = droits.couverture(utilisateur, module, ressource, action)
    if couverture is droits.TOUT_LE_PROGRAMME:
        return Portee(tout=True)
    perimetres = couverture if isinstance(couverture, frozenset) else frozenset()
    chantiers: set[UUID] = set()
    magasins: set[UUID] = set()
    for id_chantier, id_magasin in selecteur_perimetres.portees(perimetres):
        if id_magasin is not None:
            magasins.add(id_magasin)
        elif id_chantier is not None:
            chantiers.add(id_chantier)
    return Portee(tout=False, chantiers=frozenset(chantiers), magasins=frozenset(magasins))
