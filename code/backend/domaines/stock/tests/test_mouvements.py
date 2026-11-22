"""Mouvements de stock par l'API (EF-STK-01 à 03, 05 à 07, 10) : règles
RG-S1 à RG-S7, RG-S10, RG-S11, idempotence (6.4), droits et périmètres."""

import uuid
from collections.abc import Callable
from datetime import timedelta
from decimal import Decimal
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.identite.models import DroitAccorde, Perimetre
from domaines.organisation.models import (
    Chantier,
    Logement,
    Magasin,
    ParametreChantier,
    Zone,
)
from domaines.referentiels.models import (
    UniteMesure,
)
from domaines.stock.models import Alerte, MouvementStock
from domaines.stock.tests.outils import corps_mouvement, corps_sortie, stock_de

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


# --- Saisie et projection (RG-S1, RG-S2) -------------------------------------------
def test_une_reception_alimente_le_stock_et_cree_le_seuil(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    reponse = client_authentifie().post(
        "/api/mouvements",
        corps_mouvement(chantier_stock, "ENT_RECEPTION", "2", code_unite="T"),
        format="json",
    )
    assert reponse.status_code == 201
    corps = reponse.json()
    assert (corps["quantite_saisie"], corps["quantite_base"], corps["code_unite"]) == (
        "2.000",
        "2000.000",
        "T",
    )
    assert corps["statut_validation"] == "VALIDE"
    stock = stock_de(chantier_stock)
    assert stock.quantite == Decimal("2000")
    assert stock.seuil_stock.actif is False


def test_une_unite_etrangere_a_l_article_est_refusee(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    UniteMesure.objects.create(code_unite="L", libelle="litre", type_unite="VOLUME")
    reponse = client_authentifie().post(
        "/api/mouvements",
        corps_mouvement(chantier_stock, "ENT_RECEPTION", "1", code_unite="L"),
        format="json",
    )
    assert reponse.status_code == 400
    assert "code_unite" in reponse.json()["details"]


def test_un_type_reserve_au_serveur_ne_se_saisit_pas(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    reponse = client_authentifie().post(
        "/api/mouvements",
        corps_mouvement(chantier_stock, "AJU_INVENTAIRE_PLUS", "1"),
        format="json",
    )
    assert reponse.status_code == 400


# --- Idempotence (exigence 6.4, ET-3) -------------------------------------------------
def test_un_envoi_rejoue_n_est_inscrit_qu_une_fois(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    client = client_authentifie()
    corps = corps_mouvement(chantier_stock, "ENT_RECEPTION", "10", uuid=str(uuid.uuid4()))
    assert client.post("/api/mouvements", corps, format="json").status_code == 201
    rejeu = client.post("/api/mouvements", corps, format="json")
    assert rejeu.status_code == 200
    assert rejeu.json()["uuid"] == corps["uuid"]
    assert MouvementStock.objects.count() == 1
    assert stock_de(chantier_stock).quantite == Decimal("10")
    autre = client.post("/api/mouvements", {**corps, "quantite_saisie": "11"}, format="json")
    assert autre.status_code == 409
    assert autre.json()["motif"] == "UUID_DEJA_UTILISE"


# --- Contrôles métier (RG-S3, RG-S4, RG-S6, RG-S7, RG-S10, RG-S11) ----------------------
def test_une_sortie_exige_sa_destination_complete(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    client = client_authentifie()
    sans_logement = client.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "SOR_LOGEMENT", "1"), format="json"
    )
    assert "logement_id_logement" in sans_logement.json()["details"]
    sans_beneficiaire = client.post(
        "/api/mouvements", corps_sortie(chantier_stock, "1", beneficiaire=""), format="json"
    )
    assert "beneficiaire" in sans_beneficiaire.json()["details"]


def test_un_logement_d_un_autre_chantier_est_refuse(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    autre = Chantier.objects.create(code="CH-2", nom="Autre")
    zone = Zone.objects.create(code="Z", nom="Z", type_zone="TRANCHE", chantier=autre)
    ailleurs = Logement.objects.create(
        numero="Z01", zone=zone, type_logement=chantier_stock["logement"].type_logement
    )
    reponse = client_authentifie().post(
        "/api/mouvements",
        corps_sortie(chantier_stock, "1", logement_id_logement=str(ailleurs.pk)),
        format="json",
    )
    assert reponse.status_code == 400


def test_une_perte_exige_un_motif(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    reponse = client_authentifie().post(
        "/api/mouvements", corps_mouvement(chantier_stock, "SOR_PERTE", "1"), format="json"
    )
    assert "motif" in reponse.json()["details"]


def test_une_grosse_sortie_est_effective_mais_a_valider(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    client = client_authentifie()
    client.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "500"), format="json"
    )
    petite = client.post(
        "/api/mouvements", corps_sortie(chantier_stock, "10"), format="json"
    ).json()
    grosse = client.post(
        "/api/mouvements", corps_sortie(chantier_stock, "150"), format="json"
    ).json()
    assert petite["statut_validation"] == "VALIDE"
    assert grosse["statut_validation"] == "A_VALIDER"
    assert stock_de(chantier_stock).quantite == Decimal("340")


def test_le_stock_negatif_est_autorise_et_signale(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    reponse = client_authentifie().post(
        "/api/mouvements", corps_sortie(chantier_stock, "5"), format="json"
    )
    assert reponse.status_code == 201
    stock = stock_de(chantier_stock)
    assert (stock.quantite, stock.niveau_alerte) == (Decimal("-5"), "VIDE")
    assert Alerte.objects.filter(type_alerte="STOCK_NEGATIF", statut="OUVERTE").count() == 1


def test_le_chantier_peut_interdire_le_stock_negatif(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    ParametreChantier.objects.create(
        cle="autoriser_stock_negatif",
        valeur="false",
        type_valeur="BOOLEEN",
        chantier=chantier_stock["magasin"].chantier,
    )
    reponse = client_authentifie().post(
        "/api/mouvements", corps_sortie(chantier_stock, "5"), format="json"
    )
    assert reponse.status_code == 409
    assert reponse.json()["motif"] == "STOCK_INSUFFISANT"


def test_une_saisie_tardive_exige_une_justification(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    client = client_authentifie()
    il_y_a_3_jours = (timezone.now() - timedelta(days=3)).isoformat()
    sans = client.post(
        "/api/mouvements",
        corps_mouvement(chantier_stock, "ENT_RECEPTION", "1", date_operation=il_y_a_3_jours),
        format="json",
    )
    assert "motif" in sans.json()["details"]
    avec = client.post(
        "/api/mouvements",
        corps_mouvement(
            chantier_stock,
            "ENT_RECEPTION",
            "1",
            date_operation=il_y_a_3_jours,
            motif="bon de livraison retrouvé",
        ),
        format="json",
    )
    assert avec.status_code == 201
    demain = (timezone.now() + timedelta(days=1)).isoformat()
    futur = client.post(
        "/api/mouvements",
        corps_mouvement(chantier_stock, "ENT_RECEPTION", "1", date_operation=demain),
        format="json",
    )
    assert "date_operation" in futur.json()["details"]


def test_une_derive_d_horloge_est_signalee_sans_bloquer(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    decale = (timezone.now() - timedelta(minutes=12)).isoformat()
    corps = (
        client_authentifie()
        .post(
            "/api/mouvements",
            corps_mouvement(chantier_stock, "ENT_RECEPTION", "1", horodatage_appareil=decale),
            format="json",
        )
        .json()
    )
    assert corps["derive_horloge"] is True


# --- Seuils et lectures (EF-STK-05 à 07, EF-STK-10) --------------------------------------
def test_definir_un_seuil_reclasse_le_stock_et_ouvre_une_alerte(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    client = client_authentifie()
    client.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "20"), format="json"
    )
    url = (
        f"/api/magasins/{chantier_stock['magasin'].pk}/articles/{chantier_stock['ciment'].pk}/seuil"
    )
    assert (
        client.put(url, {"seuil_minimal": "80", "seuil_critique": "30"}, format="json").status_code
        == 204
    )
    assert stock_de(chantier_stock).niveau_alerte == "CRITIQUE"
    alertes = client.get("/api/stock/alertes").json()
    assert [a["type_alerte"] for a in alertes] == ["SEUIL_CRITIQUE"]
    incoherent = client.put(url, {"seuil_minimal": "10", "seuil_critique": "30"}, format="json")
    assert incoherent.status_code == 400


def test_la_ligne_de_stock_a_la_forme_de_l_ecran(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    client = client_authentifie()
    client.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "20"), format="json"
    )
    ligne = client.get(f"/api/magasins/{chantier_stock['magasin'].pk}/stock").json()[0]
    assert ligne["article"]["unite_base"]["code_unite"] == "KG"
    assert ligne["stock"]["quantite"] == "20.000"
    assert set(ligne["seuil"]) == {"id_seuil", "seuil_minimal", "seuil_critique", "actif"}
    arbre = client.get("/api/stock/arborescence").json()
    assert arbre[0]["enfants"][0]["nombreArticles"] == 1


def test_l_historique_se_filtre(client_authentifie: Client, chantier_stock: dict[str, Any]) -> None:
    client = client_authentifie()
    client.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "20"), format="json"
    )
    client.post("/api/mouvements", corps_sortie(chantier_stock, "2"), format="json")
    vers_logement = client.get(
        "/api/mouvements", {"logement": str(chantier_stock["logement"].pk)}
    ).json()
    assert [m["type_mouvement_code_type_mouvement"] for m in vers_logement] == ["SOR_LOGEMENT"]
    url = f"/api/magasins/{chantier_stock['magasin'].pk}/articles/{chantier_stock['ciment'].pk}/mouvements"
    assert len(client.get(url).json()) == 2


# --- Droits et périmètres ---------------------------------------------------------------
def test_sans_le_droit_de_creer_la_saisie_est_interdite(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    reponse = client_authentifie("TECHNICIEN").post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "1"), format="json"
    )
    assert reponse.status_code == 403


def test_un_magasin_hors_perimetre_est_introuvable(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    autre_magasin = Magasin.objects.create(
        code="MAG-2", nom="Autre magasin", chantier=chantier_stock["magasin"].chantier
    )
    perimetre = Perimetre.objects.create(libelle="Autre magasin", magasin=autre_magasin)
    DroitAccorde.objects.create(
        role_id="MAGASINIER", permission_id="api.stock.lire", portee="PERIMETRE"
    )
    client = client_authentifie("MAGASINIER", perimetre=perimetre)
    assert client.get(f"/api/magasins/{chantier_stock['magasin'].pk}/stock").status_code == 404
    assert client.get(f"/api/magasins/{autre_magasin.pk}/stock").status_code == 200
