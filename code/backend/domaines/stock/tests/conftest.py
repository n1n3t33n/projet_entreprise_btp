"""Fixtures du domaine stock : un petit catalogue et un mouvement prêt à
l'emploi, construits directement en base (les services sont testés à part)."""

from decimal import Decimal
from typing import Any

import pytest

from domaines.referentiels.models import Article, TypeMouvement, UniteMesure
from domaines.stock.models import MouvementStock, SeuilStock, StockCourant


@pytest.fixture
def catalogue(db: Any) -> dict[str, Any]:
    sac = UniteMesure.objects.create(code_unite="SAC", libelle="sac", type_unite="MASSE")
    ciment = Article.objects.create(
        code="A0001", designation="Ciment", origine="ACHAT", unite_mesure=sac
    )
    reception = TypeMouvement.objects.get_or_create(
        code_type_mouvement="ENT_TEST",
        defaults={"libelle": "Réception de test", "sens": 1},
    )[0]
    return {"sac": sac, "ciment": ciment, "reception": reception}


@pytest.fixture
def stock_courant(catalogue: dict[str, Any], magasin: Any) -> StockCourant:
    seuil = SeuilStock.objects.create(magasin=magasin, article=catalogue["ciment"])
    return StockCourant.objects.create(seuil_stock=seuil)


@pytest.fixture
def mouvement(
    catalogue: dict[str, Any], stock_courant: StockCourant, fabrique_utilisateur: Any
) -> MouvementStock:
    return MouvementStock.objects.create(
        quantite_saisie=Decimal("10"),
        quantite_base=Decimal("10"),
        type_mouvement=catalogue["reception"],
        article=catalogue["ciment"],
        magasin=stock_courant.seuil_stock.magasin,
        utilisateur=fabrique_utilisateur(role="MAGASINIER"),
        stock_courant=stock_courant,
        unite_mesure=catalogue["sac"],
    )
