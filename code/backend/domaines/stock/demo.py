"""Données de démonstration du domaine « stock », reprises de la simulation
du web (``lib/mocks/donnees-grand-bassam.ts``) : seuils par unité, stock de
départ réparti par niveaux (une seule référence en stock négatif, quelques
vides, critiques et au minimum, le reste plein), et une sortie au-delà du
seuil de validation (RG-S6) pour exercer l'écran de validation.

Tout passe par les services du domaine (RG-S2 : le stock est la somme des
mouvements) ; le chargement est rejouable : stock de départ et sorties
portent des identifiants stables et ne sont jamais inscrits deux fois.
Comptes, articles, magasin et logements sont LUS par les sélecteurs de leurs
domaines, chargés avant celui-ci (rang 30).
"""

from decimal import Decimal
from typing import Any

from domaines.identite.selecteurs import comptes
from domaines.organisation import demo as demo_organisation
from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.organisation.models import Magasin
from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.referentiels.models import Article
from domaines.stock.models import MouvementStock
from domaines.stock.services import mouvements, seuils, stock_initial
from socle.demo import uid

# Seuils indicatifs par unité de base (minimal, critique), comme le web.
ECHELLE_SEUIL = {
    "SAC": (80, 30),
    "KG": (150, 50),
    "T": (20, 6),
    "M3": (40, 12),
    "M2": (120, 40),
    "ML": (300, 100),
    "L": (60, 20),
    "U": (60, 20),
    "BTE": (25, 8),
    "ROUL": (18, 5),
}

RANG_STOCK_NEGATIF = 6
# Fer HA 12 (330 ml en stock) : la sortie reste couverte par le stock.
RANG_SORTIE_A_VALIDER = 8
QUANTITE_SORTIE_A_VALIDER = 120  # au-delà du seuil de la règle R-003 (100)


def _bande(rang: int) -> int:
    """Même répartition que la simulation du web (``bandeNiveau``)."""
    if rang == RANG_STOCK_NEGATIF:
        return 6
    if rang % 12 == 3:
        return 0
    if rang % 6 == 1:
        return 1
    if rang % 6 == 4:
        return 2
    return 3 + rang % 3


def _quantite_initiale(minimal: int, critique: int, bande: int) -> int:
    quantites = {
        0: 0,
        6: 0,  # le stock négatif vient d'une sortie, pas d'un stock de départ
        1: round(critique * 0.5),
        2: round(critique + (minimal - critique) * 0.4),
        3: round(minimal * 1.6),
        4: round(minimal * 2.2),
    }
    return quantites.get(bande, round(minimal * 1.1))


def _sortie(auteur: Any, magasin: Magasin, cle: str, article: Article, quantite: int) -> None:
    """Sortie vers le premier logement du chantier, rejouable (uuid stable)."""
    type_sortie = selecteurs_referentiels.type_mouvement("SOR_LOGEMENT")
    if type_sortie is None:
        raise LookupError("Le type SOR_LOGEMENT doit être chargé d'abord.")
    saisie = mouvements.Saisie(
        magasin=magasin,
        article=article,
        type_mouvement=type_sortie,
        quantite_saisie=Decimal(quantite),
        uuid=uid("mouvement", cle),
        logement=selecteurs_organisation.logements_du_chantier(str(magasin.chantier_id)).first(),
        corps_etat=selecteurs_referentiels.corps_etat().filter(code_corps_etat="GO").first(),
        beneficiaire="Équipe gros œuvre A",
    )
    mouvements.enregistrer(auteur, saisie)


def charger(mot_de_passe: str) -> dict[str, int]:
    magasin = selecteurs_organisation.magasin_par_code(demo_organisation.CODE_MAGASIN)
    gestionnaire = comptes.par_identifiant("gestionnaire")
    magasinier = comptes.par_identifiant("magasinier")
    if magasin is None or gestionnaire is None or magasinier is None:
        raise LookupError(
            "Le magasin et les comptes de démonstration doivent être chargés d'abord."
        )
    articles = list(selecteurs_referentiels.articles())
    for rang, article in enumerate(articles):
        minimal, critique = ECHELLE_SEUIL.get(article.unite_mesure_id, ECHELLE_SEUIL["U"])
        quantite = _quantite_initiale(minimal, critique, _bande(rang))
        if quantite > 0 and not stock_initial.existe(magasin.pk, article.pk):
            stock_initial.inscrire_stock_initial(
                gestionnaire,
                magasin,
                article,
                Decimal(quantite),
                uuid=uid("mouvement", f"initial-{article.code}"),
            )
        seuils.definir(magasin.pk, article.pk, Decimal(minimal), Decimal(critique))
    # L'unique anomalie : une sortie plus forte que le stock (RG-S7).
    negatif = articles[RANG_STOCK_NEGATIF]
    _, critique_negatif = ECHELLE_SEUIL.get(negatif.unite_mesure_id, ECHELLE_SEUIL["U"])
    _sortie(magasinier, magasin, "sortie-negative", negatif, round(critique_negatif * 0.2))
    # Une sortie au-delà du seuil de validation, en attente de décision. La clé
    # porte le code de l'article : changer d'article ne heurte pas, au rejeu,
    # une sortie déjà inscrite au journal immuable sous l'ancienne clé.
    a_valider = articles[RANG_SORTIE_A_VALIDER]
    _sortie(
        magasinier,
        magasin,
        f"sortie-a-valider-{a_valider.code}",
        a_valider,
        QUANTITE_SORTIE_A_VALIDER,
    )
    return {
        "seuils": len(articles),
        "mouvements": MouvementStock.objects.filter(magasin=magasin).count(),
    }
