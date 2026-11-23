"""Points d'entrée de la synchronisation (SQ-2, EF-SYN-01 à 06).

Réservés aux jetons mobiles liés à un appareil enrôlé (Q-AK) : le web n'a pas
de file d'envoi. Le droit ``api.synchronisation.creer`` ouvre l'envoi ; le
droit propre à chaque opération est vérifié événement par événement.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.identite.authentification import TYPE_MOBILE
from domaines.identite.permissions import ADroit
from domaines.identite.selecteurs import appareils as selecteurs_appareils
from domaines.synchronisation import selecteurs
from domaines.synchronisation.api import serialiseurs as s
from domaines.synchronisation.services import lots
from socle.erreurs import ErreurApi
from socle.limitation import LimitationAppareil
from socle.parseurs import JSONCompressible


class JetonMobile(BasePermission):
    """La requête porte un jeton mobile (lié à un appareil)."""

    message = "La synchronisation se fait depuis l'application mobile."

    def has_permission(self, request: Request, view: Any) -> bool:
        info = request.auth
        return getattr(info, "type", None) == TYPE_MOBILE and bool(
            getattr(info, "id_appareil", None)
        )


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
        return [IsAuthenticated(), JetonMobile(), ADroit("api", "synchronisation", "CREER")()]

    @extend_schema(
        request=s.LotEntreeSerializer, responses={201: s.LotSerializer, 200: s.LotSerializer}
    )
    def post(self, request: Request) -> Response:
        entree = s.LotEntreeSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        appareil = selecteurs_appareils.par_id(getattr(request.auth, "id_appareil", None))
        if appareil is None:
            raise ErreurApi(
                statut=403,
                motif="APPAREIL_REVOQUE",
                message="Cet appareil n'a plus accès à ChantierSync.",
            )
        lot, nouveau = lots.recevoir(request.user, appareil, _envoi(dict(entree.validated_data)))
        return Response(
            s.LotSerializer(selecteurs.lot(lot.pk)).data,
            status=status.HTTP_201_CREATED if nouveau else status.HTTP_200_OK,
        )
