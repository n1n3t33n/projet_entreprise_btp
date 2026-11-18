"""Routes du domaine « organisation », aux chemins du contrat simulé web."""

from django.urls import path

from domaines.organisation.api import vues

urlpatterns = [
    path("referentiels/chantiers", vues.VueChantiers.as_view(), name="chantiers"),
    path("referentiels/chantiers/<uuid:id_chantier>", vues.VueChantier.as_view(), name="chantier"),
    path(
        "referentiels/chantiers/<uuid:id_chantier>/arborescence",
        vues.VueArborescence.as_view(),
        name="chantier-arborescence",
    ),
    path("referentiels/magasins", vues.VueMagasinsReferentiel.as_view(), name="magasins-ref"),
    path(
        "referentiels/magasins/<uuid:id_magasin>",
        vues.VueMagasinReferentiel.as_view(),
        name="magasin-ref",
    ),
    path("magasins", vues.VueMagasinsStock.as_view(), name="magasins-stock"),
    path("referentiels/zones", vues.VueZones.as_view(), name="zones"),
    path("referentiels/zones/<uuid:id_zone>", vues.VueZone.as_view(), name="zone"),
    path("referentiels/logements", vues.VueLogements.as_view(), name="logements"),
    path("referentiels/logements/<uuid:id_logement>", vues.VueLogement.as_view(), name="logement"),
    path(
        "chantiers/<uuid:id_chantier>/logements",
        vues.VueLogementsDuChantier.as_view(),
        name="chantier-logements",
    ),
    path("referentiels/types-logement", vues.VueTypesLogement.as_view(), name="types-logement"),
    path("parametrage/parametres", vues.VueParametres.as_view(), name="parametres"),
    path(
        "parametrage/parametres/<uuid:id_parametre>",
        vues.VueParametre.as_view(),
        name="parametre",
    ),
]
