"""Jetons signés liés à l'appareil (arbitrage Q2, RG-D5, SQ-5 étapes 12 à 15)."""

from datetime import timedelta
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.identite.authentification import emettre_jeton
from domaines.identite.models import Appareil

pytestmark = pytest.mark.django_db

URL = "/api/auth/moi"


@pytest.fixture
def appareil(fabrique_utilisateur: Any) -> Appareil:
    utilisateur = fabrique_utilisateur(role="MAGASINIER")
    return Appareil.objects.create(
        utilisateur=utilisateur,
        empreinte_materiel="installation-0002",
        plateforme="android",
        version_application="1.0.0",
    )


def _client(jeton: str) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {jeton}")
    return client


def test_sans_jeton_401_non_authentifie() -> None:
    reponse = APIClient().get(URL)
    assert reponse.status_code == 401
    assert reponse.json()["motif"] == "NON_AUTHENTIFIE"


def test_jeton_falsifie_401_jeton_invalide(appareil: Appareil) -> None:
    jeton = emettre_jeton(appareil.utilisateur, appareil)
    reponse = _client(jeton[:-2] + "xx").get(URL)
    assert reponse.status_code == 401
    assert reponse.json()["motif"] == "JETON_INVALIDE"


def test_revocation_coupe_l_acces_a_la_requete_suivante(appareil: Appareil) -> None:
    client = _client(emettre_jeton(appareil.utilisateur, appareil))
    assert client.get(URL).status_code == 200
    Appareil.objects.filter(pk=appareil.pk).update(statut="REVOQUE")
    reponse = client.get(URL)
    assert reponse.status_code == 401
    assert reponse.json()["motif"] == "APPAREIL_REVOQUE"


def test_compte_desactive_coupe_l_acces(appareil: Appareil) -> None:
    client = _client(emettre_jeton(appareil.utilisateur, appareil))
    appareil.utilisateur.statut = "INACTIF"
    appareil.utilisateur.save()
    assert client.get(URL).json()["motif"] == "COMPTE_DESACTIVE"


def test_jeton_mobile_expire_apres_14_jours(appareil: Appareil, monkeypatch: Any) -> None:
    jeton = emettre_jeton(appareil.utilisateur, appareil)
    plus_tard = timezone.now() + timedelta(days=14, minutes=1)
    monkeypatch.setattr(timezone, "now", lambda: plus_tard)
    reponse = _client(jeton).get(URL)
    assert reponse.status_code == 401
    assert reponse.json()["motif"] == "JETON_EXPIRE"


def test_jeton_web_expire_apres_8_heures(fabrique_utilisateur: Any, monkeypatch: Any) -> None:
    jeton = emettre_jeton(fabrique_utilisateur())
    plus_tard = timezone.now() + timedelta(hours=8, minutes=1)
    monkeypatch.setattr(timezone, "now", lambda: plus_tard)
    assert _client(jeton).get(URL).json()["motif"] == "JETON_EXPIRE"


def test_requete_reussie_donne_l_heure_serveur(appareil: Appareil) -> None:
    """Arbitrage Q2 : toute requête authentifiée réussie du mobile rafraîchit
    derniere_connexion_en_ligne, à partir de l'heure du serveur."""
    reponse = _client(emettre_jeton(appareil.utilisateur, appareil)).get(URL)
    assert reponse.status_code == 200
    assert reponse["X-Horodatage-Serveur"]
    assert "X-Jeton-Renouvele" not in reponse


def test_jeton_mobile_ancien_est_renouvele(appareil: Appareil, monkeypatch: Any) -> None:
    jeton = emettre_jeton(appareil.utilisateur, appareil)
    plus_tard = timezone.now() + timedelta(days=2)
    monkeypatch.setattr(timezone, "now", lambda: plus_tard)
    reponse = _client(jeton).get(URL)
    assert reponse.status_code == 200
    nouveau = reponse["X-Jeton-Renouvele"]
    assert nouveau and nouveau != jeton
    assert _client(nouveau).get(URL).status_code == 200
