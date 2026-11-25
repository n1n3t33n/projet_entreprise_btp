"""Traçabilité des saisies mobiles (cahier des charges § 9, Q-BD, I-51) : le
journal immuable garde l'appareil et la version de l'application ; une
saisie web n'en porte aucun, et rien ne fuit d'une requête à la suivante."""

import uuid
from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.referentiels.models import Article, TypeMouvement, UniteMesure
from domaines.stock.models import MouvementStock

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def corps(magasin: Any) -> Callable[[], dict[str, Any]]:
    sac = UniteMesure.objects.create(code_unite="SAC", libelle="sac", type_unite="MASSE")
    article = Article.objects.create(
        code="A1", designation="Ciment", origine="ACHAT", unite_mesure=sac
    )
    TypeMouvement.objects.create(code_type_mouvement="ENT_RECEPTION", libelle="Réception", sens=1)

    def construire() -> dict[str, Any]:
        return {
            "uuid": str(uuid.uuid4()),
            "magasin_id_magasin": str(magasin.pk),
            "article_id_article": str(article.pk),
            "type_mouvement_code_type_mouvement": "ENT_RECEPTION",
            "quantite_saisie": "5",
        }

    return construire


def test_une_saisie_mobile_garde_son_appareil_et_sa_version(
    client_mobile: Client, client_authentifie: Client, corps: Callable[[], dict[str, Any]]
) -> None:
    mobile = client_mobile()
    appareil = mobile.appareil  # type: ignore[attr-defined]
    par_route = corps()
    mobile.post("/api/mouvements", par_route, format="json")
    par_lot = corps()
    lot = {
        "id_lot": str(uuid.uuid4()),
        "evenements": [
            {
                "uuid": par_lot.pop("uuid"),
                "type": "MOUVEMENT_STOCK",
                "charge_utile": par_lot,
            }
        ],
    }
    reponse = mobile.post("/api/synchronisation/lots", lot, format="json")
    assert reponse.json()["resultats"][0]["statut"] == "ACCEPTE"
    web = corps()
    client_authentifie().post("/api/mouvements", web, format="json")

    mobiles = MouvementStock.objects.exclude(uuid=web["uuid"])
    assert mobiles.count() == 2
    assert set(mobiles.values_list("appareil_id", "version_application")) == {
        (appareil.pk, appareil.version_application)
    }
    saisie_web = MouvementStock.objects.get(uuid=web["uuid"])
    assert (saisie_web.appareil_id, saisie_web.version_application) == (None, None)
