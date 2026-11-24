"""Points d'entrée du pilotage transverse (EF-DSH-06, EF-DSH-07).

Le pilotage propre à un domaine (avancement, stock, journal) reste dans ce
domaine ; ici, seulement ce qui assemble plusieurs domaines par le registre
des indicateurs.
"""

from datetime import timedelta
from typing import Any

from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.identite.permissions import ADroit
from domaines.pilotage.api import serialiseurs as s
from domaines.pilotage.services import rapports
from socle.indicateurs import RAPPORT, USAGE


def droit(ressource: str) -> list[Any]:
    return [IsAuthenticated(), ADroit("api", ressource, "LIRE")()]


class VueRapportHebdomadaire(APIView):
    """GET /api/pilotage/rapport-hebdomadaire?semaine=2026-W47&export=csv —
    rapport de la semaine (la dernière complète par défaut), en JSON ou en
    fichier CSV pour la réunion des associés (EF-DSH-06)."""

    def get_permissions(self) -> list[Any]:
        return droit("rapport-hebdomadaire")

    @extend_schema(
        parameters=[
            OpenApiParameter("semaine", str, description="Semaine ISO, par exemple 2026-W47."),
            OpenApiParameter(
                "export", str, enum=["csv"], description="csv : fichier à télécharger."
            ),
        ],
        responses=s.RapportSerializer,
    )
    def get(self, request: Request) -> Response | HttpResponse:
        code, debut, fin = rapports.semaine(request.query_params.get("semaine"))
        lignes = rapports.calculer(RAPPORT, debut, fin)
        if request.query_params.get("export") == "csv":
            reponse = HttpResponse(rapports.en_csv(lignes), content_type="text/csv; charset=utf-8")
            reponse["Content-Disposition"] = f'attachment; filename="rapport-{code}.csv"'
            return reponse
        return Response(
            s.RapportSerializer({"semaine": code, "du": debut, "au": fin, "lignes": lignes}).data
        )


class VueUsage(APIView):
    """GET /api/pilotage/usage?jours=7 — indicateurs d'usage du pilote sur
    les derniers jours (EF-DSH-07)."""

    def get_permissions(self) -> list[Any]:
        return droit("usage")

    @extend_schema(parameters=[s.FiltreUsageSerializer], responses=s.UsageSerializer)
    def get(self, request: Request) -> Response:
        filtre = s.FiltreUsageSerializer(data=request.query_params)
        filtre.is_valid(raise_exception=True)
        fin = timezone.localdate()
        debut = fin - timedelta(days=filtre.validated_data["jours"] - 1)
        lignes = rapports.calculer(USAGE, debut, fin)
        return Response(s.UsageSerializer({"du": debut, "au": fin, "lignes": lignes}).data)
