"""Conservation des notifications (Q-BF, B7).

Traitement planifié ``purger_notifications`` (chaque nuit) : notifications
LUES depuis plus de ``CONSERVATION_NOTIFICATIONS_LUES_JOURS`` jours, et
notifications NON LUES créées depuis plus de
``CONSERVATION_NOTIFICATIONS_NON_LUES_JOURS`` jours. Une notification n'est
qu'un avis : l'objet qu'elle cite (mouvement, étape…) reste dans son journal.
"""

from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from domaines.notifications.models import Notification


def purger() -> str:
    maintenant = timezone.now()
    lues = Q(
        date_lecture__lt=maintenant - timedelta(days=settings.CONSERVATION_NOTIFICATIONS_LUES_JOURS)
    )
    non_lues = Q(date_lecture__isnull=True) & Q(
        date_creation__lt=maintenant
        - timedelta(days=settings.CONSERVATION_NOTIFICATIONS_NON_LUES_JOURS)
    )
    nombre, _detail = Notification.objects.filter(lues | non_lues).delete()
    return f"{nombre} notification(s) purgée(s)."
