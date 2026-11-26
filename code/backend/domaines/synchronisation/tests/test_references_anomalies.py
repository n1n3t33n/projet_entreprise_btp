"""Téléchargement incrémental des références (EF-SYN-04, Q-AI) et
supervision des anomalies (EF-SYN-05, Q-AJ)."""

import uuid
from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.identite.models import DroitAccorde
from domaines.referentiels.models import Article, UniteMesure
from domaines.synchronisation.models import AnomalieSynchronisation, CurseurReference
from domaines.synchronisation.services import anomalies, references

pytestmark = pytest.mark.django_db

URL_REFERENCES = "/api/synchronisation/references"
URL_ANOMALIES = "/api/synchronisation/anomalies"
Client = Callable[..., APIClient]


@pytest.fixture
def unite(db: Any) -> UniteMesure:
    return UniteMesure.objects.create(code_unite="SAC", libelle="sac", type_unite="MASSE")


def _versions(reponse: Any) -> dict[str, int]:
    return {jeu["type_donnee"]: jeu["version"] for jeu in reponse.data["jeux"]}


# --- Références (EF-SYN-04) ---------------------------------------------------------------
def test_le_premier_telechargement_rend_tous_les_jeux(client_mobile: Client, unite: Any) -> None:
    client = client_mobile()
    reponse = client.get(URL_REFERENCES)
    assert reponse.status_code == 200
    assert {"articles", "unites", "stock", "fiches_route"} <= set(_versions(reponse))
    assert reponse.data["inchanges"] == []
    assert CurseurReference.objects.filter(appareil=client.appareil).count() == len(  # type: ignore[attr-defined]
        reponse.data["jeux"]
    )


def test_seuls_les_jeux_changes_sont_renvoyes(client_mobile: Client, unite: Any) -> None:
    client = client_mobile()
    versions = _versions(client.get(URL_REFERENCES))
    deuxieme = client.get(URL_REFERENCES, versions)
    assert deuxieme.data["jeux"] == []
    assert set(deuxieme.data["inchanges"]) == set(versions)

    Article.objects.create(code="A9", designation="Sable", origine="ACHAT", unite_mesure=unite)
    troisieme = client.get(URL_REFERENCES, versions)
    assert list(_versions(troisieme)) == ["articles"]
    assert _versions(troisieme)["articles"] != versions["articles"]
    curseur = CurseurReference.objects.get(
        appareil=client.appareil, type_donnee="articles"  # type: ignore[attr-defined]
    )
    assert curseur.version_connue == versions["articles"]


def test_seuls_les_jeux_autorises_sont_proposes(client_mobile: Client) -> None:
    for permission in ("api.synchronisation.creer", "api.articles.lire"):
        DroitAccorde.objects.create(
            role_id="TECHNICIEN", permission_id=permission, portee="GLOBALE"
        )
    reponse = client_mobile(role="TECHNICIEN").get(URL_REFERENCES)
    # « notifications » : droit accordé à tous les rôles (notifications 0004).
    assert list(_versions(reponse)) == ["articles", "notifications"]


def test_une_version_illisible_vaut_jamais_recu(client_mobile: Client) -> None:
    reponse = client_mobile().get(URL_REFERENCES, {"articles": "abc"})
    assert "articles" in _versions(reponse)


def test_une_version_de_dix_neuf_chiffres_est_reconnue(
    client_mobile: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    # La plus grande empreinte possible (16^15 - 1) s'écrit en 19 chiffres :
    # le téléphone qui la renvoie ne doit pas recevoir le jeu une seconde fois.
    monkeypatch.setattr(references, "empreinte", lambda _donnees: references.VERSION_MAX)
    client = client_mobile()
    versions = _versions(client.get(URL_REFERENCES))
    assert len(str(versions["articles"])) == 19
    deuxieme = client.get(URL_REFERENCES, versions)
    assert _versions(deuxieme) == {}
    assert set(deuxieme.data["inchanges"]) == set(versions)


# --- Anomalies (EF-SYN-05) ----------------------------------------------------------------
@pytest.fixture
def anomalie(fabrique_appareil: Any) -> AnomalieSynchronisation:
    return anomalies.signaler(fabrique_appareil(), "REJET_REGLE", "Motif obligatoire.")


def test_les_anomalies_se_filtrent_par_statut(
    client_authentifie: Client, anomalie: AnomalieSynchronisation
) -> None:
    client = client_authentifie()
    ouvertes = client.get(URL_ANOMALIES, {"statut": "OUVERTE"})
    assert [a["id_anomalie"] for a in ouvertes.data] == [str(anomalie.pk)]
    assert ouvertes.data[0]["uuid_evenement"] is None
    assert client.get(URL_ANOMALIES, {"statut": "TRAITEE"}).data == []
    assert client.get(URL_ANOMALIES, {"statut": "INCONNU"}).status_code == 400


def test_traiter_une_anomalie_deux_fois_ne_change_rien(
    client_authentifie: Client, anomalie: AnomalieSynchronisation
) -> None:
    client = client_authentifie()
    url = f"{URL_ANOMALIES}/{anomalie.pk}/traitement"
    assert client.post(url).data["statut"] == "TRAITEE"
    assert client.post(url).status_code == 200
    assert client.post(f"{URL_ANOMALIES}/{uuid.uuid4()}/traitement").status_code == 404


def test_la_supervision_exige_le_droit(
    client_authentifie: Client, anomalie: AnomalieSynchronisation
) -> None:
    client = client_authentifie(role="TECHNICIEN")
    assert client.get(URL_ANOMALIES).status_code == 403
    assert client.post(f"{URL_ANOMALIES}/{anomalie.pk}/traitement").status_code == 403


def test_une_anomalie_se_resout_depuis_le_mobile(
    client_mobile: Client, anomalie: AnomalieSynchronisation
) -> None:
    client = client_mobile()

    def resoudre() -> str:
        corps = {
            "id_lot": str(uuid.uuid4()),
            "evenements": [
                {
                    "uuid": str(uuid.uuid4()),
                    "type": "RESOLUTION_ANOMALIE",
                    "charge_utile": {"id_anomalie": str(anomalie.pk)},
                }
            ],
        }
        return str(
            client.post("/api/synchronisation/lots", corps, format="json").data["resultats"][0][
                "statut"
            ]
        )

    assert resoudre() == "ACCEPTE"
    assert resoudre() == "DEJA_RECU"
    anomalie.refresh_from_db()
    assert anomalie.statut == "TRAITEE"
