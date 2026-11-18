"""Matrice des droits servie en donnée (EF-AUT-02, EF-AUT-07, I-06)."""

from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.identite.models import DroitAccorde, JournalAudit
from domaines.identite.services.droits import RESOLVEURS_PORTEE, TOUT_LE_PROGRAMME, couverture

pytestmark = pytest.mark.django_db


def test_un_role_sans_le_droit_recoit_403(client_authentifie: Any) -> None:
    client = client_authentifie(role="MAGASINIER")
    reponse = client.get("/api/auth/comptes")
    assert reponse.status_code == 403
    assert reponse.json() == {
        "motif": "ACCES_REFUSE",
        "message": "Vous n'avez pas les droits nécessaires pour cette action.",
    }


def test_le_droit_vient_de_la_base_et_non_du_code(client_authentifie: Any) -> None:
    client = client_authentifie(role="MAGASINIER")
    DroitAccorde.objects.create(
        role_id="MAGASINIER", permission_id="api.comptes.lire", portee="GLOBALE"
    )
    assert client.get("/api/auth/comptes").status_code == 200


def test_moi_sert_les_onglets_mobiles_en_donnee(client_authentifie: Any) -> None:
    DroitAccorde.objects.create(
        role_id="MAGASINIER", permission_id="mobile.stock.lire", portee="PERIMETRE"
    )
    client = client_authentifie(role="MAGASINIER")
    corps = client.get("/api/auth/moi").json()
    onglets = {d["ressource"] for d in corps["droits"] if d["module"] == "mobile"}
    assert onglets == {"stock"}
    assert corps["affectations"][0]["role_code_role"] == "MAGASINIER"
    assert corps["horodatage_serveur"]


def test_affectation_close_ne_donne_plus_de_droit(fabrique_utilisateur: Any) -> None:
    from django.utils import timezone

    from domaines.identite.authentification import emettre_jeton
    from domaines.identite.models import AffectationRole

    utilisateur = fabrique_utilisateur(role="ADMINISTRATEUR")
    AffectationRole.objects.filter(utilisateur=utilisateur).update(date_fin=timezone.localdate())
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {emettre_jeton(utilisateur)}")
    assert client.get("/api/auth/comptes").status_code == 403


def test_lecture_de_la_matrice(client_authentifie: Any) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    roles = client.get("/api/droits/roles").json()
    permissions = client.get("/api/droits/permissions").json()
    accordes = client.get("/api/droits/accordes").json()
    assert {r["code_role"] for r in roles} >= {"ADMINISTRATEUR", "MAGASINIER"}
    assert any(p["code_permission"] == "ecran.administration.lire" for p in permissions)
    assert {"role_code_role", "permission_code_permission", "portee"} == set(accordes[0])


def test_le_web_ne_remplace_que_les_droits_d_ecran(client_authentifie: Any) -> None:
    """Le web n'envoie que des permissions d'écran : les droits « api » ne
    doivent pas disparaître (services/matrice.py)."""
    client = client_authentifie(role="ADMINISTRATEUR")
    avant_api = DroitAccorde.objects.filter(permission__module="api").count()
    reponse = client.put(
        "/api/droits/accordes",
        {
            "droits": [
                {
                    "role_code_role": "DIRECTION",
                    "permission_code_permission": "ecran.tableau-de-bord.lire",
                    "portee": "GLOBALE",
                }
            ]
        },
        format="json",
    )
    assert reponse.status_code == 200
    assert DroitAccorde.objects.filter(permission__module="ecran").count() == 1
    assert DroitAccorde.objects.filter(permission__module="api").count() == avant_api
    assert JournalAudit.objects.filter(action="MODIFICATION_DROITS").count() == 1


def test_l_administrateur_garde_le_droit_de_modifier_la_matrice(client_authentifie: Any) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    reponse = client.put(
        "/api/droits/accordes",
        {
            "droits": [
                {
                    "role_code_role": "ADMINISTRATEUR",
                    "permission_code_permission": "api.droits.lire",
                    "portee": "GLOBALE",
                }
            ]
        },
        format="json",
    )
    assert reponse.status_code == 409
    assert reponse.json()["motif"] == "VERROUILLAGE_ADMINISTRATION"


def test_une_portee_inconnue_est_refusee(client_authentifie: Any) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    reponse = client.put(
        "/api/droits/accordes",
        {
            "droits": [
                {
                    "role_code_role": "DIRECTION",
                    "permission_code_permission": "ecran.stock.lire",
                    "portee": "LOGEMENT",
                }
            ]
        },
        format="json",
    )
    assert reponse.status_code == 400


def test_couverture_par_resolveur_de_portee(
    fabrique_utilisateur: Any, perimetre_chantier: Any
) -> None:
    """Portée PERIMETRE : seul le périmètre de l'affectation ; GLOBALE : tout.
    Les deux passent par RESOLVEURS_PORTEE, extensible (arbitrage Q8)."""
    assert set(RESOLVEURS_PORTEE) == {"GLOBALE", "PERIMETRE"}
    utilisateur = fabrique_utilisateur(role="CHEF_CHANTIER", perimetre=perimetre_chantier)
    DroitAccorde.objects.create(
        role_id="CHEF_CHANTIER", permission_id="api.audit.lire", portee="PERIMETRE"
    )
    assert couverture(utilisateur, "api", "audit", "LIRE") == frozenset(
        {perimetre_chantier.id_perimetre}
    )
    DroitAccorde.objects.filter(role_id="CHEF_CHANTIER", permission_id="api.audit.lire").update(
        portee="GLOBALE"
    )
    assert couverture(utilisateur, "api", "audit", "LIRE") is TOUT_LE_PROGRAMME
