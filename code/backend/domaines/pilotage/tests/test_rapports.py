"""Rapport hebdomadaire et indicateurs d'usage (EF-DSH-06, EF-DSH-07, Q-AT) :
rubriques des domaines, CSV, semaine, droits, annonce unique."""

from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.identite.models import DroitAccorde
from domaines.notifications.models import Notification
from domaines.pilotage.services import rapports

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]
URL = "/api/pilotage/rapport-hebdomadaire"


def test_le_rapport_assemble_les_rubriques_dans_l_ordre(client_authentifie: Client) -> None:
    reponse = client_authentifie().get(URL, {"semaine": "2026-W47"})
    assert reponse.status_code == 200
    donnees = reponse.json()
    assert (donnees["semaine"], donnees["du"], donnees["au"]) == (
        "2026-W47",
        "2026-11-16",
        "2026-11-22",
    )
    rubriques = list(dict.fromkeys(ligne["rubrique"] for ligne in donnees["lignes"]))
    assert rubriques == ["Avancement", "Stock", "Synchronisation"]


def test_le_rapport_se_telecharge_en_csv(client_authentifie: Client) -> None:
    reponse = client_authentifie().get(URL, {"semaine": "2026-W47", "export": "csv"})
    assert reponse["Content-Type"].startswith("text/csv")
    assert 'filename="rapport-2026-W47.csv"' in reponse["Content-Disposition"]
    texte = reponse.content.decode("utf-8")
    assert texte.startswith("﻿Rubrique;Indicateur;Valeur\r\n")
    assert "Stock;Sorties de la période;0" in texte


def test_une_semaine_mal_formee_est_refusee(client_authentifie: Client) -> None:
    client = client_authentifie()
    assert client.get(URL, {"semaine": "47"}).status_code == 400
    assert client.get(URL, {"semaine": "2026-W60"}).status_code == 400


def test_sans_semaine_c_est_la_derniere_complete() -> None:
    code, debut, fin = rapports.semaine(None)
    assert debut.weekday() == 0 and (fin - debut).days == 6
    assert code.startswith(str(debut.isocalendar()[0]))


def test_le_rapport_et_l_usage_exigent_leur_droit(client_authentifie: Client) -> None:
    technicien = client_authentifie(role="TECHNICIEN")
    assert technicien.get(URL).status_code == 403
    assert technicien.get("/api/pilotage/usage").status_code == 403
    DroitAccorde.objects.create(
        role_id="DIRECTION", permission_id="api.rapport-hebdomadaire.lire", portee="GLOBALE"
    )
    assert client_authentifie(role="DIRECTION").get(URL).status_code == 200


def test_l_usage_couvre_les_derniers_jours(client_authentifie: Client) -> None:
    client = client_authentifie()
    usage = client.get("/api/pilotage/usage", {"jours": 30}).json()
    indicateurs = {ligne["indicateur"] for ligne in usage["lignes"]}
    assert {"Mouvements saisis", "Taux d'acceptation (%)", "Appareils actifs"} <= indicateurs
    assert client.get("/api/pilotage/usage", {"jours": 365}).status_code == 400


def test_le_rapport_n_est_annonce_qu_une_fois(fabrique_utilisateur: Any) -> None:
    direction = fabrique_utilisateur(role="DIRECTION")
    rapports.annoncer()
    rapports.annoncer()
    notification = Notification.objects.get(utilisateur=direction)
    assert notification.type_notification_id == "RAPPORT_HEBDOMADAIRE"
    assert "est disponible" in notification.message
