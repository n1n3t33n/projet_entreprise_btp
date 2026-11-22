"""Inventaire contradictoire (EF-STK-08, SQ-4, RG-S9, RG-D11) et import du
stock de départ (EF-ADM-02)."""

from collections.abc import Callable
from decimal import Decimal
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.identite.models import JournalAudit
from domaines.referentiels.models import RegleValidation
from domaines.stock.models import MouvementStock
from domaines.stock.tests.outils import corps_mouvement, stock_de

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def inventaire(client_authentifie: Client, chantier_stock: dict[str, Any]) -> dict[str, Any]:
    """Stock théorique de 200 kg ; règle RG-S9 : double validation à 5 %."""
    RegleValidation.objects.create(
        type_evenement="ECART_INVENTAIRE",
        champ_teste="ecart_pourcent",
        operateur="SUPERIEUR_EGAL",
        valeur_seuil=Decimal("5"),
    )
    compteur, valideur, second = client_authentifie(), client_authentifie(), client_authentifie()
    compteur.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "200"), format="json"
    )
    ouvert = compteur.post(
        "/api/inventaires",
        {"magasin_id_magasin": str(chantier_stock["magasin"].pk)},
        format="json",
    ).json()
    return {
        **chantier_stock,
        "compteur": compteur,
        "valideur": valideur,
        "second": second,
        "id": ouvert["id_inventaire"],
        "ligne": ouvert["lignes"][0]["id_ligne"],
        "ouvert": ouvert,
    }


def _compter(inv: dict[str, Any], quantite: str) -> Any:
    url = f"/api/inventaires/{inv['id']}/lignes/{inv['ligne']}"
    return inv["compteur"].put(url, {"quantite_comptee": quantite}, format="json")


def _soumettre(inv: dict[str, Any]) -> Any:
    return inv["compteur"].post(f"/api/inventaires/{inv['id']}/soumission")


def _valider_ligne(inv: dict[str, Any], client: APIClient, decision: str, **champs: Any) -> Any:
    url = f"/api/inventaires/{inv['id']}/lignes/{inv['ligne']}/validation"
    return client.post(url, {"decision": decision, **champs}, format="json")


def test_l_ouverture_fige_la_quantite_theorique(inventaire: dict[str, Any]) -> None:
    ouvert = inventaire["ouvert"]
    assert ouvert["statut"] == "EN_COURS"
    assert ouvert["lignes"][0]["quantite_theorique"] == "200.000"
    second = inventaire["compteur"].post(
        "/api/inventaires",
        {"magasin_id_magasin": str(inventaire["magasin"].pk)},
        format="json",
    )
    assert second.status_code == 409


def test_un_petit_ecart_est_ajuste_des_la_premiere_validation(inventaire: dict[str, Any]) -> None:
    ligne = _compter(inventaire, "196").json()
    assert ligne["ecart"] == "-4.000"
    assert JournalAudit.objects.filter(action="COMPTAGE_INVENTAIRE").count() == 1
    assert _soumettre(inventaire).json()["statut"] == "A_VALIDER"
    detail = _valider_ligne(inventaire, inventaire["valideur"], "ACCEPTE").json()
    assert detail["statut"] == "VALIDE"
    assert detail["date_fin"] is not None
    ajustement = MouvementStock.objects.get(type_mouvement_id="AJU_INVENTAIRE_MOINS")
    assert ajustement.statut_validation == "ENREGISTRE"
    assert stock_de(inventaire).quantite == Decimal("196")


def test_un_gros_ecart_exige_une_seconde_validation(inventaire: dict[str, Any]) -> None:
    _compter(inventaire, "170")  # 15 % d'écart
    _soumettre(inventaire)
    detail = _valider_ligne(inventaire, inventaire["valideur"], "ACCEPTE").json()
    uuid_ajustement = detail["lignes"][0]["uuid_ajustement"]
    assert MouvementStock.objects.get(uuid=uuid_ajustement).statut_validation == "A_VALIDER"
    url = f"/api/mouvements/{uuid_ajustement}/validation"
    par_premier = inventaire["valideur"].post(url, {"decision": "ACCEPTE"}, format="json")
    par_compteur = inventaire["compteur"].post(url, {"decision": "ACCEPTE"}, format="json")
    assert par_premier.json()["motif"] == "SEPARATION_DES_TACHES"
    assert par_compteur.json()["motif"] == "SEPARATION_DES_TACHES"
    par_second = inventaire["second"].post(url, {"decision": "ACCEPTE"}, format="json")
    assert par_second.json()["statut_validation"] == "VALIDE"


def test_le_compteur_ne_valide_pas_son_ecart(inventaire: dict[str, Any]) -> None:
    _compter(inventaire, "190")
    _soumettre(inventaire)
    reponse = _valider_ligne(inventaire, inventaire["compteur"], "ACCEPTE")
    assert reponse.status_code == 403


def test_un_refus_renvoie_la_ligne_au_comptage(inventaire: dict[str, Any]) -> None:
    _compter(inventaire, "150")
    _soumettre(inventaire)
    assert _valider_ligne(inventaire, inventaire["valideur"], "REFUSE").status_code == 400
    detail = _valider_ligne(inventaire, inventaire["valideur"], "REFUSE", motif="recompter").json()
    assert detail["statut"] == "EN_COURS"
    assert detail["lignes"][0]["statut"] == "A_COMPTER"
    assert not MouvementStock.objects.filter(ligne_inventaire__isnull=False).exists()


def test_on_ne_soumet_pas_un_comptage_incomplet(inventaire: dict[str, Any]) -> None:
    reponse = _soumettre(inventaire)
    assert reponse.status_code == 409
    assert reponse.json()["motif"] == "COMPTAGE_INCOMPLET"


# --- Import du stock de départ (EF-ADM-02) -----------------------------------------------
def test_le_stock_de_depart_s_importe_avec_ses_seuils(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    client = client_authentifie()
    contenu = (
        "magasin;article;quantite;seuil_minimal;seuil_critique\n"
        f"{chantier_stock['magasin'].code};A1;250,5;80;30\n"
        f"{chantier_stock['magasin'].code};A1;10;;\n"
        "INCONNU;A1;5;;\n"
    )
    rapport = client.post(
        "/api/import/analyse", {"cible": "stock", "contenu": contenu}, format="json"
    ).json()
    assert [ligne["erreur"] for ligne in rapport["lignes"]] == [
        None,
        f"« {chantier_stock['magasin'].code} / A1 » apparaît deux fois dans le fichier",
        "le magasin « INCONNU » n'existe pas",
    ]
    resultat = client.post(
        "/api/import/confirmation", {"cible": "stock", "contenu": contenu}, format="json"
    )
    assert resultat.json()["nombre_importees"] == 1
    stock = stock_de(chantier_stock)
    assert (stock.quantite, stock.seuil_stock.actif) == (Decimal("250.5"), True)
    reimport = client.post(
        "/api/import/analyse", {"cible": "stock", "contenu": contenu}, format="json"
    ).json()
    assert "déjà enregistré" in reimport["lignes"][0]["erreur"]
