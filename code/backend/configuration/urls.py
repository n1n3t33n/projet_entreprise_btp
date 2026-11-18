"""Routes racines du backend ChantierSync.

Tout est sous « /api », chemin déjà attendu par les deux fronts
(``VITE_API_BASE_URL=http://localhost:8000/api`` ; mobile ``…/api``).
Aucune version dans l'URL : le contrat simulé des fronts n'en a pas.

La documentation (schéma OpenAPI, Swagger, ReDoc — exigence 6.9) est servie
en production mais protégée : il faut le droit « technique / documentation /
LIRE » de la matrice. Elle accepte le jeton porteur ou la session de
l'administration (ouvrir /admin/ d'abord, puis /api/docs/swagger/).
"""

from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from domaines.identite.authentification import AuthentificationParJeton
from domaines.identite.constantes import ACTION_LIRE, MODULE_TECHNIQUE
from domaines.identite.permissions import ADroit
from socle import sante

PROTECTION_DOCUMENTATION = {
    "authentication_classes": [AuthentificationParJeton, SessionAuthentication],
    "permission_classes": [IsAuthenticated, ADroit(MODULE_TECHNIQUE, "documentation", ACTION_LIRE)],
}

routes_api: list[URLPattern | URLResolver] = [
    path("sante/vivacite", sante.vivacite, name="sante-vivacite"),
    path("sante/aptitude", sante.aptitude, name="sante-aptitude"),
    path("", include("domaines.identite.api.routes")),
    path("", include("domaines.organisation.api.routes")),
    path("", include("domaines.referentiels.api.routes")),
    path("schema/", SpectacularAPIView.as_view(**PROTECTION_DOCUMENTATION), name="schema"),
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema", **PROTECTION_DOCUMENTATION),
        name="docs-swagger",
    ),
    path(
        "docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema", **PROTECTION_DOCUMENTATION),
        name="docs-redoc",
    ),
]

urlpatterns = [
    path("api/", include(routes_api)),
    path("admin/", admin.site.urls),
]

# Erreurs hors des vues de l'API : même format JSON que l'API.
handler404 = "socle.erreurs.page_introuvable"
handler500 = "socle.erreurs.erreur_serveur"
