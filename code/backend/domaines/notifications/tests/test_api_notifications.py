"""API des notifications (EF-NOT-01, Q-AS, Q-AW) : liste, compteur, lecture,
lecture groupée, cloisonnement par utilisateur, jeu de référence mobile."""

import uuid
from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.notifications.models import Notification

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


def _notifier(utilisateur: Any, message: str = "Étape rejetée.") -> Notification:
    return Notification.objects.create(
        message=message, type_notification_id="ETAPE_REJETEE", utilisateur=utilisateur
    )


def test_chacun_ne_voit_que_ses_notifications(
    client_authentifie: Client, fabrique_utilisateur: Any
) -> None:
    client = client_authentifie(role="TECHNICIEN")  # droit accordé à tous les rôles
    moi = client.utilisateur  # type: ignore[attr-defined]
    _notifier(moi, "La mienne.")
    _notifier(fabrique_utilisateur(), "Celle d'un autre.")
    reponse = client.get("/api/notifications")
    assert reponse.status_code == 200
    assert [n["message"] for n in reponse.json()] == ["La mienne."]
    assert reponse.json()[0]["libelle_type"] == "Étape rejetée"
    assert reponse.json()[0]["est_lue"] is False


def test_compteur_lecture_et_lecture_groupee(client_authentifie: Client) -> None:
    client = client_authentifie(role="TECHNICIEN")
    moi = client.utilisateur  # type: ignore[attr-defined]
    premiere, _seconde, _troisieme = (_notifier(moi) for _ in range(3))
    assert client.get("/api/notifications/compteur").json() == {"non_lues": 3}
    lue = client.post(f"/api/notifications/{premiere.pk}/lecture").json()
    assert lue["est_lue"] is True
    assert client.post(f"/api/notifications/{premiere.pk}/lecture").status_code == 200
    assert len(client.get("/api/notifications", {"non_lues": "true"}).json()) == 2
    assert client.post("/api/notifications/lecture").json() == {"nombre": 2}
    assert client.get("/api/notifications/compteur").json() == {"non_lues": 0}


def test_on_ne_marque_pas_la_notification_d_un_autre(
    client_authentifie: Client, fabrique_utilisateur: Any
) -> None:
    autre = _notifier(fabrique_utilisateur())
    client = client_authentifie(role="TECHNICIEN")
    assert client.post(f"/api/notifications/{autre.pk}/lecture").status_code == 404
    assert client.post(f"/api/notifications/{uuid.uuid4()}/lecture").status_code == 404
    autre.refresh_from_db()
    assert autre.date_lecture is None


def test_la_limite_est_bornee(client_authentifie: Client) -> None:
    assert client_authentifie().get("/api/notifications", {"limite": 1000}).status_code == 400


def test_le_mobile_recoit_ses_notifications_non_lues(client_mobile: Client) -> None:
    client = client_mobile()
    _notifier(client.appareil.utilisateur, "À lire hors ligne.")  # type: ignore[attr-defined]
    reponse = client.get("/api/synchronisation/references")
    jeux = {jeu["type_donnee"]: jeu["donnees"] for jeu in reponse.json()["jeux"]}
    assert [n["message"] for n in jeux["notifications"]] == ["À lire hors ligne."]
