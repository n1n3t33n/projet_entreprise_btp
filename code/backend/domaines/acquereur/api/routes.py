"""Routes de l'espace acquéreur, aux chemins du web (features/acquereur)."""

from django.urls import path

from domaines.acquereur.api import vues

urlpatterns = [
    path("acquereur/logement", vues.VueLogement.as_view(), name="acquereur-logement"),
    path(
        "acquereur/notifications", vues.VueNotifications.as_view(), name="acquereur-notifications"
    ),
]
