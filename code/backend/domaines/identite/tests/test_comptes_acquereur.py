"""Rattachement d'un compte à un acquéreur (écarts Q-AY, Q-AZ ; RG-D10 :
« un logement a au plus un acquéreur, l'acquéreur n'accède qu'à son
logement »)."""

from typing import Any

import pytest
from django.db import IntegrityError, transaction

from domaines.organisation.models import Acquereur, Logement, TypeLogement, Zone

pytestmark = pytest.mark.django_db

URL = "/api/auth/comptes"


@pytest.fixture
def acquereur(chantier: Any) -> Acquereur:
    zone = Zone.objects.create(code="A", nom="Îlot A", type_zone="TRANCHE", chantier=chantier)
    villa = TypeLogement.objects.create(code_type="VILLA3", libelle="Villa 3 pièces")
    logement = Logement.objects.create(numero="A01", zone=zone, type_logement=villa)
    return Acquereur.objects.create(nom="Diallo", prenom="Mariam", logement=logement)


def _compte(perimetre: Any, **champs: Any) -> dict[str, Any]:
    return {
        "identifiant": "m.diallo",
        "nom": "Diallo",
        "prenom": "Mariam",
        "statut": "ACTIF",
        "role_code_role": "ACQUEREUR",
        "perimetre_id_perimetre": str(perimetre.id_perimetre),
        "mot_de_passe": "Logement-A01-2026",
        **champs,
    }


def test_un_compte_acquereur_se_rattache_a_son_acquereur(
    client_authentifie: Any, perimetre_global: Any, acquereur: Acquereur
) -> None:
    corps = _compte(perimetre_global, acquereur_id_acquereur=str(acquereur.pk))
    reponse = client_authentifie().post(URL, corps, format="json")
    assert reponse.status_code == 201
    assert reponse.json()["acquereur_id_acquereur"] == str(acquereur.pk)


def test_seul_un_compte_acquereur_peut_etre_rattache(
    client_authentifie: Any, perimetre_global: Any, acquereur: Acquereur
) -> None:
    corps = _compte(
        perimetre_global, role_code_role="MAGASINIER", acquereur_id_acquereur=str(acquereur.pk)
    )
    reponse = client_authentifie().post(URL, corps, format="json")
    assert reponse.status_code == 400
    assert "acquereur_id_acquereur" in reponse.json()["details"]


def test_un_acquereur_n_a_qu_un_compte(
    client_authentifie: Any, perimetre_global: Any, acquereur: Acquereur
) -> None:
    client = client_authentifie()
    client.post(
        URL, _compte(perimetre_global, acquereur_id_acquereur=str(acquereur.pk)), format="json"
    )
    second = _compte(
        perimetre_global, identifiant="autre.compte", acquereur_id_acquereur=str(acquereur.pk)
    )
    assert client.post(URL, second, format="json").status_code == 400


def test_un_put_sans_le_champ_conserve_le_rattachement(
    client_authentifie: Any, perimetre_global: Any, acquereur: Acquereur
) -> None:
    client = client_authentifie()
    cree = client.post(
        URL, _compte(perimetre_global, acquereur_id_acquereur=str(acquereur.pk)), format="json"
    ).json()
    url = f"{URL}/{cree['id_utilisateur']}"
    sans_champ = _compte(perimetre_global, fonction="Acquéreuse", mot_de_passe=None)
    assert client.put(url, sans_champ, format="json").json()["acquereur_id_acquereur"] == str(
        acquereur.pk
    )
    detache = _compte(perimetre_global, mot_de_passe=None, acquereur_id_acquereur=None)
    assert client.put(url, detache, format="json").json()["acquereur_id_acquereur"] is None


def test_un_logement_n_a_qu_un_acquereur(acquereur: Acquereur) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Acquereur.objects.create(nom="Autre", prenom="Personne", logement=acquereur.logement)
