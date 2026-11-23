"""MPD-6 côté serveur : contraintes des lots, résultats, curseurs, anomalies."""

from typing import Any

import pytest
from django.db import IntegrityError, transaction

from domaines.synchronisation.models import (
    AnomalieSynchronisation,
    CurseurReference,
    LotSynchronisation,
    ResultatEvenement,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def lot(fabrique_appareil: Any) -> LotSynchronisation:
    return LotSynchronisation.objects.create(appareil=fabrique_appareil())


def test_un_statut_de_resultat_hors_liste_est_refuse(lot: LotSynchronisation) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        ResultatEvenement.objects.create(
            uuid_evenement="00000000-0000-0000-0000-000000000001",
            statut="EN_ATTENTE",
            lot_synchronisation=lot,
        )


def test_un_type_d_anomalie_hors_liste_est_refuse(lot: LotSynchronisation) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        AnomalieSynchronisation.objects.create(
            type_anomalie="INCONNUE", description="x", appareil=lot.appareil
        )


def test_un_curseur_par_appareil_et_par_type(lot: LotSynchronisation) -> None:
    CurseurReference.objects.create(appareil=lot.appareil, type_donnee="articles")
    with pytest.raises(IntegrityError), transaction.atomic():
        CurseurReference.objects.create(appareil=lot.appareil, type_donnee="articles")
