"""Routes du domaine « synchronisation » (SQ-2, EF-SYN-04, EF-SYN-05)."""

from django.urls import path

from domaines.synchronisation.api import vues

urlpatterns = [
    path("synchronisation/lots", vues.VueLots.as_view(), name="synchronisation-lots"),
    path(
        "synchronisation/references",
        vues.VueReferences.as_view(),
        name="synchronisation-references",
    ),
    path(
        "synchronisation/anomalies",
        vues.VueAnomalies.as_view(),
        name="synchronisation-anomalies",
    ),
    path(
        "synchronisation/anomalies/<uuid:id_anomalie>/traitement",
        vues.VueTraitementAnomalie.as_view(),
        name="synchronisation-anomalie-traitement",
    ),
]
