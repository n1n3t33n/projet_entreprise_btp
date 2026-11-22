"""Routes du domaine « avancement », aux chemins du contrat simulé web."""

from django.urls import path

from domaines.avancement.api import vues

urlpatterns = [
    path("avancement/zones", vues.VueZonesAvancement.as_view(), name="avancement-zones"),
    path("avancement/synthese", vues.VueSynthese.as_view(), name="avancement-synthese"),
    path(
        "avancement/logements", vues.VueLogementsAvancement.as_view(), name="avancement-logements"
    ),
    path(
        "pilotage/avancement/chantier", vues.VuePilotageChantier.as_view(), name="pilotage-chantier"
    ),
    path("pilotage/avancement/zones", vues.VuePilotageZones.as_view(), name="pilotage-zones"),
    path(
        "pilotage/avancement/logements",
        vues.VuePilotageLogements.as_view(),
        name="pilotage-logements",
    ),
    path(
        "pilotage/avancement/corps-etat",
        vues.VuePilotageCorpsEtat.as_view(),
        name="pilotage-corps-etat",
    ),
    path("pilotage/alertes-etapes", vues.VueAlertesEtapes.as_view(), name="pilotage-alertes"),
    path(
        "etapes/<uuid:id_etape>/declaration",
        vues.VueDeclaration.as_view(),
        name="etape-declaration",
    ),
    path("etapes/<uuid:id_etape>/blocage", vues.VueBlocage.as_view(), name="etape-blocage"),
    path(
        "etapes/<uuid:id_etape>/levee-blocage", vues.VueLeveeBlocage.as_view(), name="etape-levee"
    ),
    path(
        "etapes/<uuid:id_etape>/validation",
        vues.VueValidationEtape.as_view(),
        name="etape-validation",
    ),
    path(
        "etapes/<uuid:id_etape>/evenements",
        vues.VueEvenementsEtape.as_view(),
        name="etape-evenements",
    ),
    path("avancement/etapes-a-valider", vues.VueEtapesAValider.as_view(), name="etapes-a-valider"),
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
