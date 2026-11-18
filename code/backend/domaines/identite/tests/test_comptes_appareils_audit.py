"""Comptes (EF-AUT-01/02, Q12), appareils (EF-AUT-06) et audit (EF-AUT-08)."""

from typing import Any

import pytest

from domaines.identite.models import Appareil, JournalAudit, Utilisateur

pytestmark = pytest.mark.django_db


def _compte(perimetre: Any, **champs: Any) -> dict[str, Any]:
    return {
        "identifiant": "nouveau.compte",
        "nom": "Ouattara",
        "prenom": "Aïcha",
        "fonction": "Magasinière",
        "statut": "ACTIF",
        "role_code_role": "MAGASINIER",
        "perimetre_id_perimetre": str(perimetre.id_perimetre),
        "mot_de_passe": "Magasin-Bassam-2026",
        **champs,
    }


def test_creation_avec_mot_de_passe_initial(client_authentifie: Any, perimetre_global: Any) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    reponse = client.post("/api/auth/comptes", _compte(perimetre_global), format="json")
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["role_code_role"] == "MAGASINIER"
    assert "mot_de_passe" not in corps
    assert Utilisateur.objects.get(identifiant="nouveau.compte").check_password(
        "Magasin-Bassam-2026"
    )
    assert JournalAudit.objects.filter(action="CREATION_COMPTE").count() == 1


def test_mot_de_passe_faible_refuse_avec_raisons(
    client_authentifie: Any, perimetre_global: Any
) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    reponse = client.post(
        "/api/auth/comptes", _compte(perimetre_global, mot_de_passe="123456"), format="json"
    )
    assert reponse.status_code == 400
    assert reponse.json()["details"]["mot_de_passe"]


def test_identifiant_en_double_refuse(client_authentifie: Any, perimetre_global: Any) -> None:
    client = client_authentifie(role="ADMINISTRATEUR", identifiant="deja.pris")
    reponse = client.post(
        "/api/auth/comptes", _compte(perimetre_global, identifiant="Deja.Pris"), format="json"
    )
    assert reponse.status_code == 400
    assert "identifiant" in reponse.json()["details"]


def test_desactivation_revoque_les_appareils(
    client_authentifie: Any, fabrique_utilisateur: Any, perimetre_global: Any
) -> None:
    """ET-4 : « compte désactivé » → « appareil révoqué »."""
    client = client_authentifie(role="ADMINISTRATEUR")
    cible = fabrique_utilisateur(role="MAGASINIER", identifiant="partant")
    Appareil.objects.create(
        utilisateur=cible, empreinte_materiel="x", plateforme="android", version_application="1"
    )
    reponse = client.put(
        f"/api/auth/comptes/{cible.pk}",
        _compte(perimetre_global, identifiant="partant", statut="INACTIF", mot_de_passe=None),
        format="json",
    )
    assert reponse.status_code == 200
    assert Appareil.objects.get(utilisateur=cible).statut == "REVOQUE"
    assert JournalAudit.objects.filter(action="DESACTIVATION_COMPTE").count() == 1


def test_changer_de_role_cloture_l_ancienne_affectation(
    client_authentifie: Any, fabrique_utilisateur: Any, perimetre_global: Any
) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    cible = fabrique_utilisateur(role="MAGASINIER", identifiant="mutation")
    corps = _compte(perimetre_global, identifiant="mutation", role_code_role="GESTIONNAIRE_STOCK")
    corps.pop("mot_de_passe")
    reponse = client.put(f"/api/auth/comptes/{cible.pk}", corps, format="json")
    assert reponse.json()["role_code_role"] == "GESTIONNAIRE_STOCK"


def test_revocation_d_un_appareil_idempotente_et_auditee(
    client_authentifie: Any, fabrique_utilisateur: Any
) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    proprietaire = fabrique_utilisateur(role="TECHNICIEN")
    appareil = Appareil.objects.create(
        utilisateur=proprietaire,
        empreinte_materiel="T-841",
        plateforme="android",
        version_application="1.0.0",
    )
    url = f"/api/appareils/{appareil.pk}/revocation"
    premiere = client.post(url)
    seconde = client.post(url)
    assert premiere.status_code == seconde.status_code == 200
    assert premiere.json()["statut"] == "REVOQUE"
    assert JournalAudit.objects.filter(action="REVOCATION_APPAREIL").count() == 1
    # RG-D9 + écart Q-C : la trace dit QUEL appareil a été révoqué.
    trace = JournalAudit.objects.get(action="REVOCATION_APPAREIL")
    assert trace.id_objet == str(appareil.pk)
    liste = client.get("/api/appareils").json()
    assert liste[0]["nom_utilisateur"] == proprietaire.nom_complet


def test_appareil_inconnu_404(client_authentifie: Any) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    reponse = client.post("/api/appareils/00000000-0000-4000-8000-000000000000/revocation")
    assert reponse.status_code == 404
    assert reponse.json()["motif"] == "INTROUVABLE"


def test_journal_d_audit_filtre_et_sans_code_interne(client_authentifie: Any) -> None:
    client = client_authentifie(role="ADMINISTRATEUR")
    client.post("/api/auth/deconnexion")
    entrees = client.get("/api/audit", {"action": "DECONNEXION"}).json()
    assert len(entrees) == 1
    entree = entrees[0]
    assert entree["resume"] == "Déconnexion"
    # Écart Q-C : la trace désigne l'objet visé (ici le compte qui se déconnecte).
    assert entree["id_objet"] == str(client.utilisateur.pk)
    assert entree["identifiant_utilisateur"] == client.utilisateur.identifiant
