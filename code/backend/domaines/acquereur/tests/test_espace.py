"""Espace acquéreur (UC-5, EF-ACQ-01, EF-ACQ-02, RG-D10, Q-BA, Q-BB)."""

from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.avancement.models import EtapeTravaux
from domaines.avancement.services import declarations, fiches
from domaines.identite.models import DroitAccorde
from domaines.notifications.models import Notification
from domaines.organisation.models import Acquereur, Logement

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def acquereuse(logement: Logement, fabrique_utilisateur: Any) -> Any:
    compte = fabrique_utilisateur(role="ACQUEREUR")
    compte.acquereur = Acquereur.objects.create(nom="Diallo", prenom="Mariam", logement=logement)
    compte.save(update_fields=["acquereur"])
    return compte


@pytest.fixture
def etapes(
    chantier_avancement: dict[str, Any], logement: Logement, fabrique_utilisateur: Any
) -> list[EtapeTravaux]:
    DroitAccorde.objects.create(
        role_id="TECHNICIEN", permission_id="api.etapes.modifier", portee="GLOBALE"
    )
    liste = list(EtapeTravaux.objects.filter(logement=logement).order_by("etape_modele__ordre"))
    fiches.affecter(
        fabrique_utilisateur(), [e.pk for e in liste], chantier_avancement["technicien"], None
    )
    return liste


def test_l_acquereur_voit_son_logement_sans_details_internes(
    client_authentifie: Client,
    chantier_avancement: dict[str, Any],
    etapes: list[EtapeTravaux],
    acquereuse: Any,
) -> None:
    technicien = chantier_avancement["technicien"]
    declarations.declarer_terminee(technicien, etapes[1].pk, commentaire="Murs finis")
    declarations.bloquer(technicien, etapes[2].pk, "INTEMPERIES", commentaire="Pluie")
    reponse = client_authentifie(utilisateur=acquereuse).get("/api/acquereur/logement")
    assert reponse.status_code == 200
    donnees = reponse.json()
    assert donnees["numero_logement"] == "A01"
    assert donnees["libelle_type_logement"] == "Villa 3 pièces"
    statuts = {e["libelle_etape"]: e["statut"] for e in donnees["etapes"]}
    assert statuts == {"Fondations": "EN_COURS", "Murs": "VALIDEE", "Peinture": "EN_COURS"}
    murs = next(e for e in donnees["etapes"] if e["libelle_etape"] == "Murs")
    assert murs["date_franchissement"] is not None
    assert float(donnees["pourcentage_valide"]) == 30.0
    texte = reponse.content.decode()
    assert "Pluie" not in texte and "Murs finis" not in texte and technicien.nom not in texte


def test_une_etape_franchie_previent_l_acquereur_et_lui_seul(
    client_authentifie: Client,
    chantier_avancement: dict[str, Any],
    etapes: list[EtapeTravaux],
    acquereuse: Any,
    fabrique_utilisateur: Any,
) -> None:
    autre_acquereur = fabrique_utilisateur(role="ACQUEREUR")
    chef = fabrique_utilisateur(role="CHEF_CHANTIER")
    declarations.declarer_terminee(chantier_avancement["technicien"], etapes[1].pk)
    franchies = Notification.objects.filter(type_notification_id="ETAPE_FRANCHIE")
    assert list(franchies.values_list("utilisateur_id", flat=True)) == [acquereuse.pk]
    assert not franchies.filter(utilisateur__in=[autre_acquereur, chef]).exists()
    liste = client_authentifie(utilisateur=acquereuse).get("/api/acquereur/notifications").json()
    assert [(n["libelle_etape"], n["lue"]) for n in liste] == [("Murs", False)]


def test_un_compte_acquereur_non_rattache_n_a_pas_de_logement(
    client_authentifie: Client,
) -> None:
    reponse = client_authentifie(role="ACQUEREUR").get("/api/acquereur/logement")
    assert reponse.status_code == 404
    assert reponse.json()["message"] == "Aucun logement n'est rattaché à ce compte."


def test_l_espace_exige_le_droit_acquereur(client_authentifie: Client) -> None:
    assert client_authentifie(role="TECHNICIEN").get("/api/acquereur/logement").status_code == 403
