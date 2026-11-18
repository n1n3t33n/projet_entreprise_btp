"""Permission DRF ``ADroit(module, ressource, action)`` (EF-AUT-07).

EF-AUT-07 : « Appliquer la matrice de droits côté serveur à chaque requête ».
Chaque vue de l'API déclare explicitement le droit qu'elle exige ; la
décision vient de la matrice en base (droit_accorde), jamais d'un test de
rôle écrit dans le code. Les rares vues publiques (connexion, santé)
déclarent ``AllowAny`` explicitement.
"""

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from domaines.identite.services.droits import a_le_droit


def ADroit(module: str, ressource: str, action: str) -> type[BasePermission]:  # noqa: N802
    """Fabrique la classe de permission exigeant (module, ressource, action)."""

    class _Droit(BasePermission):
        exigence = (module, ressource, action)

        def has_permission(self, request: Request, view: Any) -> bool:
            utilisateur = request.user
            if utilisateur is None or not utilisateur.is_authenticated:
                return False
            return a_le_droit(utilisateur, module, ressource, action)

    _Droit.__name__ = f"ADroit_{module}_{ressource}_{action}".replace("-", "_")
    _Droit.__qualname__ = _Droit.__name__
    return _Droit
