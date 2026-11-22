"""Routes du domaine « avancement », aux chemins du contrat simulé web."""

from django.urls import path

from domaines.avancement.api import vues

urlpatterns = [
    path(
        "logements/<uuid:id_logement>/etapes",
        vues.VueEtapesLogement.as_view(),
        name="etapes-logement",
    ),
    path("fiches-route", vues.VueFiches.as_view(), name="fiches-route"),
    path("fiches-route/courante", vues.VueFicheCourante.as_view(), name="fiche-courante"),
    path("fiches-route/affectations", vues.VueAffectations.as_view(), name="fiches-affectations"),
    path("fiches-route/<uuid:id_fiche>", vues.VueFiche.as_view(), name="fiche-route"),
    path("fiches-route/<uuid:id_fiche>/cloture", vues.VueCloture.as_view(), name="fiche-cloture"),
]
