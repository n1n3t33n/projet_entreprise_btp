"""Contrôle d'accès par chantier.

Un droit de portée GLOBALE couvre tout le programme ; un droit de portée
PERIMETRE couvre les chantiers de ses périmètres (EF-AUT-02). Un périmètre de
magasin ne donne pas accès à l'avancement. Hors couverture : 404, on ne
révèle pas l'existence de l'objet.
"""

from typing import Any
from uuid import UUID

from domaines.avancement.models import EtapeTravaux
from domaines.identite.constantes import MODULE_API
from domaines.identite.services import portee
from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.organisation.models import Logement
from socle.erreurs import ErreurApi


def chantiers_couverts(utilisateur: Any, ressource: str, action: str) -> set[UUID] | None:
    """Identifiants des chantiers couverts, ou ``None`` pour « tous »."""
    couverte = portee.portee(utilisateur, MODULE_API, ressource, action)
    return None if couverte.tout else set(couverte.chantiers)


def _introuvable(message: str) -> ErreurApi:
    return ErreurApi(statut=404, motif="INTROUVABLE", message=message)


def logement_autorise(utilisateur: Any, id_logement: Any, ressource: str, action: str) -> Logement:
    logement = (
        selecteurs_organisation.logements()
        .select_related("zone")
        .filter(id_logement=id_logement)
        .first()
    )
    couverts = chantiers_couverts(utilisateur, ressource, action)
    if logement is None or (couverts is not None and logement.zone.chantier_id not in couverts):
        raise _introuvable("Ce logement est introuvable.")
    return logement


def etape_autorisee(
    utilisateur: Any, id_etape: Any, ressource: str, action: str, verrouiller: bool = False
) -> EtapeTravaux:
    """L'étape (verrouillée jusqu'à la fin de la transaction si demandé :
    ``etape_travaux`` n'est pas immuable, le rôle applicatif peut la verrouiller)."""
    requete = EtapeTravaux.objects.select_related(
        "logement__zone", "etape_modele__corps_etat"
    ).filter(id_etape=id_etape)
    if verrouiller:
        requete = requete.select_for_update(of=("self",))
    etape = requete.first()
    couverts = chantiers_couverts(utilisateur, ressource, action)
    if etape is None or (couverts is not None and etape.logement.zone.chantier_id not in couverts):
        raise _introuvable("Cette étape est introuvable.")
    return etape
