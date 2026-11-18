"""En-têtes de session ajoutés aux réponses authentifiées.

Arbitrage Q2 : le verrou de 14 jours se calcule côté mobile depuis
``derniere_connexion_en_ligne`` (AC-1, ET-4), et TOUTE requête authentifiée
réussie du mobile (connexion OU synchronisation) le rafraîchit. Le serveur
fournit donc, sur chaque réponse authentifiée réussie :
  * ``X-Horodatage-Serveur`` : l'heure du serveur, que le mobile range dans
    ``derniere_connexion_en_ligne`` (l'horloge du téléphone n'est pas fiable) ;
  * ``X-Jeton-Renouvele`` (mobile seulement) : un jeton neuf quand le jeton
    présenté a plus de ``JETON_RENOUVELLEMENT_HEURES`` heures, pour qu'un
    appareil qui se synchronise régulièrement ne soit jamais forcé à
    ressaisir son mot de passe au bout de 14 jours.
"""

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from django.utils import timezone

EN_TETE_HORODATAGE = "X-Horodatage-Serveur"
EN_TETE_JETON_RENOUVELE = "X-Jeton-Renouvele"


class MiddlewareEnTetesSession:
    """Ajoute les en-têtes de session après une réponse authentifiée réussie."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        reponse = self.get_response(request)
        if not getattr(request, "jeton_authentifie", False) or reponse.status_code >= 400:
            return reponse
        reponse[EN_TETE_HORODATAGE] = timezone.now().isoformat()
        jeton_neuf = getattr(request, "jeton_renouvele", None)
        if jeton_neuf:
            reponse[EN_TETE_JETON_RENOUVELE] = jeton_neuf
        return reponse
