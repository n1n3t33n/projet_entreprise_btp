"""API du domaine « référentiels » : catalogue, corps d'état, cycle des
versions de gamme (EF-REF-09), règles de validation (EF-REF-08)."""

from collections.abc import Callable
from decimal import Decimal
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.organisation.models import TypeLogement
from domaines.referentiels.models import (
    CategorieArticle,
    CorpsEtat,
    EtapeModele,
    Gamme,
    UniteMesure,
)

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def unite(db: Any) -> UniteMesure:
    return UniteMesure.objects.create(code_unite="SAC", libelle="sac", type_unite="MASSE")


@pytest.fixture
def gamme_active(db: Any) -> Gamme:
    villa = TypeLogement.objects.create(code_type="VILLA3", libelle="Villa 3 pièces")
    corps = CorpsEtat.objects.create(code_corps_etat="GO", libelle="Gros œuvre", ordre=1)
    gamme = Gamme.objects.create(
        version=1, libelle="Villa standard", statut="ACTIVE", type_logement=villa
    )
    for ordre, (code, poids) in enumerate([("V3-EM-01", 60), ("V3-EM-02", 40)], start=1):
        EtapeModele.objects.create(
            code=code,
            libelle=f"Étape {ordre}",
            ordre=ordre,
            poids=Decimal(poids),
            controle_requis=False,
            gamme=gamme,
            corps_etat=corps,
        )
    return gamme


# --- Catalogue ------------------------------------------------------------------
def test_les_familles_sont_plates(client_authentifie: Client) -> None:
    CategorieArticle.objects.create(code_categorie="GO-CIM", libelle="Ciment")
    corps = client_authentifie().get("/api/referentiels/categories").json()
    assert corps == [{"code_categorie": "GO-CIM", "libelle": "Ciment", "code_parent": None}]


def test_un_article_se_cree_et_un_code_barre_vide_devient_nul(
    client_authentifie: Client, unite: UniteMesure
) -> None:
    reponse = client_authentifie().post(
        "/api/referentiels/articles",
        {
            "code": "A0001",
            "designation": "Ciment",
            "origine": "ACHAT",
            "code_barre": "",
            "actif": True,
            "unite_mesure_code_unite": "SAC",
        },
        format="json",
    )
    assert reponse.status_code == 201
    assert reponse.json()["code_barre"] is None
    assert reponse.json()["categorie_article_code_categorie"] is None


def test_une_origine_hors_liste_est_refusee(client_authentifie: Client, unite: UniteMesure) -> None:
    reponse = client_authentifie().post(
        "/api/referentiels/articles",
        {
            "code": "A0002",
            "designation": "X",
            "origine": "VOL",
            "actif": True,
            "unite_mesure_code_unite": "SAC",
        },
        format="json",
    )
    assert reponse.status_code == 400


def test_le_technicien_lit_le_catalogue_sans_pouvoir_le_modifier(
    client_authentifie: Client, unite: UniteMesure
) -> None:
    from domaines.identite.models import DroitAccorde

    DroitAccorde.objects.create(
        role_id="TECHNICIEN", permission_id="api.articles.lire", portee="GLOBALE"
    )
    client = client_authentifie("TECHNICIEN")
    assert client.get("/api/referentiels/articles").status_code == 200
    creation = client.post("/api/referentiels/articles", {}, format="json")
    assert creation.status_code == 403


# --- Corps d'état ------------------------------------------------------------------
def test_un_corps_d_etat_existant_n_est_pas_ecrase_par_une_creation(
    client_authentifie: Client,
) -> None:
    CorpsEtat.objects.create(code_corps_etat="GO", libelle="Gros œuvre", ordre=1)
    reponse = client_authentifie().post(
        "/api/gammes/corps-etat",
        {"code_corps_etat": "GO", "libelle": "Autre", "ordre": 9},
        format="json",
    )
    assert reponse.status_code == 400
    assert CorpsEtat.objects.get(pk="GO").libelle == "Gros œuvre"


def test_un_corps_d_etat_se_modifie_sans_changer_de_code(client_authentifie: Client) -> None:
    CorpsEtat.objects.create(code_corps_etat="GO", libelle="Gros œuvre", ordre=1)
    reponse = client_authentifie().put(
        "/api/gammes/corps-etat/GO",
        {"code_corps_etat": "GO", "libelle": "Gros œuvre", "ordre": 1, "couleur": "#6c8ebf"},
        format="json",
    )
    assert reponse.status_code == 200
    assert reponse.json()["couleur"] == "#6c8ebf"


# --- Gammes : versions, brouillon, publication, archivage -----------------------------
def test_la_liste_des_gammes_compte_les_etapes_et_le_poids(
    client_authentifie: Client, gamme_active: Gamme
) -> None:
    corps = client_authentifie().get("/api/gammes").json()[0]
    assert corps["nombre_etapes"] == 2
    assert Decimal(corps["poids_total"]) == Decimal(100)
    assert corps["libelle_type_logement"] == "Villa 3 pièces"


def test_une_gamme_publiee_ne_se_modifie_pas(
    client_authentifie: Client, gamme_active: Gamme
) -> None:
    reponse = client_authentifie().put(
        f"/api/gammes/{gamme_active.pk}/etapes", {"etapes": []}, format="json"
    )
    assert reponse.status_code == 409
    assert reponse.json()["motif"] == "GAMME_PUBLIEE"


def test_cycle_complet_d_une_nouvelle_version(
    client_authentifie: Client, gamme_active: Gamme
) -> None:
    client = client_authentifie()
    # 1. Nouvelle version : brouillon v2, étapes copiées sous des codes propres.
    creation = client.post(f"/api/gammes/{gamme_active.pk}/versions")
    assert creation.status_code == 201
    brouillon = creation.json()
    assert (brouillon["version"], brouillon["statut"]) == (2, "BROUILLON")
    etapes = client.get(f"/api/gammes/{brouillon['id_gamme']}/etapes").json()
    assert [e["code"] for e in etapes] == ["V3-EM-01~V2", "V3-EM-02~V2"]

    # 2. Un seul brouillon à la fois par type de logement.
    second = client.post(f"/api/gammes/{gamme_active.pk}/versions")
    assert second.status_code == 409

    # 3. Les étapes du brouillon se remplacent.
    modifiees = client.put(
        f"/api/gammes/{brouillon['id_gamme']}/etapes",
        {
            "etapes": [
                {
                    "code": "V3-EM-01~V2",
                    "libelle": "Fondations",
                    "ordre": 1,
                    "poids": 100,
                    "controle_requis": True,
                    "corps_etat_code_corps_etat": "GO",
                },
            ]
        },
        format="json",
    )
    assert modifiees.status_code == 200
    assert len(modifiees.json()) == 1

    # 4. Publier : le brouillon devient actif, l'ancienne version est archivée.
    publiee = client.post(f"/api/gammes/{brouillon['id_gamme']}/publication")
    assert publiee.status_code == 200
    assert publiee.json()["statut"] == "ACTIVE"
    assert publiee.json()["date_activation"] is not None
    gamme_active.refresh_from_db()
    assert gamme_active.statut == "ARCHIVEE"

    # 5. Archiver la version active.
    archivee = client.post(f"/api/gammes/{brouillon['id_gamme']}/archivage")
    assert archivee.json()["statut"] == "ARCHIVEE"


def test_un_code_d_etape_pris_par_une_autre_gamme_est_refuse(
    client_authentifie: Client, gamme_active: Gamme
) -> None:
    client = client_authentifie()
    brouillon = client.post(f"/api/gammes/{gamme_active.pk}/versions").json()
    reponse = client.put(
        f"/api/gammes/{brouillon['id_gamme']}/etapes",
        {
            "etapes": [
                {
                    "code": "V3-EM-01",
                    "libelle": "Doublon",
                    "ordre": 1,
                    "poids": 10,
                    "controle_requis": False,
                    "corps_etat_code_corps_etat": "GO",
                },
            ]
        },
        format="json",
    )
    assert reponse.status_code == 400
    assert "etapes" in reponse.json()["details"]


def test_publier_demande_le_droit_valider(client_authentifie: Client, gamme_active: Gamme) -> None:
    from domaines.identite.models import DroitAccorde

    DroitAccorde.objects.create(
        role_id="CHEF_CHANTIER", permission_id="api.gammes.lire", portee="GLOBALE"
    )
    reponse = client_authentifie("CHEF_CHANTIER").post(f"/api/gammes/{gamme_active.pk}/publication")
    assert reponse.status_code == 403


# --- Règles de validation (EF-REF-08) -------------------------------------------------
def test_une_regle_se_cree_et_l_operateur_est_controle(client_authentifie: Client) -> None:
    client = client_authentifie()
    valide = client.post(
        "/api/parametrage/regles",
        {
            "type_evenement": "ECART_INVENTAIRE",
            "champ_teste": "ecart_pourcent",
            "operateur": "SUPERIEUR_EGAL",
            "valeur_seuil": "5.000",
            "delai_heures": None,
        },
        format="json",
    )
    assert valide.status_code == 201
    assert valide.json()["valeur_seuil"] == "5.000"
    invalide = client.post(
        "/api/parametrage/regles",
        {"type_evenement": "ECART_INVENTAIRE", "champ_teste": "x", "operateur": "ENVIRON"},
        format="json",
    )
    assert invalide.status_code == 400
    assert "operateur" in invalide.json()["details"]
