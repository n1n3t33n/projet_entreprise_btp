"""Cible d'import CSV du domaine « stock » (EF-ADM-02 « stock de départ »).

Colonnes : ``magasin`` (code), ``article`` (code), ``quantite`` ; facultatives
``seuil_minimal`` et ``seuil_critique`` (ensemble). Une ligne de stock est
identifiée par le couple (magasin, article).

Le stock de départ est un mouvement ENT_STOCK_INITIAL inscrit au nom de la
personne qui importe (RG-S2 : un stock ne se saisit pas, il se mouvemente) ;
il n'existe qu'une fois par article et par magasin. Une quantité nulle ne
crée pas de mouvement mais peut poser des seuils. Les seuils posés activent
les alertes (RG-S5). Décimaux avec point ou virgule.

Droit : ``api.import.creer`` (route d'import commune) ; l'import est une
fonction d'administration qui porte sur tous les magasins.
"""

from decimal import Decimal, InvalidOperation
from typing import Any

from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.stock.constantes import TYPE_STOCK_INITIAL
from domaines.stock.models import MouvementStock
from domaines.stock.services import seuils, stock_initial
from socle.importation import CibleImport, Colonne, Ligne, Validateur


def lire_decimal(valeur: str) -> Decimal | None:
    try:
        nombre = Decimal(valeur.replace(",", ".").replace(" ", ""))
    except InvalidOperation:
        return None
    return nombre if nombre.is_finite() else None


def _preparer() -> Validateur:
    magasins = set(selecteurs_organisation.magasins().values_list("code", flat=True))
    articles = set(
        selecteurs_referentiels.articles().filter(actif=True).values_list("code", flat=True)
    )
    deja = set(
        MouvementStock.objects.filter(type_mouvement_id=TYPE_STOCK_INITIAL).values_list(
            "magasin__code", "article__code"
        )
    )

    def valider(ligne: Ligne) -> str | None:
        if ligne["magasin"] not in magasins:
            return f"le magasin « {ligne['magasin']} » n'existe pas"
        if ligne["article"] not in articles:
            return f"l'article « {ligne['article']} » n'existe pas ou n'est plus actif"
        quantite = lire_decimal(ligne["quantite"])
        if quantite is None or quantite < 0:
            return "« quantite » doit être un nombre positif ou nul"
        if quantite > 0 and (ligne["magasin"], ligne["article"]) in deja:
            return "le stock de départ de cet article est déjà enregistré dans ce magasin"
        minimal, critique = ligne["seuil_minimal"], ligne["seuil_critique"]
        if bool(minimal) != bool(critique):
            return "« seuil_minimal » et « seuil_critique » se renseignent ensemble"
        if minimal:
            valeur_min, valeur_crit = lire_decimal(minimal), lire_decimal(critique)
            if valeur_min is None or valeur_crit is None or valeur_min < 0 or valeur_crit < 0:
                return "les seuils doivent être des nombres positifs ou nuls"
            if valeur_crit > valeur_min:
                return "le seuil critique ne peut pas dépasser le seuil minimal"
        return None

    return valider


def _enregistrer(lignes: list[Ligne], utilisateur: Any) -> int:
    magasins = {magasin.code: magasin for magasin in selecteurs_organisation.magasins()}
    articles = {article.code: article for article in selecteurs_referentiels.articles()}
    for ligne in lignes:
        magasin, article = magasins[ligne["magasin"]], articles[ligne["article"]]
        quantite = lire_decimal(ligne["quantite"]) or Decimal("0")
        if quantite > 0:
            stock_initial.inscrire_stock_initial(utilisateur, magasin, article, quantite)
        if ligne["seuil_minimal"]:
            seuils.definir(
                magasin.pk,
                article.pk,
                lire_decimal(ligne["seuil_minimal"]) or Decimal("0"),
                lire_decimal(ligne["seuil_critique"]) or Decimal("0"),
            )
    return len(lignes)


STOCK = CibleImport(
    code="stock",
    colonnes=(
        Colonne("magasin"),
        Colonne("article"),
        Colonne("quantite"),
        Colonne("seuil_minimal", obligatoire=False),
        Colonne("seuil_critique", obligatoire=False),
    ),
    preparer=_preparer,
    enregistrer=_enregistrer,
    cle=("magasin", "article"),
)
