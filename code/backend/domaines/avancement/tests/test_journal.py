"""Journal d'exécution filtré et intervenants (EF-DSH-03, RG-A5), aux formes
de features/pilotage/api/dto.ts."""

from collections.abc import Callable
from datetime import timedelta
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.avancement.models import EtapeTravaux
from domaines.avancement.services import fiches
from domaines.identite.models import DroitAccorde
from domaines.organisation.models import Logement

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]
URL = "/api/pilotage/journal"


@pytest.fixture
def journal(
    client_authentifie: Client,
    chantier_avancement: dict[str, Any],
    logement: Logement,
    fabrique_utilisateur: Any,
) -> dict[str, Any]:
    """Un encadrant affecte les trois étapes (trois événements « en cours ») ;
    le technicien déclare les murs (validés implicitement) et bloque la
    peinture (trois événements de plus)."""
    DroitAccorde.objects.create(
        role_id="TECHNICIEN", permission_id="api.etapes.modifier", portee="GLOBALE"
    )
    etapes = list(EtapeTravaux.objects.filter(logement=logement).order_by("etape_modele__ordre"))
    technicien = chantier_avancement["technicien"]
    encadrant = fabrique_utilisateur()
    fiches.affecter(encadrant, [e.pk for e in etapes], technicien, None)
    client = client_authentifie(utilisateur=technicien)
    client.post(f"/api/etapes/{etapes[1].pk}/declaration", {}, format="json")
    client.post(f"/api/etapes/{etapes[2].pk}/blocage", {"code_motif": "INTEMPERIES"}, format="json")
    return {**chantier_avancement, "encadrant": encadrant, "lecteur": client_authentifie()}


def test_le_journal_rend_l_evenement_et_son_contexte(journal: dict[str, Any]) -> None:
    technicien = journal["technicien"]
    lignes = journal["lecteur"].get(URL, {"auteur": str(technicien.pk)}).json()
    assert [ligne["statut_apres"] for ligne in lignes] == [
        "BLOQUEE",
        "VALIDEE",
        "TERMINEE_DECLAREE",
    ]
    blocage = lignes[0]
    assert blocage["libelle_etape"] == "Peinture"
    assert blocage["numero_logement"] == "A01"
    assert blocage["libelle_zone"] == "Îlot A"
    assert blocage["code_corps_etat"] == "FIN"
    assert blocage["libelle_motif_blocage"] == "Intempéries"
    assert blocage["nom_auteur"] == technicien.nom_complet
    assert blocage["est_delegation"] is False


def test_le_journal_se_filtre(journal: dict[str, Any]) -> None:
    lecteur = journal["lecteur"]
    assert len(lecteur.get(URL).json()) == 6
    assert len(lecteur.get(URL, {"statut": "bloquee"}).json()) == 1  # casse indifférente
    assert len(lecteur.get(URL, {"statut": "EN_COURS"}).json()) == 3
    assert len(lecteur.get(URL, {"auteur": str(journal["encadrant"].pk)}).json()) == 3
    assert len(lecteur.get(URL, {"zone": str(journal["zone"].pk)}).json()) == 6
    demain = (timezone.localdate() + timedelta(days=1)).isoformat()
    assert lecteur.get(URL, {"depuis": demain}).json() == []
    assert len(lecteur.get(URL, {"jusqua": timezone.localdate().isoformat()}).json()) == 6
    assert lecteur.get(URL, {"statut": "INCONNU"}).status_code == 400


def test_les_intervenants_sont_les_auteurs(journal: dict[str, Any]) -> None:
    intervenants = journal["lecteur"].get("/api/pilotage/journal/intervenants").json()
    assert {i["id_utilisateur"] for i in intervenants} == {
        str(journal["technicien"].pk),
        str(journal["encadrant"].pk),
    }
    noms = [i["nom"] for i in intervenants]
    assert noms == sorted(noms, key=str.lower)
