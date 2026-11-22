"""Cible d'import CSV du domaine « référentiels » (EF-ADM-02) : les articles.
Déclarée au démarrage par ``apps.ready()`` ; le moteur commun est dans
``socle/importation.py``.

Colonnes tirées du MPD-3 (I-37) : la simulation du web demandait
``seuil_minimal`` et ``seuil_critique``, qui appartiennent au domaine stock
(table ``seuil_stock``, B4) et ne s'importent pas avec l'article. Une ligne
dont le code existe déjà MET À JOUR l'article.
"""

from typing import Any

from domaines.referentiels import selecteurs
from domaines.referentiels.constantes import ORIGINES_ARTICLE
from domaines.referentiels.models import Article
from socle.importation import CibleImport, Colonne, Ligne, Validateur, longueur_excessive

ORIGINE_PAR_DEFAUT = "ACHAT"


def _preparer() -> Validateur:
    # Trois requêtes pour toute l'analyse, aucune par ligne.
    unites = set(selecteurs.unites().values_list("code_unite", flat=True))
    familles = set(selecteurs.categories().values_list("code_categorie", flat=True))
    codes_barres = dict(
        selecteurs.articles().exclude(code_barre=None).values_list("code_barre", "code")
    )
    codes_barres_du_fichier: set[str] = set()

    def valider(ligne: Ligne) -> str | None:
        trop_long = longueur_excessive(ligne, {"code": 32, "designation": 120, "code_barre": 32})
        if trop_long:
            return trop_long
        if ligne["unite"] not in unites:
            return f"l'unité « {ligne['unite']} » n'existe pas"
        if ligne["famille"] and ligne["famille"] not in familles:
            return f"la famille « {ligne['famille']} » n'existe pas"
        if ligne["origine"] and ligne["origine"].upper() not in ORIGINES_ARTICLE:
            return f"« origine » doit valoir {', '.join(ORIGINES_ARTICLE)}"
        code_barre = ligne["code_barre"]
        if code_barre:
            proprietaire = codes_barres.get(code_barre)
            if proprietaire is not None and proprietaire != ligne["code"]:
                return f"le code-barres est déjà porté par l'article « {proprietaire} »"
            if code_barre in codes_barres_du_fichier:
                return "le code-barres apparaît deux fois dans le fichier"
            codes_barres_du_fichier.add(code_barre)
        return None

    return valider


def _enregistrer(lignes: list[Ligne], utilisateur: Any) -> int:
    for ligne in lignes:
        Article.objects.update_or_create(
            code=ligne["code"],
            defaults={
                "designation": ligne["designation"],
                "unite_mesure_id": ligne["unite"],
                "categorie_article_id": ligne["famille"] or None,
                "origine": (ligne["origine"] or ORIGINE_PAR_DEFAUT).upper(),
                "code_barre": ligne["code_barre"] or None,
            },
        )
    return len(lignes)


ARTICLES = CibleImport(
    code="articles",
    colonnes=(
        Colonne("code"),
        Colonne("designation"),
        Colonne("unite"),
        Colonne("origine", obligatoire=False),
        Colonne("famille", obligatoire=False),
        Colonne("code_barre", obligatoire=False),
    ),
    preparer=_preparer,
    enregistrer=_enregistrer,
)
