"""Points d'entrée de l'espace acquéreur (UC-5, EF-ACQ-01, EF-ACQ-02).

Lecture seule ; la portée vient du compte connecté, jamais d'un paramètre
(RG-D10). Droit ``api.acquereur.lire``, accordé au rôle ACQUEREUR.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.acquereur.api import serialiseurs as s
from domaines.acquereur.services import espace
from domaines.identite.permissions import ADroit


def droit() -> list[Any]:
    return [IsAuthenticated(), ADroit("api", "acquereur", "LIRE")()]


class VueLogement(APIView):
    """GET /api/acquereur/logement — avancement du logement de l'acquéreur."""

    def get_permissions(self) -> list[Any]:
        return droit()

    @extend_schema(responses=s.AvancementLogementSerializer)
    def get(self, request: Request) -> Response:
        return Response(s.AvancementLogementSerializer(espace.logement(request.user)).data)


class VueNotifications(APIView):
    """GET /api/acquereur/notifications — étapes franchies annoncées."""

    def get_permissions(self) -> list[Any]:
        return droit()

    @extend_schema(responses=s.NotificationAcquereurSerializer(many=True))
    def get(self, request: Request) -> Response:
        lignes = espace.notifications(request.user)
        return Response(s.NotificationAcquereurSerializer(lignes, many=True).data)
