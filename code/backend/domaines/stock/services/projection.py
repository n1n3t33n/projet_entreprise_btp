"""Projection du stock courant, niveaux et alertes de seuil.

RG-S2 : le stock d'un article dans un magasin est la somme des mouvements ;
``stock_courant`` n'est qu'une projection recalculée à chaque mouvement, sous
verrou de ligne (deux saisies simultanées ne perdent pas de quantité).

Niveau (même règle que le web, ``lib/seuils.ts``) : stock nul ou négatif →
VIDE ; sous le seuil critique → CRITIQUE ; sous le seuil minimal → MINIMAL ;
sinon NORMAL. Un seuil inactif ne classe que VIDE ou NORMAL.

Alertes (RG-S5, RG-S7, EF-STK-07) : une alerte s'ouvre quand le niveau se
dégrade (et à chaque passage sous zéro) ; les alertes ouvertes se ferment
d'elles-mêmes quand le stock redevient normal ou positif.
"""

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from domaines.stock.constantes import (
    ALERTE_OUVERTE,
    ALERTE_SEUIL_CRITIQUE,
    ALERTE_SEUIL_MINIMAL,
    ALERTE_STOCK_NEGATIF,
    ALERTE_TRAITEE,
    NIVEAU_CRITIQUE,
    NIVEAU_MINIMAL,
    NIVEAU_NORMAL,
    NIVEAU_VIDE,
)
from domaines.stock.models import Alerte, SeuilStock, StockCourant
from domaines.stock.services import publications

# Gravité croissante, pour savoir si un niveau se dégrade.
GRAVITE = {NIVEAU_NORMAL: 0, NIVEAU_MINIMAL: 1, NIVEAU_CRITIQUE: 2, NIVEAU_VIDE: 3}


def niveau(quantite: Decimal, seuil: SeuilStock) -> str:
    if quantite <= 0:
        return NIVEAU_VIDE
    if not seuil.actif:
        return NIVEAU_NORMAL
    if quantite < seuil.seuil_critique:
        return NIVEAU_CRITIQUE
    if quantite < seuil.seuil_minimal:
        return NIVEAU_MINIMAL
    return NIVEAU_NORMAL


def stock_courant_verrouille(id_magasin: Any, id_article: Any) -> StockCourant:
    """Stock courant de l'article dans le magasin, verrouillé jusqu'à la fin de
    la transaction. Au premier mouvement, le seuil (inactif) et la projection
    sont créés : le MPD identifie le stock courant par son seuil (Q-O)."""
    seuil, _ = SeuilStock.objects.get_or_create(magasin_id=id_magasin, article_id=id_article)
    StockCourant.objects.get_or_create(seuil_stock=seuil)
    return (
        StockCourant.objects.select_for_update()
        .select_related("seuil_stock__article", "seuil_stock__magasin")
        .get(seuil_stock=seuil)
    )


def ouvrir_alerte(stock: StockCourant, type_alerte: str, message: str) -> None:
    """Ouvre une alerte, sauf si la même est déjà ouverte pour ce stock (un
    stock critique qui devient vide ne crée pas une seconde alerte)."""
    if Alerte.objects.filter(
        stock_courant=stock, type_alerte=type_alerte, statut=ALERTE_OUVERTE
    ).exists():
        return
    alerte = Alerte.objects.create(
        type_alerte=type_alerte,
        niveau=stock.niveau_alerte,
        message=message,
        statut=ALERTE_OUVERTE,
        stock_courant=stock,
    )
    publications.alerte_ouverte(alerte, stock)


def fermer_alertes(stock: StockCourant, types: list[str]) -> None:
    Alerte.objects.filter(stock_courant=stock, statut=ALERTE_OUVERTE, type_alerte__in=types).update(
        statut=ALERTE_TRAITEE
    )


@transaction.atomic
def recalculer(stock: StockCourant, nouvelle_quantite: Decimal) -> StockCourant:
    """Pose la nouvelle quantité, reclasse le niveau, ouvre ou ferme les
    alertes. ``stock`` doit venir de ``stock_courant_verrouille``."""
    seuil = stock.seuil_stock
    ancienne_quantite, ancien_niveau = stock.quantite, stock.niveau_alerte
    stock.quantite = nouvelle_quantite
    stock.niveau_alerte = niveau(nouvelle_quantite, seuil)
    stock.date_calcul = timezone.now()
    stock.save(update_fields=["quantite", "niveau_alerte", "date_calcul"])

    article, magasin = seuil.article, seuil.magasin
    libelle = f"{article.designation} ({article.code}), magasin {magasin.code}"
    if nouvelle_quantite < 0 <= ancienne_quantite:
        ouvrir_alerte(
            stock, ALERTE_STOCK_NEGATIF, f"{libelle} : stock négatif ({nouvelle_quantite})."
        )
    if nouvelle_quantite >= 0:
        fermer_alertes(stock, [ALERTE_STOCK_NEGATIF])
    if seuil.actif and GRAVITE[stock.niveau_alerte] > GRAVITE[ancien_niveau]:
        if stock.niveau_alerte == NIVEAU_MINIMAL:
            ouvrir_alerte(
                stock,
                ALERTE_SEUIL_MINIMAL,
                f"{libelle} : {nouvelle_quantite} sous le seuil minimal ({seuil.seuil_minimal}).",
            )
        else:
            ouvrir_alerte(
                stock,
                ALERTE_SEUIL_CRITIQUE,
                f"{libelle} : {nouvelle_quantite} sous le seuil critique ({seuil.seuil_critique}).",
            )
    if stock.niveau_alerte == NIVEAU_NORMAL:
        fermer_alertes(stock, [ALERTE_SEUIL_MINIMAL, ALERTE_SEUIL_CRITIQUE])
    return stock
