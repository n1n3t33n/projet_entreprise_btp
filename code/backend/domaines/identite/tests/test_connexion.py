"""POST /api/auth/connexion (SQ-5 étapes 2 à 5, EF-AUT-03/04, ET-4)."""

from typing import Any

import pytest
from rest_framework.test import APIClient

from conftest import MOT_DE_PASSE_TEST
from domaines.identite.models import Appareil, JournalAudit

pytestmark = pytest.mark.django_db

URL = "/api/auth/connexion"
APPAREIL = {
    "empreinte_materiel": "installation-0001",
    "plateforme": "android",
    "version_application": "1.0.0",
}


def test_connexion_web_rend_jeton_utilisateur_et_droits(fabrique_utilisateur: Any) -> None:
    utilisateur = fabrique_utilisateur(role="ADMINISTRATEUR", identifiant="y.bamba")
    reponse = APIClient().post(
        URL, {"identifiant": "Y.Bamba", "mot_de_passe": MOT_DE_PASSE_TEST}, format="json"
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["jeton"]
    assert corps["id_appareil"] is None
    assert corps["utilisateur"]["id_utilisateur"] == str(utilisateur.pk)
    assert corps["utilisateur"]["role_code_role"] == "ADMINISTRATEUR"
    assert corps["connecte_le"]
    assert any(d["code_permission"] == "api.comptes.lire" for d in corps["droits"])
    # Le mot de passe et son empreinte ne sortent jamais.
    assert "mot_de_passe" not in str(corps)
    assert "password" not in str(corps)


def test_connexion_mobile_enrole_l_appareil_une_seule_fois(fabrique_utilisateur: Any) -> None:
    fabrique_utilisateur(role="MAGASINIER", identifiant="magasinier")
    corps = {"identifiant": "magasinier", "mot_de_passe": MOT_DE_PASSE_TEST, "appareil": APPAREIL}
    premiere = APIClient().post(URL, corps, format="json").json()
    seconde = APIClient().post(URL, corps, format="json").json()
    assert premiere["id_appareil"] == seconde["id_appareil"]
    assert Appareil.objects.count() == 1
    assert JournalAudit.objects.filter(action="ENROLEMENT_APPAREIL").count() == 1


def test_mauvais_mot_de_passe_401_sans_reveler_le_compte(fabrique_utilisateur: Any) -> None:
    fabrique_utilisateur(identifiant="y.bamba")
    mauvais = APIClient().post(
        URL, {"identifiant": "y.bamba", "mot_de_passe": "faux"}, format="json"
    )
    inconnu = APIClient().post(URL, {"identifiant": "personne", "mot_de_passe": "x"}, format="json")
    assert mauvais.status_code == inconnu.status_code == 401
    assert (
        mauvais.json()
        == inconnu.json()
        == {
            "motif": "IDENTIFIANTS",
            "message": "Identifiant ou mot de passe incorrect.",
        }
    )
    # L'échec sur un compte existant est tracé (RG-D9).
    assert JournalAudit.objects.filter(action="ECHEC_CONNEXION").count() == 1


def test_compte_inactif_403(fabrique_utilisateur: Any) -> None:
    fabrique_utilisateur(identifiant="parti", statut="INACTIF")
    reponse = APIClient().post(
        URL, {"identifiant": "parti", "mot_de_passe": MOT_DE_PASSE_TEST}, format="json"
    )
    assert reponse.status_code == 403
    assert reponse.json()["motif"] == "COMPTE_INACTIF"


def test_compte_sans_role_403(fabrique_utilisateur: Any) -> None:
    fabrique_utilisateur(role=None, identifiant="sans.role")
    reponse = APIClient().post(
        URL, {"identifiant": "sans.role", "mot_de_passe": MOT_DE_PASSE_TEST}, format="json"
    )
    assert reponse.status_code == 403
    assert reponse.json()["motif"] == "AUCUNE_AFFECTATION"


def test_appareil_revoque_refuse_a_la_connexion(fabrique_utilisateur: Any) -> None:
    utilisateur = fabrique_utilisateur(role="TECHNICIEN", identifiant="technicien")
    Appareil.objects.create(utilisateur=utilisateur, statut="REVOQUE", **APPAREIL)
    reponse = APIClient().post(
        URL,
        {"identifiant": "technicien", "mot_de_passe": MOT_DE_PASSE_TEST, "appareil": APPAREIL},
        format="json",
    )
    assert reponse.status_code == 403
    assert reponse.json()["motif"] == "APPAREIL_REVOQUE"


def test_trop_de_tentatives_429_verrouille(fabrique_utilisateur: Any) -> None:
    """EF-AUT-04 (arbitrage Q11) : 5 tentatives par minute et par identifiant
    en test ; la 6e reçoit 429 VERROUILLE avec le délai restant."""
    fabrique_utilisateur(identifiant="cible")
    client = APIClient()
    for _ in range(5):
        client.post(URL, {"identifiant": "cible", "mot_de_passe": "faux"}, format="json")
    reponse = client.post(URL, {"identifiant": "cible", "mot_de_passe": "faux"}, format="json")
    assert reponse.status_code == 429
    corps = reponse.json()
    assert corps["motif"] == "VERROUILLE"
    assert corps["secondes_restantes"] >= 1
    assert reponse["Retry-After"] == str(corps["secondes_restantes"])


def test_corps_invalide_400_avec_details() -> None:
    reponse = APIClient().post(URL, {"identifiant": ""}, format="json")
    assert reponse.status_code == 400
    corps = reponse.json()
    assert corps["motif"] == "DONNEES_INVALIDES"
    assert "mot_de_passe" in corps["details"]
