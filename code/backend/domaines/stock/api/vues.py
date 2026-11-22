"""Points d'entrée du domaine « stock » (UC-1 ; EF-STK-01 à 03, 05 à 07, 09 à 11).

Chaque vue déclare son droit (``ADroit``, EF-AUT-07) ; ``services.acces``
vérifie en plus que le magasin demandé est couvert par ce droit (périmètre).
Les permissions sont des données (migration ``stock 0003``).
"""

from datetime import date, datetime, time
from typing import Any

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.identite.permissions import ADroit
from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.stock import selecteurs
from domaines.stock.api import serialiseurs as s
from domaines.stock.services import acces, annulation, mouvements, parametres, seuils, validation
from socle.api_outils import donnee_invalide

LIMITE_PAR_DEFAUT = 200
LIMITE_MAXIMALE = 1000


def droit(ressource: str, action: str) -> list[Any]:
    return [IsAuthenticated(), ADroit("api", ressource, action)()]


def _valider(classe: Any, donnees: Any) -> dict[str, Any]:
    entree = classe(data=donnees)
    entree.is_valid(raise_exception=True)
    return dict(entree.validated_data)


def contexte() -> dict[str, Any]:
    return {"parametres": parametres.ParametresParChantier()}


# --- Stock d'un magasin (EF-STK-05, EF-STK-06) -----------------------------------
class VueStockMagasin(APIView):
    """GET /api/magasins/{id}/stock — articles suivis, seuils et stock courant."""

    def get_permissions(self) -> list[Any]:
        return droit("stock", "LIRE")

    @extend_schema(responses=s.LigneStockSerializer(many=True))
    def get(self, request: Request, id_magasin: str) -> Response:
        magasin = acces.magasin_autorise(request.user, id_magasin, "stock", "LIRE")
        lignes = selecteurs.lignes_stock(magasin.pk)
        return Response(s.LigneStockSerializer(lignes, many=True).data)


class VueSeuil(APIView):
    """PUT /api/magasins/{id}/articles/{id}/seuil — seuils minimal et critique."""

    def get_permissions(self) -> list[Any]:
        return droit("seuils", "MODIFIER")

    @extend_schema(request=s.SeuilEntreeSerializer, responses={204: None})
    def put(self, request: Request, id_magasin: str, id_article: str) -> Response:
        magasin = acces.magasin_autorise(request.user, id_magasin, "seuils", "MODIFIER")
        donnees = _valider(s.SeuilEntreeSerializer, request.data)
        seuils.definir(magasin.pk, id_article, donnees["seuil_minimal"], donnees["seuil_critique"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class VueArborescence(APIView):
    """GET /api/stock/arborescence — chantier › magasin › familles."""

    def get_permissions(self) -> list[Any]:
        return droit("stock", "LIRE")

    @extend_schema(responses=s.NoeudStockSerializer(many=True))
    def get(self, request: Request) -> Response:
        couverts = acces.magasins_couverts(request.user, "stock", "LIRE")
        magasins = selecteurs_organisation.magasins().select_related("chantier")
        if couverts is not None:
            magasins = magasins.filter(id_magasin__in=couverts)
        return Response(s.NoeudStockSerializer(selecteurs.arborescence(magasins), many=True).data)


class VueAlertes(APIView):
    """GET /api/stock/alertes — alertes de stock ouvertes (EF-STK-07)."""

    def get_permissions(self) -> list[Any]:
        return droit("stock", "LIRE")

    @extend_schema(responses=s.AlerteSerializer(many=True))
    def get(self, request: Request) -> Response:
        couverts = acces.magasins_couverts(request.user, "stock", "LIRE")
        return Response(s.AlerteSerializer(selecteurs.alertes_ouvertes(couverts), many=True).data)


# --- Mouvements (EF-STK-01 à 03, EF-STK-10) ----------------------------------------
def _date(valeur: str | None, champ: str, fin_de_journee: bool = False) -> datetime | None:
    if not valeur:
        return None
    try:
        jour = date.fromisoformat(valeur)
    except ValueError as erreur:
        raise donnee_invalide(champ, "Date attendue au format AAAA-MM-JJ.") from erreur
    return timezone.make_aware(datetime.combine(jour, time.max if fin_de_journee else time.min))


def _limite(valeur: str | None) -> int:
    try:
        limite = int(valeur) if valeur else LIMITE_PAR_DEFAUT
    except ValueError as erreur:
        raise donnee_invalide("limite", "Nombre attendu.") from erreur
    return max(1, min(limite, LIMITE_MAXIMALE))


class VueMouvements(APIView):
    """GET /api/mouvements (historique filtrable, EF-STK-10) et POST
    /api/mouvements (saisie, idempotente sur ``uuid``)."""

    def get_permissions(self) -> list[Any]:
        return droit("mouvements", "CREER" if self.request.method == "POST" else "LIRE")

    @extend_schema(
        parameters=[
            OpenApiParameter("magasin", str),
            OpenApiParameter("article", str),
            OpenApiParameter("logement", str),
            OpenApiParameter("auteur", str),
            OpenApiParameter("debut", str, description="AAAA-MM-JJ"),
            OpenApiParameter("fin", str, description="AAAA-MM-JJ"),
            OpenApiParameter("limite", int, description="1 à 1000, 200 par défaut"),
        ],
        responses=s.MouvementSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        filtres = request.query_params
        requete = selecteurs.mouvements(acces.magasins_couverts(request.user, "mouvements", "LIRE"))
        for parametre, champ in (
            ("magasin", "magasin_id"),
            ("article", "article_id"),
            ("logement", "logement_id"),
            ("auteur", "utilisateur_id"),
        ):
            if filtres.get(parametre):
                requete = requete.filter(**{champ: filtres[parametre]})
        debut = _date(filtres.get("debut"), "debut")
        fin = _date(filtres.get("fin"), "fin", fin_de_journee=True)
        if debut:
            requete = requete.filter(date_operation__gte=debut)
        if fin:
            requete = requete.filter(date_operation__lte=fin)
        lignes = requete[: _limite(filtres.get("limite"))]
        return Response(s.MouvementSerializer(lignes, many=True, context=contexte()).data)

    @extend_schema(
        request=s.MouvementEntreeSerializer,
        responses={201: s.MouvementSerializer, 200: s.MouvementSerializer},
    )
    def post(self, request: Request) -> Response:
        donnees = _valider(s.MouvementEntreeSerializer, request.data)
        magasin = acces.magasin_autorise(
            request.user, donnees["magasin_id_magasin"], "mouvements", "CREER"
        )
        saisie = mouvements.Saisie(
            magasin=magasin,
            article=donnees["article_id_article"],
            type_mouvement=donnees["type_mouvement_code_type_mouvement"],
            quantite_saisie=donnees["quantite_saisie"],
            code_unite=donnees.get("code_unite"),
            uuid=donnees.get("uuid"),
            logement=donnees.get("logement_id_logement"),
            corps_etat=donnees.get("corps_etat"),
            beneficiaire=donnees.get("beneficiaire") or None,
            motif=donnees.get("motif") or None,
            reference_externe=donnees.get("reference_externe") or None,
            date_operation=donnees.get("date_operation"),
            horodatage_appareil=donnees.get("horodatage_appareil"),
        )
        mouvement, cree = mouvements.enregistrer(request.user, saisie)
        relu = selecteurs.mouvements().get(pk=mouvement.pk)
        return Response(
            s.MouvementSerializer(relu, context=contexte()).data,
            status=status.HTTP_201_CREATED if cree else status.HTTP_200_OK,
        )


class VueMouvementsArticle(APIView):
    """GET /api/magasins/{id}/articles/{id}/mouvements — fiche article."""

    def get_permissions(self) -> list[Any]:
        return droit("mouvements", "LIRE")

    @extend_schema(responses=s.MouvementSerializer(many=True))
    def get(self, request: Request, id_magasin: str, id_article: str) -> Response:
        magasin = acces.magasin_autorise(request.user, id_magasin, "mouvements", "LIRE")
        lignes = selecteurs.mouvements().filter(magasin=magasin, article_id=id_article)
        return Response(
            s.MouvementSerializer(lignes[:LIMITE_PAR_DEFAUT], many=True, context=contexte()).data
        )


# --- Validation et annulation (EF-STK-09, EF-STK-11) ---------------------------------
class VueMouvementsAValider(APIView):
    """GET /api/mouvements/a-valider — sorties en attente de décision, les plus
    anciennes d'abord (statut A_VALIDER ou EN_ALERTE)."""

    def get_permissions(self) -> list[Any]:
        return droit("mouvements", "VALIDER")

    @extend_schema(responses=s.MouvementSerializer(many=True))
    def get(self, request: Request) -> Response:
        couverts = acces.magasins_couverts(request.user, "mouvements", "VALIDER")
        lignes = selecteurs.en_attente(couverts)[:LIMITE_MAXIMALE]
        return Response(s.MouvementSerializer(lignes, many=True, context=contexte()).data)


class VueDecision(APIView):
    """POST /api/mouvements/{uuid}/validation — ACCEPTE ou REFUSE (motif
    obligatoire pour un refus) ; l'auteur du mouvement ne peut pas décider
    (RG-D8, RG-D11)."""

    def get_permissions(self) -> list[Any]:
        return droit("mouvements", "VALIDER")

    @extend_schema(request=s.DecisionEntreeSerializer, responses=s.MouvementSerializer)
    def post(self, request: Request, uuid_mouvement: str) -> Response:
        donnees = _valider(s.DecisionEntreeSerializer, request.data)
        mouvement = validation.decider(
            request.user,
            uuid_mouvement,
            donnees["decision"],
            donnees.get("motif"),
            donnees.get("uuid"),
        )
        return Response(s.MouvementSerializer(mouvement, context=contexte()).data)


class VueAnnulation(APIView):
    """POST /api/mouvements/{uuid}/annulation — contre-mouvement justifié
    (RG-S8) ; rend le contre-mouvement créé."""

    def get_permissions(self) -> list[Any]:
        return droit("mouvements", "VALIDER")

    @extend_schema(request=s.AnnulationEntreeSerializer, responses={201: s.MouvementSerializer})
    def post(self, request: Request, uuid_mouvement: str) -> Response:
        donnees = _valider(s.AnnulationEntreeSerializer, request.data)
        contre = annulation.annuler(request.user, uuid_mouvement, donnees["motif"])
        relu = selecteurs.mouvements().get(pk=contre.pk)
        return Response(
            s.MouvementSerializer(relu, context=contexte()).data, status=status.HTTP_201_CREATED
        )
