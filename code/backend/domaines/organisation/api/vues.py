"""Points d'entrée du domaine « organisation du chantier » (UC-3, EF-REF-01,
EF-REF-02, EF-REF-07).

Chaque vue déclare le droit qu'elle exige (``ADroit``, EF-AUT-07) ; les
permissions correspondantes sont des DONNÉES créées par la migration
``organisation 0004``. Les vues valident l'entrée, appellent ``services`` ou
``selecteurs``, et rendent la forme attendue par l'écran.
"""

from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.identite.permissions import ADroit
from domaines.organisation import selecteurs, services
from domaines.organisation.api import serialiseurs as s
from domaines.organisation.models import Logement, Magasin, ParametreChantier, Zone
from socle.api_outils import obtenir_ou_404
from socle.erreurs import ErreurApi


def droit(ressource: str, action: str) -> list[Any]:
    return [IsAuthenticated(), ADroit("api", ressource, action)()]


def _valider(classe: Any, donnees: Any, objet: Any = None) -> dict[str, Any]:
    entree = classe(objet, data=donnees) if objet is not None else classe(data=donnees)
    entree.is_valid(raise_exception=True)
    return dict(entree.validated_data)


# --- Chantiers (Référentiels) ----------------------------------------------
class VueChantiers(APIView):
    """GET /api/referentiels/chantiers."""

    def get_permissions(self) -> list[Any]:
        return droit("chantiers", "LIRE")

    @extend_schema(responses=s.ChantierSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.ChantierSerializer(selecteurs.chantiers(), many=True).data)


class VueChantier(APIView):
    """PUT /api/referentiels/chantiers/{id} — la création passe par l'import
    CSV (le contrat simulé n'a pas de POST)."""

    def get_permissions(self) -> list[Any]:
        return droit("chantiers", "MODIFIER")

    @extend_schema(request=s.ChantierSerializer, responses=s.ChantierSerializer)
    def put(self, request: Request, id_chantier: str) -> Response:
        chantier = obtenir_ou_404(
            selecteurs.chantiers(), "Ce chantier est introuvable.", id_chantier=id_chantier
        )
        donnees = _valider(s.ChantierSerializer, request.data, chantier)
        return Response(s.ChantierSerializer(services.enregistrer(chantier, donnees)).data)


class VueArborescence(APIView):
    """GET /api/referentiels/chantiers/{id}/arborescence — zones et logements."""

    def get_permissions(self) -> list[Any]:
        return droit("chantiers", "LIRE")

    @extend_schema(responses=s.ArborescenceSerializer)
    def get(self, request: Request, id_chantier: str) -> Response:
        chantier = selecteurs.arborescence(id_chantier)
        if chantier is None:
            raise ErreurApi(statut=404, motif="INTROUVABLE", message="Ce chantier est introuvable.")
        return Response(s.ArborescenceSerializer(chantier).data)


# --- Magasins ---------------------------------------------------------------
class VueMagasinsReferentiel(APIView):
    """GET et POST /api/referentiels/magasins (forme de l'écran Référentiels)."""

    def get_permissions(self) -> list[Any]:
        return droit("magasins", "CREER" if self.request.method == "POST" else "LIRE")

    @extend_schema(responses=s.MagasinReferentielSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.MagasinReferentielSerializer(selecteurs.magasins(), many=True).data)

    @extend_schema(
        request=s.MagasinReferentielSerializer,
        responses={201: s.MagasinReferentielSerializer},
    )
    def post(self, request: Request) -> Response:
        donnees = _valider(s.MagasinReferentielSerializer, request.data)
        magasin = services.enregistrer(Magasin(), donnees)
        return Response(
            s.MagasinReferentielSerializer(magasin).data, status=status.HTTP_201_CREATED
        )


class VueMagasinReferentiel(APIView):
    """PUT /api/referentiels/magasins/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("magasins", "MODIFIER")

    @extend_schema(request=s.MagasinReferentielSerializer, responses=s.MagasinReferentielSerializer)
    def put(self, request: Request, id_magasin: str) -> Response:
        magasin = obtenir_ou_404(
            selecteurs.magasins(), "Ce magasin est introuvable.", id_magasin=id_magasin
        )
        donnees = _valider(s.MagasinReferentielSerializer, request.data, magasin)
        return Response(s.MagasinReferentielSerializer(services.enregistrer(magasin, donnees)).data)


class VueMagasinsStock(APIView):
    """GET /api/magasins — forme de l'écran Stock (``libelle``, I-30)."""

    def get_permissions(self) -> list[Any]:
        return droit("magasins", "LIRE")

    @extend_schema(responses=s.MagasinStockSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.MagasinStockSerializer(selecteurs.magasins(), many=True).data)


# --- Zones et logements -----------------------------------------------------
class VueZones(APIView):
    """POST /api/referentiels/zones."""

    def get_permissions(self) -> list[Any]:
        return droit("zones", "CREER")

    @extend_schema(request=s.ZoneSerializer, responses={201: s.ZoneSerializer})
    def post(self, request: Request) -> Response:
        zone = services.enregistrer(Zone(), _valider(s.ZoneSerializer, request.data))
        return Response(s.ZoneSerializer(zone).data, status=status.HTTP_201_CREATED)


class VueZone(APIView):
    """PUT /api/referentiels/zones/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("zones", "MODIFIER")

    @extend_schema(request=s.ZoneSerializer, responses=s.ZoneSerializer)
    def put(self, request: Request, id_zone: str) -> Response:
        zone = obtenir_ou_404(selecteurs.zones(), "Cette zone est introuvable.", id_zone=id_zone)
        donnees = _valider(s.ZoneSerializer, request.data, zone)
        return Response(s.ZoneSerializer(services.enregistrer(zone, donnees)).data)


class VueLogements(APIView):
    """POST /api/referentiels/logements."""

    def get_permissions(self) -> list[Any]:
        return droit("logements", "CREER")

    @extend_schema(request=s.LogementSerializer, responses={201: s.LogementSerializer})
    def post(self, request: Request) -> Response:
        logement = services.enregistrer(Logement(), _valider(s.LogementSerializer, request.data))
        return Response(s.LogementSerializer(logement).data, status=status.HTTP_201_CREATED)


class VueLogement(APIView):
    """PUT /api/referentiels/logements/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("logements", "MODIFIER")

    @extend_schema(request=s.LogementSerializer, responses=s.LogementSerializer)
    def put(self, request: Request, id_logement: str) -> Response:
        logement = obtenir_ou_404(
            selecteurs.logements(), "Ce logement est introuvable.", id_logement=id_logement
        )
        donnees = _valider(s.LogementSerializer, request.data, logement)
        return Response(s.LogementSerializer(services.enregistrer(logement, donnees)).data)


class VueLogementsDuChantier(APIView):
    """GET /api/chantiers/{id}/logements — destinations d'une sortie de stock."""

    def get_permissions(self) -> list[Any]:
        return droit("logements", "LIRE")

    @extend_schema(responses=s.LogementDestinationSerializer(many=True))
    def get(self, request: Request, id_chantier: str) -> Response:
        logements = selecteurs.logements_du_chantier(id_chantier)
        return Response(s.LogementDestinationSerializer(logements, many=True).data)


class VueTypesLogement(APIView):
    """GET /api/referentiels/types-logement."""

    def get_permissions(self) -> list[Any]:
        return droit("types-logement", "LIRE")

    @extend_schema(responses=s.TypeLogementSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.TypeLogementSerializer(selecteurs.types_logement(), many=True).data)


# --- Paramètres de chantier (EF-REF-07) -------------------------------------
class VueParametres(APIView):
    """GET et POST /api/parametrage/parametres. ``?chantier=`` filtre ; sans
    lui, le chantier unique du pilote (I-35)."""

    def get_permissions(self) -> list[Any]:
        return droit("parametres", "CREER" if self.request.method == "POST" else "LIRE")

    @extend_schema(
        parameters=[OpenApiParameter("chantier", str, description="Identifiant du chantier.")],
        responses=s.ParametreSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        id_chantier = request.query_params.get("chantier")
        parametres = selecteurs.parametres(id_chantier)
        return Response(s.ParametreSerializer(parametres, many=True).data)

    @extend_schema(request=s.ParametreSerializer, responses={201: s.ParametreSerializer})
    def post(self, request: Request) -> Response:
        donnees = _valider(s.ParametreSerializer, request.data)
        id_chantier = donnees.pop("chantier_id", None)
        parametre = services.enregistrer_parametre(ParametreChantier(), donnees, id_chantier)
        return Response(s.ParametreSerializer(parametre).data, status=status.HTTP_201_CREATED)


class VueParametre(APIView):
    """PUT /api/parametrage/parametres/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("parametres", "MODIFIER")

    @extend_schema(request=s.ParametreSerializer, responses=s.ParametreSerializer)
    def put(self, request: Request, id_parametre: str) -> Response:
        parametre = obtenir_ou_404(
            selecteurs.parametres(), "Ce paramètre est introuvable.", id_parametre=id_parametre
        )
        donnees = _valider(s.ParametreSerializer, request.data, parametre)
        id_chantier = donnees.pop("chantier_id", None)
        resultat = services.enregistrer_parametre(parametre, donnees, id_chantier)
        return Response(s.ParametreSerializer(resultat).data)
