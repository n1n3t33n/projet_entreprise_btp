"""Contrôle d'accès par magasin.

``ADroit`` vérifie qu'un utilisateur détient une permission ; ce module
vérifie en plus QUEL magasin elle couvre. Un droit de portée GLOBALE couvre
tout le programme ; un droit de portée PERIMETRE couvre les magasins de ses
périmètres : un périmètre de chantier couvre tous les magasins du chantier,
un périmètre de magasin ce seul magasin (EF-AUT-02, MPD-1 ``perimetre``).
Un magasin hors couverture répond 404 : on ne révèle pas son existence.
"""

from typing import Any
from uuid import UUID

from domaines.identite.constantes import MODULE_API
from domaines.identite.services import portee
from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.organisation.models import Magasin
from socle.erreurs import ErreurApi


def magasins_couverts(utilisateur: Any, ressource: str, action: str) -> set[UUID] | None:
    """Identifiants des magasins couverts, ou ``None`` pour « tous ». Un
    périmètre de chantier couvre tous les magasins de ce chantier."""
    couverte = portee.portee(utilisateur, MODULE_API, ressource, action)
    if couverte.tout:
        return None
    magasins = set(couverte.magasins)
    if couverte.chantiers:
        magasins |= set(
            selecteurs_organisation.magasins()
            .filter(chantier_id__in=couverte.chantiers)
            .values_list("id_magasin", flat=True)
        )
    return magasins


def magasin_autorise(utilisateur: Any, id_magasin: Any, ressource: str, action: str) -> Magasin:
    """Le magasin demandé, s'il existe et si le droit le couvre ; sinon 404."""
    magasin = selecteurs_organisation.magasins().filter(id_magasin=id_magasin).first()
    couverts = magasins_couverts(utilisateur, ressource, action)
    if magasin is None or (couverts is not None and magasin.pk not in couverts):
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Ce magasin est introuvable.")
    return magasin
