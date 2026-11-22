"""Points d'entrée du domaine « avancement » (UC-2 ; EF-AVA-01 à 10).

Chaque vue déclare son droit (``ADroit``, EF-AUT-07) ; ``services.acces``
vérifie en plus que le chantier de l'étape est couvert par ce droit. Les
permissions sont des données (migration ``avancement 0003``).
"""

from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.avancement import selecteurs
from domaines.avancement.api import serialiseurs as s
from domaines.avancement.constantes import FICHE_OUVERTE
from domaines.avancement.services import acces, fiches
from domaines.identite.permissions import ADroit

LIMITE_FICHES = 100


def droit(ressource: str, action: str) -> list[Any]:
    return [IsAuthenticated(), ADroit("api", ressource, action)()]


def _valider(classe: Any, donnees: Any) -> dict[str, Any]:
    entree = classe(data=donnees)
    entree.is_valid(raise_exception=True)
    return dict(entree.validated_data)


def _encadre(utilisateur: Any) -> bool:
    """Vrai si l'utilisateur affecte des étapes (encadrement) : il voit les
    fiches de tous ; sinon chacun ne voit que les siennes (RG-A3)."""
    return acces.chantiers_couverts(utilisateur, "fiches-route", "CREER") != set()


# --- Étapes d'un logement (EF-AVA-01, EF-AVA-03) ----------------------------------
class VueEtapesLogement(APIView):
    """GET /api/logements/{id}/etapes — étapes du logement, dans l'ordre."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.LigneEtapeSerializer(many=True))
    def get(self, request: Request, id_logement: str) -> Response:
        logement = acces.logement_autorise(request.user, id_logement, "avancement", "LIRE")
        etapes = selecteurs.etapes_du_logement(logement.pk)
        return Response(s.LigneEtapeSerializer(etapes, many=True).data)


# --- Fiches de route (RG-A7, EF-AVA-02, 03, 08) ---------------------------------------
class VueFiches(APIView):
    """GET /api/fiches-route?technicien=&statut= — un technicien ne voit que
    ses fiches ; l'encadrement voit celles de tous."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "LIRE")

    @extend_schema(
        parameters=[OpenApiParameter("technicien", str), OpenApiParameter("statut", str)],
        responses=s.FicheRouteSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        technicien = request.query_params.get("technicien")
        if not _encadre(request.user):
            technicien = str(request.user.pk)
        requete = selecteurs.fiches(technicien)
        if request.query_params.get("statut"):
            requete = requete.filter(statut=request.query_params["statut"])
        return Response(s.FicheRouteSerializer(requete[:LIMITE_FICHES], many=True).data)


class VueFicheCourante(APIView):
    """GET /api/fiches-route/courante — fiches ouvertes de l'utilisateur
    (écran « Mes fiches » du mobile, EF-AVA-03)."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "LIRE")

    @extend_schema(responses=s.FicheRouteSerializer(many=True))
    def get(self, request: Request) -> Response:
        ouvertes = selecteurs.fiches(request.user.pk).filter(statut=FICHE_OUVERTE)
        return Response(s.FicheRouteSerializer(ouvertes, many=True).data)


class VueFiche(APIView):
    """GET /api/fiches-route/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "LIRE")

    @extend_schema(responses=s.FicheRouteSerializer)
    def get(self, request: Request, id_fiche: str) -> Response:
        fiche = fiches.fiche_autorisee(request.user, id_fiche, "CREER")
        return Response(s.FicheRouteSerializer(fiche).data)


class VueAffectations(APIView):
    """POST /api/fiches-route/affectations — affecter un lot d'étapes à un
    technicien, avec date prévue ; la réaffectation est tracée (RG-A3)."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "CREER")

    @extend_schema(
        request=s.AffectationEntreeSerializer, responses=s.LigneEtapeSerializer(many=True)
    )
    def post(self, request: Request) -> Response:
        donnees = _valider(s.AffectationEntreeSerializer, request.data)
        affectees = fiches.affecter(
            request.user,
            donnees["etapes"],
            donnees["technicien_id_utilisateur"],
            donnees.get("date_prevue"),
        )
        relues = selecteurs.etapes().filter(pk__in=[etape.pk for etape in affectees])
        return Response(s.LigneEtapeSerializer(relues, many=True).data)


class VueCloture(APIView):
    """POST /api/fiches-route/{id}/cloture — fin de cycle, report motivé des
    étapes non faites (EF-AVA-08). Le technicien clôture sa propre fiche."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "LIRE")

    @extend_schema(request=s.ClotureEntreeSerializer, responses=s.FicheRouteSerializer)
    def post(self, request: Request, id_fiche: str) -> Response:
        donnees = _valider(s.ClotureEntreeSerializer, request.data)
        fiche = fiches.fiche_autorisee(request.user, id_fiche, "MODIFIER")
        motifs = {str(r["id_etape"]): r["motif"] for r in donnees.get("reports", [])}
        fiches.verifier_motifs(fiche, motifs)
        return Response(s.FicheRouteSerializer(fiches.cloturer(fiche, motifs)).data)
