"""Limitation du taux (exigence 6.3 du rapport B0).

Les compteurs vivent dans le cache Django (mémoire locale en B1, arbitrage
Q5 ; dette : cache partagé avant tout passage à plusieurs processus).

Le point d'entrée de synchronisation a sa propre portée, par APPAREIL
(``LimitationAppareil``, B5, Q-AL) ; la taille d'un lot est bornée à part :
une rafale légitime au retour du réseau tient en quelques lots, jamais
rejetés en bloc (rapport B0 § 6.5).
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


class LimitationAppareil(SimpleRateThrottle):
    """Lots de synchronisation par appareil enrôlé (Q-AL, 30 par minute par
    défaut) : un téléphone qui boucle ne gêne pas les autres."""

    scope = "synchronisation"

    def get_cache_key(self, request: "Request", view: "APIView") -> str | None:
        id_appareil = getattr(request.auth, "id_appareil", None)
        if not id_appareil:
            return None
        return self.cache_format % {"scope": self.scope, "ident": id_appareil}
