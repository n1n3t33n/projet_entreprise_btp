"""Limitation du taux (exigence 6.3 du rapport B0).

Les compteurs vivent dans le cache Django (mémoire locale en B1, arbitrage
Q5 ; dette : cache partagé avant tout passage à plusieurs processus).

Le point d'entrée de synchronisation recevra en B5 sa propre portée, par
APPAREIL et par taille de lot, pour qu'une rafale légitime au retour du
réseau ne soit jamais rejetée en bloc (rapport B0 § 6.5).
"""

from typing import TYPE_CHECKING

from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle, UserRateThrottle

if TYPE_CHECKING:
    # Annotations seulement : importer rest_framework.views au chargement
    # créerait une importation circulaire avec les réglages de DRF.
    from rest_framework.request import Request
    from rest_framework.views import APIView


class LimitationAnonyme(AnonRateThrottle):
    """Requêtes sans authentification, comptées par adresse IP."""

    scope = "anonyme"


class LimitationUtilisateur(UserRateThrottle):
    """Requêtes authentifiées, comptées par utilisateur."""

    scope = "utilisateur"


class LimitationConnexionParIP(SimpleRateThrottle):
    """Tentatives de connexion par adresse IP : freine le robot qui essaie
    beaucoup d'identifiants depuis une même machine."""

    scope = "connexion_ip"

    def get_cache_key(self, request: "Request", view: "APIView") -> str | None:
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class LimitationConnexionParIdentifiant(SimpleRateThrottle):
    """Tentatives de connexion par identifiant : freine l'essai de nombreux
    mots de passe sur un même compte. C'est la réponse retenue à EF-AUT-04
    (arbitrage Q11) : un « 429 VERROUILLE » temporaire, sans verrouillage dur
    du compte."""

    scope = "connexion_identifiant"

    def get_cache_key(self, request: "Request", view: "APIView") -> str | None:
        identifiant = request.data.get("identifiant") if hasattr(request, "data") else None
        if not isinstance(identifiant, str) or not identifiant.strip():
            return None
        return self.cache_format % {"scope": self.scope, "ident": identifiant.strip().lower()}
