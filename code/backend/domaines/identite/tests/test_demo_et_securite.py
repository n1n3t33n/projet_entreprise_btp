"""Démonstration rejouable, journaux sans secret (6.1), documentation et
administration protégées par la matrice (6.9, 6.10)."""

import logging
from typing import Any

import pytest
from django.core.management import call_command
from django.test import Client
from rest_framework.test import APIClient

from conftest import MOT_DE_PASSE_TEST
from domaines.identite.models import AffectationRole, Equipe, Utilisateur

pytestmark = pytest.mark.django_db


def test_la_demo_est_rejouable_sans_doublon(monkeypatch: Any) -> None:
    monkeypatch.setenv("DEMO_MOT_DE_PASSE", "Demo-Grand-Bassam-2026")
    call_command("charger_demo")
    call_command("charger_demo")
    assert Utilisateur.objects.count() == 14
    assert Equipe.objects.count() == 2
    assert AffectationRole.objects.count() == 10
    assert Utilisateur.objects.get(identifiant="magasinier").check_password(
        "Demo-Grand-Bassam-2026"
    )
    # Les membres d'équipe sans accès n'ont pas de mot de passe utilisable.
    assert not Utilisateur.objects.get(identifiant="a.kone").has_usable_password()


def test_la_demo_exige_son_mot_de_passe(monkeypatch: Any) -> None:
    from django.core.management.base import CommandError

    monkeypatch.delenv("DEMO_MOT_DE_PASSE", raising=False)
    with pytest.raises(CommandError):
        call_command("charger_demo")


def test_aucun_secret_dans_les_journaux(
    fabrique_utilisateur: Any, caplog: pytest.LogCaptureFixture, monkeypatch: Any
) -> None:
    """Exigence 6.1 : ni mot de passe ni jeton dans aucune sortie, même
    quand une erreur serveur survient pendant la requête."""
    from socle.journalisation.formateur import FormateurJson
    from socle.journalisation.masquage import FiltreMasquage

    fabrique_utilisateur(identifiant="secret.test")
    caplog.set_level(logging.INFO)
    client = APIClient()
    jeton = client.post(
        "/api/auth/connexion",
        {"identifiant": "secret.test", "mot_de_passe": MOT_DE_PASSE_TEST},
        format="json",
    ).json()["jeton"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {jeton}")

    def panne(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError(f"panne simulée avec Bearer {jeton} et mot_de_passe={MOT_DE_PASSE_TEST}")

    monkeypatch.setattr("domaines.identite.api.vues.droits_effectifs", panne)
    assert client.get("/api/auth/moi").status_code == 500

    formateur, filtre = FormateurJson(), FiltreMasquage()
    sorties = []
    for enregistrement in caplog.records:
        filtre.filter(enregistrement)
        sorties.append(formateur.format(enregistrement))
    tout = "\n".join(sorties)
    assert "requête traitée" in tout
    assert MOT_DE_PASSE_TEST not in tout
    assert jeton not in tout


def test_erreur_500_au_format_unique_avec_numero_de_suivi(
    client_authentifie: Any, monkeypatch: Any
) -> None:
    def panne(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("panne interne")

    monkeypatch.setattr("domaines.identite.api.vues.droits_effectifs", panne)
    reponse = client_authentifie(role="ADMINISTRATEUR").get("/api/auth/moi")
    assert reponse.status_code == 500
    corps = reponse.json()
    assert corps["motif"] == "ERREUR_INTERNE"
    assert corps["id_correlation"] == reponse["X-Request-ID"]
    assert "panne interne" not in str(corps)


def test_route_inconnue_404_json() -> None:
    reponse = Client().get("/api/nexiste-pas")
    assert reponse.status_code == 404
    assert reponse.json()["motif"] == "INTROUVABLE"


def test_documentation_refusee_sans_le_droit(client_authentifie: Any) -> None:
    assert APIClient().get("/api/schema/").status_code == 401
    assert client_authentifie(role="MAGASINIER").get("/api/schema/").status_code == 403


def test_documentation_ouverte_avec_le_droit(client_authentifie: Any) -> None:
    reponse = client_authentifie(role="ADMINISTRATEUR").get("/api/docs/redoc/")
    assert reponse.status_code == 200


def test_admin_reserve_au_droit_technique(fabrique_utilisateur: Any) -> None:
    administrateur = fabrique_utilisateur(role="ADMINISTRATEUR", identifiant="admin.tech")
    magasinier = fabrique_utilisateur(role="MAGASINIER", identifiant="mag.tech")
    client = Client()
    client.force_login(magasinier)
    assert client.get("/admin/").status_code == 302  # renvoyé vers la connexion
    client.force_login(administrateur)
    assert client.get("/admin/").status_code == 200
    assert client.get("/admin/identite/utilisateur/").status_code == 200
    # Lecture seule : aucun ajout de compte par l'admin.
    assert client.get("/admin/identite/utilisateur/add/").status_code == 403
