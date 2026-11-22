"""Routes du domaine « stock », aux chemins du contrat simulé web."""

from django.urls import path

from domaines.stock.api import vues

urlpatterns = [
    path("magasins/<uuid:id_magasin>/stock", vues.VueStockMagasin.as_view(), name="stock-magasin"),
    path(
        "magasins/<uuid:id_magasin>/articles/<uuid:id_article>/seuil",
        vues.VueSeuil.as_view(),
        name="seuil",
    ),
    path(
        "magasins/<uuid:id_magasin>/articles/<uuid:id_article>/mouvements",
        vues.VueMouvementsArticle.as_view(),
        name="mouvements-article",
    ),
    path("stock/arborescence", vues.VueArborescence.as_view(), name="stock-arborescence"),
    path("stock/alertes", vues.VueAlertes.as_view(), name="stock-alertes"),
    path("mouvements", vues.VueMouvements.as_view(), name="mouvements"),
    path("mouvements/a-valider", vues.VueMouvementsAValider.as_view(), name="mouvements-a-valider"),
    path(
        "mouvements/<uuid:uuid_mouvement>/validation",
        vues.VueDecision.as_view(),
        name="mouvement-validation",
    ),
    path(
        "mouvements/<uuid:uuid_mouvement>/annulation",
        vues.VueAnnulation.as_view(),
        name="mouvement-annulation",
    ),
    path("inventaires", vues.VueInventaires.as_view(), name="inventaires"),
    path("inventaires/<uuid:id_inventaire>", vues.VueInventaire.as_view(), name="inventaire"),
    path(
        "inventaires/<uuid:id_inventaire>/soumission",
        vues.VueSoumission.as_view(),
        name="inventaire-soumission",
    ),
    path(
        "inventaires/<uuid:id_inventaire>/lignes/<uuid:id_ligne>",
        vues.VueComptage.as_view(),
        name="inventaire-comptage",
    ),
    path(
        "inventaires/<uuid:id_inventaire>/lignes/<uuid:id_ligne>/validation",
        vues.VueValidationLigne.as_view(),
        name="inventaire-validation",
    ),
]
