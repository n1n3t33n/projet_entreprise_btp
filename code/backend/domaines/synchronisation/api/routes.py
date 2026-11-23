"""Routes du domaine « synchronisation » (SQ-2)."""

from django.urls import path

from domaines.synchronisation.api import vues

urlpatterns = [
    path("synchronisation/lots", vues.VueLots.as_view(), name="synchronisation-lots"),
]
