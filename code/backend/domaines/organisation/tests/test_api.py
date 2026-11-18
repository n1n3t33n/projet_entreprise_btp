"""API du domaine « organisation » : droits exigés, formes rendues aux écrans,
erreurs de saisie (EF-REF-01, EF-REF-02, EF-REF-07)."""

from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.organisation.models import Chantier, Logement, ParametreChantier, TypeLogement, Zone

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def arbre(chantier: Chantier) -> dict[str, Any]:
    villa = TypeLogement.objects.create(code_type="VILLA3", libelle="Villa 3 pièces")
    zone = Zone.objects.create(code="A", nom="Îlot A", type_zone="TRANCHE", chantier=chantier)
    logement = Logement.objects.create(numero="A01", zone=zone, type_logement=villa)
    return {"chantier": chantier, "villa": villa, "zone": zone, "logement": logement}


# --- Droits -------------------------------------------------------------------
def test_sans_jeton_la_liste_des_chantiers_est_refusee(client_api: APIClient) -> None:
    assert client_api.get("/api/referentiels/chantiers").status_code == 401


def test_sans_le_droit_la_liste_des_chantiers_est_interdite(client_authentifie: Client) -> None:
    # L'acquéreur ne reçoit aucun droit « api.chantiers » (ni par la migration,
    # ni par défaut) : la vue le refuse.
    reponse = client_authentifie("ACQUEREUR").get("/api/referentiels/chantiers")
    assert reponse.status_code == 403


def test_l_administrateur_recoit_les_permissions_du_domaine_par_amorcage() -> None:
    from domaines.identite.models import DroitAccorde

    codes = set(
        DroitAccorde.objects.filter(role_id="ADMINISTRATEUR").values_list(
            "permission_id", flat=True
        )
    )
    assert {"api.chantiers.lire", "api.parametres.modifier", "api.logements.creer"} <= codes


# --- Chantiers et arborescence --------------------------------------------------
def test_la_liste_des_chantiers_a_la_forme_de_l_ecran(
    client_authentifie: Client, chantier: Chantier
) -> None:
    corps = client_authentifie().get("/api/referentiels/chantiers").json()
    assert corps == [
        {
            "id_chantier": str(chantier.pk),
            "code": "CH-TEST",
            "nom": "Chantier de test",
            "programme": "",
            "date_debut": None,
            "statut": "ACTIF",
        }
    ]


def test_un_chantier_se_modifie(client_authentifie: Client, chantier: Chantier) -> None:
    reponse = client_authentifie().put(
        f"/api/referentiels/chantiers/{chantier.pk}",
        {"code": "CH-TEST", "nom": "Nouveau nom", "statut": "INACTIF"},
        format="json",
    )
    assert reponse.status_code == 200
    chantier.refresh_from_db()
    assert (chantier.nom, chantier.statut) == ("Nouveau nom", "INACTIF")


def test_un_statut_de_chantier_hors_liste_est_refuse(
    client_authentifie: Client, chantier: Chantier
) -> None:
    reponse = client_authentifie().put(
        f"/api/referentiels/chantiers/{chantier.pk}",
        {"code": "CH-TEST", "nom": "X", "statut": "INVENTE"},
        format="json",
    )
    assert reponse.status_code == 400
    assert reponse.json()["motif"] == "DONNEES_INVALIDES"


def test_l_arborescence_rend_zones_et_logements(
    client_authentifie: Client, arbre: dict[str, Any]
) -> None:
    corps = (
        client_authentifie()
        .get(f"/api/referentiels/chantiers/{arbre['chantier'].pk}/arborescence")
        .json()
    )
    assert corps["chantier"]["code"] == "CH-TEST"
    assert corps["zones"][0]["zone"]["code"] == "A"
    assert corps["zones"][0]["logements"][0]["numero"] == "A01"
    assert corps["zones"][0]["logements"][0]["statut"] == "A_VENIR"


def test_l_arborescence_d_un_chantier_inconnu_est_une_404(client_authentifie: Client) -> None:
    reponse = client_authentifie().get(
        "/api/referentiels/chantiers/00000000-0000-0000-0000-000000000000/arborescence"
    )
    assert reponse.status_code == 404
    assert reponse.json()["message"] == "Ce chantier est introuvable."


# --- Magasins : deux formes pour deux écrans (I-30) --------------------------------
def test_le_magasin_a_la_forme_referentiels_et_la_forme_stock(
    client_authentifie: Client, magasin: Any
) -> None:
    client = client_authentifie()
    referentiel = client.get("/api/referentiels/magasins").json()[0]
    stock = client.get("/api/magasins").json()[0]
    assert referentiel["nom"] == "Magasin de test"
    assert referentiel["chantier_id_chantier"] == str(magasin.chantier_id)
    assert stock == {
        "id_magasin": str(magasin.pk),
        "code": "MAG-TEST",
        "libelle": "Magasin de test",
        "id_chantier": str(magasin.chantier_id),
        "libelle_chantier": "Chantier de test",
    }


def test_un_code_de_magasin_deja_pris_est_une_erreur_de_saisie(
    client_authentifie: Client, magasin: Any
) -> None:
    reponse = client_authentifie().post(
        "/api/referentiels/magasins",
        {
            "code": "MAG-TEST",
            "nom": "Doublon",
            "actif": True,
            "chantier_id_chantier": str(magasin.chantier_id),
        },
        format="json",
    )
    assert reponse.status_code == 400
    assert "code" in reponse.json()["details"]


# --- Zones et logements -------------------------------------------------------------
def test_une_zone_puis_un_logement_se_creent(
    client_authentifie: Client, arbre: dict[str, Any]
) -> None:
    client = client_authentifie()
    zone = client.post(
        "/api/referentiels/zones",
        {
            "code": "B",
            "nom": "Îlot B",
            "type_zone": "TRANCHE",
            "chantier_id_chantier": str(arbre["chantier"].pk),
        },
        format="json",
    )
    assert zone.status_code == 201
    logement = client.post(
        "/api/referentiels/logements",
        {
            "numero": "B01",
            "statut": "EN_COURS",
            "zone_id_zone": zone.json()["id_zone"],
            "type_logement_code_type": "VILLA3",
        },
        format="json",
    )
    assert logement.status_code == 201
    assert logement.json()["statut"] == "EN_COURS"


def test_les_logements_du_chantier_servent_de_destinations(
    client_authentifie: Client, arbre: dict[str, Any]
) -> None:
    corps = client_authentifie().get(f"/api/chantiers/{arbre['chantier'].pk}/logements").json()
    assert corps == [
        {
            "id_logement": str(arbre["logement"].pk),
            "numero": "A01",
            "libelle_zone": "Îlot A",
            "libelle_type": "Villa 3 pièces",
        }
    ]


# --- Paramètres de chantier (EF-REF-07, I-35) -----------------------------------------
def _parametre(**champs: Any) -> dict[str, Any]:
    return {
        "cle": "delai_relance_validation_h",
        "valeur": "24",
        "type_valeur": "ENTIER",
        "libelle": "Délai de relance",
        **champs,
    }


def test_sans_chantier_precise_le_parametre_va_au_chantier_unique(
    client_authentifie: Client, chantier: Chantier
) -> None:
    reponse = client_authentifie().post("/api/parametrage/parametres", _parametre(), format="json")
    assert reponse.status_code == 201
    assert reponse.json()["chantier_id_chantier"] == str(chantier.pk)


def test_avec_deux_chantiers_il_faut_preciser_lequel(
    client_authentifie: Client, chantier: Chantier
) -> None:
    Chantier.objects.create(code="CH-2", nom="Second chantier")
    reponse = client_authentifie().post("/api/parametrage/parametres", _parametre(), format="json")
    assert reponse.status_code == 400
    assert "chantier_id_chantier" in reponse.json()["details"]


def test_une_cle_n_existe_qu_une_fois_par_chantier(
    client_authentifie: Client, chantier: Chantier
) -> None:
    client = client_authentifie()
    premier = client.post("/api/parametrage/parametres", _parametre(), format="json")
    assert premier.status_code == 201
    doublon = client.post("/api/parametrage/parametres", _parametre(), format="json")
    assert doublon.status_code == 400
    assert "cle" in doublon.json()["details"]


def test_une_valeur_illisible_dans_son_type_est_refusee(
    client_authentifie: Client, chantier: Chantier
) -> None:
    reponse = client_authentifie().post(
        "/api/parametrage/parametres", _parametre(valeur="vingt-quatre"), format="json"
    )
    assert reponse.status_code == 400
    assert "valeur" in reponse.json()["details"]


def test_un_parametre_se_modifie_sans_changer_de_chantier(
    client_authentifie: Client, chantier: Chantier
) -> None:
    parametre = ParametreChantier.objects.create(
        cle="devise", valeur="XOF", type_valeur="TEXTE", chantier=chantier
    )
    Chantier.objects.create(code="CH-2", nom="Second chantier")
    reponse = client_authentifie().put(
        f"/api/parametrage/parametres/{parametre.pk}",
        {"cle": "devise", "valeur": "EUR", "type_valeur": "TEXTE"},
        format="json",
    )
    assert reponse.status_code == 200
    parametre.refresh_from_db()
    assert (parametre.valeur, parametre.chantier_id) == ("EUR", chantier.pk)
