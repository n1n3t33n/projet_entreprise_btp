"""Réception des lots (SQ-2, EF-SYN-01 à 06, ET-3, Q-AE à Q-AM)."""

import gzip
import json
import uuid
from collections.abc import Callable
from datetime import timedelta
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.identite.models import DroitAccorde
from domaines.referentiels.models import Article, TypeMouvement, UniteMesure
from domaines.stock.models import MouvementStock
from domaines.synchronisation.models import AnomalieSynchronisation, LotSynchronisation

pytestmark = pytest.mark.django_db

URL = "/api/synchronisation/lots"
Client = Callable[..., APIClient]


@pytest.fixture
def ciment(magasin: Any) -> dict[str, Any]:
    sac = UniteMesure.objects.create(code_unite="SAC", libelle="sac", type_unite="MASSE")
    article = Article.objects.create(
        code="A1", designation="Ciment", origine="ACHAT", unite_mesure=sac
    )
    TypeMouvement.objects.create(code_type_mouvement="ENT_RECEPTION", libelle="Réception", sens=1)
    TypeMouvement.objects.create(
        code_type_mouvement="SOR_PERTE", libelle="Perte", sens=-1, motif_obligatoire=True
    )
    return {"magasin": magasin, "article": article}


def _mouvement(ciment: dict[str, Any], type_mouvement: str, quantite: str, **champs: Any) -> dict:
    return {
        "uuid": str(champs.pop("uuid", uuid.uuid4())),
        "type": "MOUVEMENT_STOCK",
        "horodatage_appareil": timezone.now().isoformat(),
        "charge_utile": {
            "magasin_id_magasin": str(ciment["magasin"].pk),
            "article_id_article": str(ciment["article"].pk),
            "type_mouvement_code_type_mouvement": type_mouvement,
            "quantite_saisie": quantite,
            **champs,
        },
    }


def _lot(*evenements: dict, **champs: Any) -> dict:
    return {
        "id_lot": str(champs.pop("id_lot", uuid.uuid4())),
        "evenements": list(evenements),
        **champs,
    }


def _statuts(reponse: Any) -> list[str]:
    return [r["statut"] for r in reponse.data["resultats"]]


def _par_uuid(reponse: Any) -> dict[str, dict[str, Any]]:
    """Le téléphone rapproche chaque résultat par ``uuid_evenement`` : l'ordre
    de la réponse n'est pas garanti."""
    return {str(r["uuid_evenement"]): r for r in reponse.data["resultats"]}


def test_un_lot_est_rejoue_par_les_services_du_stock(
    client_mobile: Client, ciment: dict[str, Any]
) -> None:
    client = client_mobile()
    corps = _lot(
        _mouvement(ciment, "ENT_RECEPTION", "10"),
        _mouvement(ciment, "SOR_PERTE", "4", motif="Sac éventré"),
    )
    reponse = client.post(URL, corps, format="json")
    assert reponse.status_code == 201
    assert _statuts(reponse) == ["ACCEPTE", "ACCEPTE"]
    assert reponse.data["nombre_acceptes"] == 2
    assert MouvementStock.objects.count() == 2
    appareil = client.appareil  # type: ignore[attr-defined]
    appareil.refresh_from_db()
    assert appareil.derniere_synchronisation is not None


def test_un_lot_renvoye_rend_les_memes_resultats_sans_retraiter(
    client_mobile: Client, ciment: dict[str, Any]
) -> None:
    client = client_mobile()
    corps = _lot(_mouvement(ciment, "ENT_RECEPTION", "10"))
    assert client.post(URL, corps, format="json").status_code == 201
    reponse = client.post(URL, corps, format="json")
    assert reponse.status_code == 200
    assert _statuts(reponse) == ["ACCEPTE"]
    assert MouvementStock.objects.count() == 1


def test_un_evenement_deja_recu_n_est_pas_applique_deux_fois(
    client_mobile: Client, ciment: dict[str, Any]
) -> None:
    client = client_mobile()
    evenement = _mouvement(ciment, "ENT_RECEPTION", "10")
    client.post(URL, _lot(evenement), format="json")
    reponse = client.post(URL, _lot(evenement), format="json")
    assert reponse.status_code == 201
    assert _statuts(reponse) == ["DEJA_RECU"]
    assert MouvementStock.objects.count() == 1


def test_un_rejet_n_empeche_pas_les_autres_evenements(
    client_mobile: Client, ciment: dict[str, Any]
) -> None:
    client = client_mobile()
    inconnu: dict[str, Any] = {"uuid": str(uuid.uuid4()), "type": "INCONNU", "charge_utile": {}}
    sans_motif = _mouvement(ciment, "SOR_PERTE", "1")  # motif obligatoire manquant
    valide = _mouvement(ciment, "ENT_RECEPTION", "5")
    reponse = client.post(URL, _lot(inconnu, sans_motif, valide), format="json")
    resultats = _par_uuid(reponse)
    assert resultats[inconnu["uuid"]]["code_rejet"] == "TYPE_INCONNU"
    assert resultats[sans_motif["uuid"]]["statut"] == "REJETE"
    assert resultats[sans_motif["uuid"]]["code_rejet"] is not None
    assert resultats[valide["uuid"]]["statut"] == "ACCEPTE"
    assert reponse.data["nombre_rejetes"] == 2
    assert MouvementStock.objects.count() == 1
    assert AnomalieSynchronisation.objects.filter(type_anomalie="REJET_REGLE").count() == 2


def test_un_stock_devenu_negatif_est_signale(client_mobile: Client, ciment: dict[str, Any]) -> None:
    client = client_mobile()
    reponse = client.post(
        URL, _lot(_mouvement(ciment, "SOR_PERTE", "3", motif="Casse")), format="json"
    )
    assert _statuts(reponse) == ["ACCEPTE"]
    anomalie = AnomalieSynchronisation.objects.get(type_anomalie="ECART_QUANTITE")
    assert anomalie.resultat_evenement is not None
    assert "Ciment" in anomalie.description


def test_une_operation_sans_droit_est_rejetee(
    client_mobile: Client, ciment: dict[str, Any]
) -> None:
    DroitAccorde.objects.create(
        role_id="TECHNICIEN", permission_id="api.synchronisation.creer", portee="GLOBALE"
    )
    client = client_mobile(role="TECHNICIEN")
    reponse = client.post(URL, _lot(_mouvement(ciment, "ENT_RECEPTION", "1")), format="json")
    assert reponse.status_code == 201
    assert reponse.data["resultats"][0]["code_rejet"] == "DROIT_INSUFFISANT"


def test_la_synchronisation_exige_un_jeton_mobile(
    client_authentifie: Client, ciment: dict[str, Any]
) -> None:
    reponse = client_authentifie().post(
        URL, _lot(_mouvement(ciment, "ENT_RECEPTION", "1")), format="json"
    )
    assert reponse.status_code == 403


def test_la_derive_d_horloge_est_signalee(client_mobile: Client, ciment: dict[str, Any]) -> None:
    client = client_mobile()
    envoi = (timezone.now() - timedelta(minutes=30)).isoformat()
    corps = _lot(_mouvement(ciment, "ENT_RECEPTION", "1"), horodatage_envoi=envoi)
    client.post(URL, corps, format="json")
    anomalie = AnomalieSynchronisation.objects.get(type_anomalie="DERIVE_HORLOGE")
    assert anomalie.resultat_evenement is None


def test_un_lot_compresse_est_accepte(client_mobile: Client, ciment: dict[str, Any]) -> None:
    client = client_mobile()
    brut = gzip.compress(json.dumps(_lot(_mouvement(ciment, "ENT_RECEPTION", "2"))).encode())
    reponse = client.post(URL, brut, content_type="application/json", HTTP_CONTENT_ENCODING="gzip")
    assert reponse.status_code == 201
    assert _statuts(reponse) == ["ACCEPTE"]


def test_un_corps_compresse_illisible_est_refuse(client_mobile: Client) -> None:
    reponse = client_mobile().post(
        URL, b"pas du gzip", content_type="application/json", HTTP_CONTENT_ENCODING="gzip"
    )
    assert reponse.status_code == 400


def test_un_lot_d_un_autre_appareil_est_refuse(
    client_mobile: Client, ciment: dict[str, Any]
) -> None:
    corps = _lot(_mouvement(ciment, "ENT_RECEPTION", "1"))
    client_mobile().post(URL, corps, format="json")
    reponse = client_mobile().post(URL, corps, format="json")
    assert reponse.status_code == 409
    assert LotSynchronisation.objects.count() == 1


def test_un_lot_trop_gros_est_refuse(client_mobile: Client, ciment: dict[str, Any]) -> None:
    corps = _lot(*[_mouvement(ciment, "ENT_RECEPTION", "1") for _ in range(201)])
    assert client_mobile().post(URL, corps, format="json").status_code == 400


def test_une_decision_sur_un_mouvement_inconnu_est_un_conflit(client_mobile: Client) -> None:
    decision = {
        "uuid": str(uuid.uuid4()),
        "type": "DECISION_MOUVEMENT",
        "charge_utile": {"uuid_mouvement": str(uuid.uuid4()), "decision": "ACCEPTE"},
    }
    reponse = client_mobile().post(URL, _lot(decision), format="json")
    assert reponse.data["resultats"][0]["code_rejet"] == "INTROUVABLE"
    assert AnomalieSynchronisation.objects.get().type_anomalie == "CONFLIT_VERSION"
