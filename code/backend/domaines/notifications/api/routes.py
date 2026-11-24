"""Routes du domaine « notifications » (EF-NOT-01)."""

from django.urls import path

from domaines.notifications.api import vues

urlpatterns = [
    path("notifications", vues.VueNotifications.as_view(), name="notifications"),
    path("notifications/compteur", vues.VueCompteur.as_view(), name="notifications-compteur"),
    path("notifications/lecture", vues.VueLectureGroupee.as_view(), name="notifications-lecture"),
    path(
        "notifications/<uuid:id_notification>/lecture",
        vues.VueLecture.as_view(),
        name="notification-lecture",
    ),
]
