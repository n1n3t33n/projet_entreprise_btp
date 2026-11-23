"""MPD-5, partie notifications : contraintes, écart Q-AN et catalogue
initial (migration notifications 0002)."""

from typing import Any

import pytest
from django.db import IntegrityError, transaction

from domaines.notifications.models import (
    AbonnementNotification,
    Notification,
    TypeNotification,
)

pytestmark = pytest.mark.django_db


def test_le_catalogue_initial_est_pose() -> None:
    assert TypeNotification.objects.filter(code_type="ETAPE_REJETEE").exists()
    personnes = AbonnementNotification.objects.filter(role__isnull=True)
    assert set(personnes.values_list("type_notification_id", flat=True)) == {
        "SORTIE_REFUSEE",
        "ETAPE_REJETEE",
    }


def test_un_canal_hors_liste_est_refuse(fabrique_utilisateur: Any) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Notification.objects.create(
            message="x",
            canal="SMS",
            type_notification_id="ETAPE_REJETEE",
            utilisateur=fabrique_utilisateur(),
        )


def test_une_notification_peut_ne_viser_aucune_alerte(fabrique_utilisateur: Any) -> None:
    """Écart Q-AN : une étape rejetée n'a pas d'alerte de stock."""
    notification = Notification.objects.create(
        message="Étape rejetée.",
        type_notification_id="ETAPE_REJETEE",
        utilisateur=fabrique_utilisateur(),
    )
    assert notification.alerte_id is None
    assert notification.canal == "APPLICATION"
