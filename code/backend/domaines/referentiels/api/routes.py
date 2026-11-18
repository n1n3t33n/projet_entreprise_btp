"""Routes du domaine « référentiels », aux chemins du contrat simulé web."""

from django.urls import path

from domaines.referentiels.api import vues

urlpatterns = [
    path("referentiels/categories", vues.VueCategories.as_view(), name="categories"),
    path("referentiels/unites", vues.VueUnites.as_view(), name="unites"),
    path("referentiels/articles", vues.VueArticles.as_view(), name="articles"),
    path("referentiels/articles/<uuid:id_article>", vues.VueArticle.as_view(), name="article"),
    path("gammes/corps-etat", vues.VueCorpsEtat.as_view(), name="corps-etat"),
    path("gammes/corps-etat/<str:code>", vues.VueUnCorpsEtat.as_view(), name="un-corps-etat"),
    path("gammes", vues.VueGammes.as_view(), name="gammes"),
    path("gammes/<uuid:id_gamme>", vues.VueGamme.as_view(), name="gamme"),
    path("gammes/<uuid:id_gamme>/etapes", vues.VueEtapesGamme.as_view(), name="gamme-etapes"),
    path("gammes/<uuid:id_gamme>/versions", vues.VueVersionGamme.as_view(), name="gamme-version"),
    path(
        "gammes/<uuid:id_gamme>/publication",
        vues.VuePublicationGamme.as_view(),
        name="gamme-publication",
    ),
    path(
        "gammes/<uuid:id_gamme>/archivage",
        vues.VueArchivageGamme.as_view(),
        name="gamme-archivage",
    ),
    path("types-mouvement", vues.VueTypesMouvement.as_view(), name="types-mouvement"),
    path("motifs-blocage", vues.VueMotifsBlocage.as_view(), name="motifs-blocage"),
    path("parametrage/regles", vues.VueRegles.as_view(), name="regles"),
    path("parametrage/regles/<uuid:id_regle>", vues.VueRegle.as_view(), name="regle"),
]
