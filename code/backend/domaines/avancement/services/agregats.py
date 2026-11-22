"""Agrégats d'avancement (RG-A6, CL-5 ``AvancementAgrege``).

Un agrégat par portée et par cible (Q-V) : logement, zone, chantier, et corps
d'état d'un chantier (cible « id du chantier:code du corps d'état »). Un
événement d'exécution alimente l'agrégat de SON logement (MCD « alimente »
(1,1), H11).
"""

from typing import Any

from domaines.avancement.constantes import PORTEE_LOGEMENT
from domaines.avancement.models import AvancementAgrege


def agregat(portee: str, id_cible: str) -> AvancementAgrege:
    return AvancementAgrege.objects.get_or_create(portee=portee, id_cible=id_cible)[0]


def agregat_du_logement(logement: Any) -> AvancementAgrege:
    return agregat(PORTEE_LOGEMENT, str(logement.pk))
