"""Points d'entrée des notifications (EF-NOT-01, Q-AS).

Chacun ne voit et ne marque que ses propres notifications (droits
``api.notifications.lire`` et ``modifier``, accordés à tous les rôles comme
``api.session.lire``). Pas de canal temps réel (Q-AS) : le web interroge
``/compteur`` toutes les 30 à 60 secondes, réponse très légère ; le mobile
reçoit ses notifications à chaque synchronisation (jeu ``notifications``).
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.identite.permissions import ADroit
from domaines.notifications import selecteurs
from domaines.notifications.api import serialiseurs as s
from domaines.notifications.services import lecture


def droit(action: str) -> list[Any]:
    return [IsAuthenticated(), ADroit("api", "notifications", action)()]


class VueNotifications(APIView):
    """GET /api/notifications — mes notifications, les plus récentes d'abord
    (``non_lues``, ``limite``)."""

    def get_permissions(self) -> list[Any]:
        return droit("LIRE")

    @extend_schema(
        parameters=[s.FiltreNotificationsSerializer],
        responses=s.NotificationSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        filtres = s.FiltreNotificationsSerializer(data=request.query_params)
        filtres.is_valid(raise_exception=True)
        lignes = selecteurs.de(request.user, filtres.validated_data["non_lues"])
        lignes = lignes[: filtres.validated_data["limite"]]
        return Response(s.NotificationSerializer(lignes, many=True).data)


class VueCompteur(APIView):
    """GET /api/notifications/compteur — nombre de notifications non lues
    (pastille de la cloche, interrogée périodiquement, Q-AS)."""

    def get_permissions(self) -> list[Any]:
        return droit("LIRE")

    @extend_schema(responses=s.CompteurSerializer)
    def get(self, request: Request) -> Response:
        return Response({"non_lues": selecteurs.nombre_non_lues(request.user)})


class VueLecture(APIView):
    """POST /api/notifications/{id}/lecture — marquer une notification lue."""

    def get_permissions(self) -> list[Any]:
        return droit("MODIFIER")

    @extend_schema(
        operation_id="notification_lecture", request=None, responses=s.NotificationSerializer
    )
    def post(self, request: Request, id_notification: str) -> Response:
        notification = lecture.marquer_lue(request.user, id_notification)
        return Response(s.NotificationSerializer(notification).data)


class VueLectureGroupee(APIView):
    """POST /api/notifications/lecture — tout marquer lu."""

    def get_permissions(self) -> list[Any]:
        return droit("MODIFIER")

    @extend_schema(
        operation_id="notifications_lecture_groupee",
        request=None,
        responses=s.LectureGroupeeSerializer,
    )
    def post(self, request: Request) -> Response:
        return Response({"nombre": lecture.tout_lire(request.user)})
