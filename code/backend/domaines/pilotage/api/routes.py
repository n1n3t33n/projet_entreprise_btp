"""Routes du pilotage transverse (EF-DSH-06, EF-DSH-07)."""

from django.urls import path

from domaines.pilotage.api import vues

urlpatterns = [
    path(
        "pilotage/rapport-hebdomadaire",
        vues.VueRapportHebdomadaire.as_view(),
        name="pilotage-rapport-hebdomadaire",
    ),
    path("pilotage/usage", vues.VueUsage.as_view(), name="pilotage-usage"),
]
