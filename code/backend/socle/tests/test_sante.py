"""Exigence 6.2 : vivacité et aptitude, sans authentification ni fuite."""

import uuid

import pytest
from django.test import Client

from socle import sante


def test_vivacite_repond_sans_authentification() -> None:
    reponse = Client().get("/api/sante/vivacite")
    assert reponse.status_code == 200
    assert reponse.json() == {"statut": "OK"}


@pytest.mark.django_db
def test_aptitude_verifie_base_et_migrations() -> None:
    reponse = Client().get("/api/sante/aptitude")
    assert reponse.status_code == 200
    assert reponse.json() == {
        "statut": "OK",
        "verifications": {"base_de_donnees": "OK", "migrations": "OK"},
    }


@pytest.mark.django_db
def test_aptitude_signale_une_base_injoignable_sans_detail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sante, "verifier_base", lambda: sante.KO)
    reponse = Client().get("/api/sante/aptitude")
    assert reponse.status_code == 503
    corps = reponse.json()
    assert corps["statut"] == "INDISPONIBLE"
    # Rien sur l'infrastructure : uniquement des états.
    assert set(corps) == {"statut", "verifications"}


def test_la_reponse_porte_l_identifiant_de_correlation() -> None:
    identifiant = str(uuid.uuid4())
    reponse = Client().get("/api/sante/vivacite", HTTP_X_REQUEST_ID=identifiant)
    assert reponse["X-Request-ID"] == identifiant


def test_un_identifiant_de_correlation_invalide_est_remplace() -> None:
    reponse = Client().get("/api/sante/vivacite", HTTP_X_REQUEST_ID="<script>")
    assert reponse["X-Request-ID"] != "<script>"
    uuid.UUID(reponse["X-Request-ID"])


def test_seul_get_est_accepte() -> None:
    assert Client().post("/api/sante/vivacite").status_code == 405
