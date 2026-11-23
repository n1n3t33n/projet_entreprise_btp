"""Points d'entrée de la synchronisation (SQ-2, EF-SYN-01 à 06).

Envoi des lots et téléchargement des références : réservés aux jetons
mobiles liés à un appareil enrôlé (Q-AK), le web n'a pas de file d'envoi. Le
droit ``api.synchronisation.creer`` ouvre l'échange ; le droit propre à chaque
opération ou à chaque jeu de données est vérifié un à un.

Supervision des anomalies (EF-SYN-05) : web ou mobile, droits
``api.anomalies.lire`` et ``api.anomalies.modifier``.
"""

from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.identite.authentification import TYPE_MOBILE
from domaines.identite.models import Appareil
from domaines.identite.permissions import ADroit
from domaines.identite.selecteurs import appareils as selecteurs_appareils
from domaines.synchronisation import selecteurs
from domaines.synchronisation.api import serialiseurs as s
from domaines.synchronisation.services import anomalies, lots, references
from socle.erreurs import ErreurApi
from socle.limitation import LimitationAppareil
from socle.parseurs import JSONCompressible
from socle.synchronisation import REFERENCES

LIMITE_ANOMALIES = 200
CHIFFRES_VERSION_MAX = 18


class JetonMobile(BasePermission):
    """La requête porte un jeton mobile (lié à un appareil)."""

    message = "La synchronisation se fait depuis l'application mobile."

    def has_permission(self, request: Request, view: Any) -> bool:
        info = request.auth
        return getattr(info, "type", None) == TYPE_MOBILE and bool(
            getattr(info, "id_appareil", None)
        )


def droits_mobiles() -> list[Any]:
    return [IsAuthenticated(), JetonMobile(), ADroit("api", "synchronisation", "CREER")()]


def droit(ressource: str, action: str) -> list[Any]:
    return [IsAuthenticated(), ADroit("api", ressource, action)()]


def _appareil(request: Request) -> Appareil:
    appareil = selecteurs_appareils.par_id(getattr(request.auth, "id_appareil", None))
    if appareil is None:
        raise ErreurApi(
            statut=403,
            motif="APPAREIL_REVOQUE",
            message="Cet appareil n'a plus accès à ChantierSync.",
        )
    return appareil


def _envoi(donnees: dict[str, Any]) -> lots.Envoi:
    return lots.Envoi(
        id_lot=donnees["id_lot"],
        horodatage_envoi=donnees.get("horodatage_envoi"),
        evenements=tuple(
            lots.EvenementRecu(
                uuid=e["uuid"],
                type=e["type"],
                charge_utile=dict(e["charge_utile"]),
                horodatage_appareil=e.get("horodatage_appareil"),
            )
            for e in donnees["evenements"]
        ),
    )


class VueLots(APIView):
    """POST /api/synchronisation/lots — envoi d'un lot d'événements (SQ-2).

    201 pour un lot nouveau, 200 pour un lot déjà reçu (mêmes résultats).
    Corps éventuellement compressé (``Content-Encoding: gzip``, ENF-02)."""

    parser_classes = [JSONCompressible]
    throttle_classes = [LimitationAppareil]

    def get_permissions(self) -> list[Any]:
        return droits_mobiles()

    @extend_schema(
        request=s.LotEntreeSerializer, responses={201: s.LotSerializer, 200: s.LotSerializer}
    )
    def post(self, request: Request) -> Response:
        entree = s.LotEntreeSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        appareil = _appareil(request)
        lot, nouveau = lots.recevoir(request.user, appareil, _envoi(dict(entree.validated_data)))
        return Response(
            s.LotSerializer(selecteurs.lot(lot.pk)).data,
            status=status.HTTP_201_CREATED if nouveau else status.HTTP_200_OK,
        )


class VueReferences(APIView):
    """GET /api/synchronisation/references — données de référence changées
    depuis la version que l'appareil détient (EF-SYN-04, Q-AI).

    Le téléphone passe, pour chaque jeu, la version qu'il détient
    (``?articles=123&stock=456``) ; un jeu absent vaut 0 (jamais reçu)."""

    throttle_classes = [LimitationAppareil]

    def get_permissions(self) -> list[Any]:
        return droits_mobiles()

    @extend_schema(
        parameters=[
            OpenApiParameter(code, int, description="Version détenue par l'appareil.")
            for code in sorted(REFERENCES)
        ],
        responses=s.ReferencesSerializer,
    )
    def get(self, request: Request) -> Response:
        versions = {}
        for code in REFERENCES:
            valeur = str(request.query_params.get(code, ""))
            # Une version valide tient en 18 chiffres (bigint du MPD).
            if valeur.isdigit() and len(valeur) <= CHIFFRES_VERSION_MAX:
                versions[code] = int(valeur)
        jeux, inchanges = references.telecharger(request.user, _appareil(request), versions)
        return Response(
            s.ReferencesSerializer(
                {"jeux": [jeu.__dict__ for jeu in jeux], "inchanges": inchanges}
            ).data
        )


class VueAnomalies(APIView):
    """GET /api/synchronisation/anomalies — anomalies de synchronisation, les
    plus récentes d'abord, filtrables par statut et par type (EF-SYN-05)."""

    def get_permissions(self) -> list[Any]:
        return droit("anomalies", "LIRE")

    @extend_schema(
        parameters=[s.FiltreAnomaliesSerializer], responses=s.AnomalieSerializer(many=True)
    )
    def get(self, request: Request) -> Response:
        filtres = s.FiltreAnomaliesSerializer(data=request.query_params)
        filtres.is_valid(raise_exception=True)
        lignes = selecteurs.anomalies(**filtres.validated_data)[:LIMITE_ANOMALIES]
        return Response(s.AnomalieSerializer(lignes, many=True).data)


class VueTraitementAnomalie(APIView):
    """POST /api/synchronisation/anomalies/{id}/traitement — marque une
    anomalie traitée (EF-SYN-05). Sans effet si elle l'est déjà."""

    def get_permissions(self) -> list[Any]:
        return droit("anomalies", "MODIFIER")

    @extend_schema(request=None, responses=s.AnomalieSerializer)
    def post(self, request: Request, id_anomalie: str) -> Response:
        anomalie, _change = anomalies.traiter(id_anomalie)
        relue = selecteurs.anomalies().get(pk=anomalie.pk)
        return Response(s.AnomalieSerializer(relue).data)
