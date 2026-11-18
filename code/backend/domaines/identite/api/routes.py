"""Routes du domaine identité, en français et SANS barre finale : ce sont
exactement les chemins que le web et le mobile appellent déjà (rapport B0
§ 3.2), sous le préfixe « /api »."""

from django.urls import path

from domaines.identite.api import vues

urlpatterns = [
    path("auth/connexion", vues.VueConnexion.as_view(), name="auth-connexion"),
    path("auth/deconnexion", vues.VueDeconnexion.as_view(), name="auth-deconnexion"),
    path("auth/moi", vues.VueMoi.as_view(), name="auth-moi"),
    path("auth/perimetres", vues.VuePerimetres.as_view(), name="auth-perimetres"),
    path("auth/comptes", vues.VueComptes.as_view(), name="auth-comptes"),
    path("auth/comptes/<uuid:id_utilisateur>", vues.VueCompte.as_view(), name="auth-compte"),
    path("droits/roles", vues.VueRoles.as_view(), name="droits-roles"),
    path("droits/permissions", vues.VuePermissions.as_view(), name="droits-permissions"),
    path("droits/accordes", vues.VueDroitsAccordes.as_view(), name="droits-accordes"),
    path("appareils", vues.VueAppareils.as_view(), name="appareils"),
    path(
        "appareils/<uuid:id_appareil>/revocation",
        vues.VueRevocation.as_view(),
        name="appareil-revocation",
    ),
    path("audit", vues.VueAudit.as_view(), name="audit"),
]
