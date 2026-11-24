"""Pilotage du stock pour le tableau de bord (EF-DSH-04) : synthèse par
niveau et derniers mouvements, aux formes de features/pilotage/api/dto.ts."""

from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.stock.tests.outils import corps_mouvement

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def mouvements(client_authentifie: Client, chantier_stock: dict[str, Any]) -> APIClient:
    client = client_authentifie()
    for quantite in ("10", "20", "30"):
        client.post(
            "/api/mouvements",
            corps_mouvement(chantier_stock, "ENT_RECEPTION", quantite),
            format="json",
        )
    client.post(
        "/api/mouvements",
        corps_mouvement(chantier_stock, "SOR_PERTE", "100", motif="Casse"),
        format="json",
    )
    return client


def test_la_synthese_suit_la_regle_de_l_ecran(mouvements: APIClient) -> None:
    synthese = mouvements.get("/api/pilotage/stock/synthese").json()
    # 60 - 100 : stock négatif, donc niveau VIDE, compté « critique ».
    assert synthese == {
        "nombre_articles": 1,
        "nombre_critique": 1,
        "nombre_vigilance": 0,
        "nombre_negatif": 1,
    }


def test_les_mouvements_recents_portent_l_article_et_son_niveau(mouvements: APIClient) -> None:
    recents = mouvements.get("/api/pilotage/stock/mouvements-recents", {"limite": 2}).json()
    assert len(recents) == 2
    assert recents[0]["type_mouvement_code_type_mouvement"] == "SOR_PERTE"
    assert recents[0]["libelle_article"] == "Ciment"
    assert recents[0]["code_article"] == "A1"
    assert recents[0]["niveau_alerte_article"] == "VIDE"
    assert len(mouvements.get("/api/pilotage/stock/mouvements-recents").json()) == 4


def test_les_mouvements_recents_sont_plafonnes(mouvements: APIClient) -> None:
    reponse = mouvements.get("/api/pilotage/stock/mouvements-recents", {"limite": 500})
    assert reponse.status_code == 200
    assert len(reponse.json()) == 4
