"""Fixtures du domaine stock : un petit catalogue et un mouvement prêt à
l'emploi, construits directement en base (les services sont testés à part)."""

from decimal import Decimal
from typing import Any

import pytest

from domaines.organisation.models import Logement, Magasin, TypeLogement, Zone
from domaines.referentiels.models import (
    Article,
    Conditionnement,
    CorpsEtat,
    RegleValidation,
    TypeMouvement,
    UniteMesure,
)
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


@pytest.fixture
def chantier_stock(magasin: Magasin) -> dict[str, Any]:
    kg = UniteMesure.objects.create(code_unite="KG", libelle="kg", type_unite="MASSE")
    tonne = UniteMesure.objects.create(code_unite="T", libelle="tonne", type_unite="MASSE")
    ciment = Article.objects.create(
        code="A1", designation="Ciment", origine="ACHAT", unite_mesure=kg
    )
    Conditionnement.objects.create(article=ciment, unite_mesure=tonne, facteur_conversion=1000)
    villa = TypeLogement.objects.create(code_type="VILLA3", libelle="Villa 3 pièces")
    zone = Zone.objects.create(
        code="A", nom="Îlot A", type_zone="TRANCHE", chantier=magasin.chantier
    )
    logement = Logement.objects.create(numero="A01", zone=zone, type_logement=villa)
    TypeMouvement.objects.create(code_type_mouvement="ENT_RECEPTION", libelle="Réception", sens=1)
    TypeMouvement.objects.create(
        code_type_mouvement="SOR_LOGEMENT",
        libelle="Sortie",
        sens=-1,
        destination_obligatoire=True,
    )
    TypeMouvement.objects.create(
        code_type_mouvement="SOR_PERTE", libelle="Perte", sens=-1, motif_obligatoire=True
    )
    CorpsEtat.objects.create(code_corps_etat="GO", libelle="Gros œuvre", ordre=1)
    RegleValidation.objects.create(
        type_evenement="MOUVEMENT_STOCK",
        champ_teste="quantite_base",
        operateur="SUPERIEUR_EGAL",
        valeur_seuil=Decimal("100"),
    )
    return {"magasin": magasin, "ciment": ciment, "logement": logement}
