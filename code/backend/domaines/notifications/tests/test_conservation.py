"""Conservation des notifications (Q-BF) : lues après 90 jours, non lues
après 365 jours."""

from datetime import timedelta
from typing import Any

import pytest
from django.utils import timezone

from domaines.notifications.models import Notification
from domaines.notifications.services import conservation

pytestmark = pytest.mark.django_db


def _notification(utilisateur: Any, cree_il_y_a: int, lue_il_y_a: int | None) -> Notification:
    maintenant = timezone.now()
    return Notification.objects.create(
        message=f"{cree_il_y_a}/{lue_il_y_a}",
        type_notification_id="ETAPE_REJETEE",
        utilisateur=utilisateur,
        date_creation=maintenant - timedelta(days=cree_il_y_a),
        date_lecture=maintenant - timedelta(days=lue_il_y_a) if lue_il_y_a is not None else None,
    )


def test_la_purge_suit_la_lecture_et_l_age(fabrique_utilisateur: Any) -> None:
    moi = fabrique_utilisateur()
    _notification(moi, 200, 100)  # lue il y a plus de 90 jours : purgée
    _notification(moi, 200, 30)  # lue récemment : gardée
    _notification(moi, 400, None)  # non lue depuis plus d'un an : purgée
    _notification(moi, 200, None)  # non lue, moins d'un an : gardée
    assert conservation.purger() == "2 notification(s) purgée(s)."
    assert set(Notification.objects.values_list("message", flat=True)) == {"200/30", "200/None"}
