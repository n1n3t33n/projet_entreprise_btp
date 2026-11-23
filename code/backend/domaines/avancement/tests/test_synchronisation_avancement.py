"""Opérations d'avancement rejouées par lot (SQ-2, Q-AE, Q-AG) : blocage,
levée et déclaration d'une même étape, dans l'ordre d'envoi ; une
déclaration devenue impossible sur le serveur est un conflit (EF-SYN-05)."""

import uuid
from collections.abc import Callable
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.avancement.models import EtapeTravaux, EvenementExecution
from domaines.avancement.services import fiches
from domaines.identite.models import DroitAccorde
from domaines.organisation.models import Logement
from domaines.synchronisation.models import AnomalieSynchronisation

pytestmark = pytest.mark.django_db

URL = "/api/synchronisation/lots"


def _evenement(type_evenement: str, etape: EtapeTravaux, **corps: Any) -> dict[str, Any]:
    return {
        "uuid": str(uuid.uuid4()),
        "type": type_evenement,
        "horodatage_appareil": timezone.now().isoformat(),
        "charge_utile": {"id_etape": str(etape.pk), **corps},
    }


def _lot(*evenements: dict[str, Any]) -> dict[str, Any]:
    return {"id_lot": str(uuid.uuid4()), "evenements": list(evenements)}


@pytest.fixture
def technicien_mobile(
    chantier_avancement: dict[str, Any],
    logement: Logement,
    fabrique_utilisateur: Any,
    client_mobile: Callable[..., APIClient],
) -> tuple[APIClient, list[EtapeTravaux]]:
    """Les étapes du logement affectées au technicien, qui peut déclarer et
    synchroniser."""
    for permission in ("api.etapes.modifier", "api.synchronisation.creer"):
        DroitAccorde.objects.create(
            role_id="TECHNICIEN", permission_id=permission, portee="GLOBALE"
        )
    etapes = list(EtapeTravaux.objects.filter(logement=logement).order_by("etape_modele__ordre"))
    technicien = chantier_avancement["technicien"]
    fiches.affecter(fabrique_utilisateur(), [e.pk for e in etapes], technicien, None)
    return client_mobile(utilisateur=technicien), etapes


def test_blocage_levee_et_declaration_dans_le_meme_lot(
    technicien_mobile: tuple[APIClient, list[EtapeTravaux]],
) -> None:
    client, etapes = technicien_mobile
    murs = etapes[1]
    evenements = [
        _evenement("BLOCAGE_ETAPE", murs, code_motif="INTEMPERIES"),
        _evenement("LEVEE_BLOCAGE", murs),
        _evenement("DECLARATION_ETAPE", murs),
    ]
    reponse = client.post(URL, _lot(*evenements), format="json")
    assert reponse.status_code == 201
    assert {r["statut"] for r in reponse.data["resultats"]} == {"ACCEPTE"}
    murs.refresh_from_db()
    assert murs.statut == "VALIDEE"  # sans contrôle : validée implicitement (Q-X)
    uuids = {uuid.UUID(e["uuid"]) for e in evenements}
    assert set(
        EvenementExecution.objects.filter(uuid__in=uuids).values_list("uuid", flat=True)
    ) == (uuids)


def test_une_declaration_sur_une_etape_terminee_est_un_conflit(
    technicien_mobile: tuple[APIClient, list[EtapeTravaux]],
) -> None:
    client, etapes = technicien_mobile
    murs = etapes[1]
    client.post(URL, _lot(_evenement("DECLARATION_ETAPE", murs)), format="json")
    reponse = client.post(URL, _lot(_evenement("DECLARATION_ETAPE", murs)), format="json")
    resultat = reponse.data["resultats"][0]
    assert resultat["statut"] == "REJETE"
    assert resultat["code_rejet"] == "TRANSITION_IMPOSSIBLE"
    assert AnomalieSynchronisation.objects.get().type_anomalie == "CONFLIT_VERSION"
