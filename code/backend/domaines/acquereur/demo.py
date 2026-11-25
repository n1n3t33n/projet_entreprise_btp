"""Données de démonstration du domaine « acquéreur », reprises de la
simulation du web (``lib/mocks/acquereur-grand-bassam.ts``) : l'acquéreuse
Mariam Diallo (compte ``m.diallo``) a acheté le logement A01.

Rang 50 : après l'organisation (logements), l'identité (compte) et
l'avancement (étapes). Rejouable : l'acquéreur est repris s'il existe.
"""

from datetime import datetime

from django.utils import timezone

from domaines.identite.selecteurs import comptes
from domaines.identite.services import comptes as service_comptes
from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.organisation.models import Acquereur

LOGEMENT = "A01"
IDENTIFIANT = "m.diallo"
DATE_ACQUISITION = datetime(2026, 9, 15, 10, 0)


def charger(mot_de_passe: str) -> dict[str, int]:
    logement = selecteurs_organisation.logements().filter(numero=LOGEMENT).first()
    compte = comptes.par_identifiant(IDENTIFIANT)
    if logement is None or compte is None:
        return {"acquéreurs": 0}
    acquereur, _cree = Acquereur.objects.get_or_create(
        logement=logement,
        defaults={
            "nom": compte.nom,
            "prenom": compte.prenom,
            "date_acquisition": timezone.make_aware(DATE_ACQUISITION),
        },
    )
    service_comptes.rattacher_acquereur(compte, acquereur)
    return {"acquéreurs": Acquereur.objects.count()}
