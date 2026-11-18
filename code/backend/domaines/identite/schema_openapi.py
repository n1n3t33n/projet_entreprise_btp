"""Description OpenAPI de l'authentification par jeton porteur (exigence 6.9).

Permet à Swagger de proposer « Authorize » avec un jeton « Bearer » et au
schéma de déclarer, pour chaque point d'entrée protégé, le jeton exigé.
Chargé au démarrage par ``ConfigurationIdentite.ready``.
"""

from typing import Any

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class SchemaJetonPorteur(OpenApiAuthenticationExtension):  # type: ignore[no-untyped-call]
    target_class = "domaines.identite.authentification.AuthentificationParJeton"
    name = "jetonPorteur"

    def get_security_definition(self, auto_schema: Any) -> dict[str, str]:
        return {
            "type": "http",
            "scheme": "bearer",
            "description": (
                "Jeton rendu par POST /api/auth/connexion. Mobile : lié à l'appareil, "
                "14 jours, renouvelé par l'en-tête X-Jeton-Renouvele. Web : 8 heures."
            ),
        }
