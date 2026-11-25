"""Conservation des données de synchronisation (Q-BF) : anomalies traitées
et lots anciens purgés ; un lot cité par une anomalie conservée est gardé."""

import uuid
from datetime import timedelta
from typing import Any

import pytest
from django.test import override_settings
from django.utils import timezone

from domaines.synchronisation.models import (
    AnomalieSynchronisation,
    LotSynchronisation,
    ResultatEvenement,
)
from domaines.synchronisation.services import conservation

pytestmark = pytest.mark.django_db


def _lot(appareil: Any, age_jours: int) -> ResultatEvenement:
    lot = LotSynchronisation.objects.create(
        appareil=appareil, date_reception=timezone.now() - timedelta(days=age_jours)
    )
    return ResultatEvenement.objects.create(
        lot_synchronisation=lot, uuid_evenement=uuid.uuid4(), statut="REJETE"
    )


def _anomalie(appareil: Any, statut: str, age_jours: int, resultat: Any = None) -> Any:
    return AnomalieSynchronisation.objects.create(
        appareil=appareil,
        type_anomalie="REJET_REGLE",
        description="x",
        statut=statut,
        date_detection=timezone.now() - timedelta(days=age_jours),
        resultat_evenement=resultat,
    )


def test_la_purge_respecte_les_durees_et_les_anomalies_conservees(fabrique_appareil: Any) -> None:
    appareil = fabrique_appareil()
    ancien = _lot(appareil, 120)
    recent = _lot(appareil, 10)
    cite = _lot(appareil, 120)
    _anomalie(appareil, "OUVERTE", 120, cite)
    vieille_traitee = _anomalie(appareil, "TRAITEE", 200, _lot(appareil, 200))
    recente_traitee = _anomalie(appareil, "TRAITEE", 30)

    bilan = conservation.purger()

    assert bilan == "1 anomalie(s) traitée(s), 2 lot(s) et 2 résultat(s) purgés."
    restants = set(LotSynchronisation.objects.values_list("pk", flat=True))
    assert recent.lot_synchronisation_id in restants
    assert cite.lot_synchronisation_id in restants
    assert ancien.lot_synchronisation_id not in restants
    assert not AnomalieSynchronisation.objects.filter(pk=vieille_traitee.pk).exists()
    assert AnomalieSynchronisation.objects.filter(pk=recente_traitee.pk).exists()


@override_settings(CONSERVATION_LOTS_JOURS=5)
def test_la_duree_est_reglable(fabrique_appareil: Any) -> None:
    _lot(fabrique_appareil(), 10)
    conservation.purger()
    assert LotSynchronisation.objects.count() == 0
