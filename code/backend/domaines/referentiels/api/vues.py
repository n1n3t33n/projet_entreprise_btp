"""Points d'entrée du domaine « référentiels et catalogue » (UC-3 ; EF-REF-03
à 06, EF-REF-08, EF-REF-09).

Chaque vue déclare son ``ADroit`` (EF-AUT-07) ; les permissions sont créées en
données par la migration ``referentiels 0003``.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.identite.permissions import ADroit
from domaines.referentiels import selecteurs, services
from domaines.referentiels.api import serialiseurs as s
from domaines.referentiels.models import Article, CorpsEtat, RegleValidation
from socle.api_outils import obtenir_ou_404


def droit(ressource: str, action: str) -> list[Any]:
    return [IsAuthenticated(), ADroit("api", ressource, action)()]


def _valider(classe: Any, donnees: Any, objet: Any = None) -> dict[str, Any]:
    entree = classe(objet, data=donnees) if objet is not None else classe(data=donnees)
    entree.is_valid(raise_exception=True)
    return dict(entree.validated_data)


def _gamme_lue(id_gamme: str) -> Any:
    return obtenir_ou_404(selecteurs.gammes(), "Cette gamme est introuvable.", id_gamme=id_gamme)


# --- Familles, unités, articles ---------------------------------------------
class VueCategories(APIView):
    """GET /api/referentiels/categories."""

    def get_permissions(self) -> list[Any]:
        return droit("categories", "LIRE")

    @extend_schema(responses=s.CategorieSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.CategorieSerializer(selecteurs.categories(), many=True).data)


class VueUnites(APIView):
    """GET /api/referentiels/unites."""

    def get_permissions(self) -> list[Any]:
        return droit("unites", "LIRE")

    @extend_schema(responses=s.UniteSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.UniteSerializer(selecteurs.unites(), many=True).data)


class VueArticles(APIView):
    """GET et POST /api/referentiels/articles (EF-REF-03)."""

    def get_permissions(self) -> list[Any]:
        return droit("articles", "CREER" if self.request.method == "POST" else "LIRE")

    @extend_schema(responses=s.ArticleSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.ArticleSerializer(selecteurs.articles(), many=True).data)

    @extend_schema(request=s.ArticleSerializer, responses={201: s.ArticleSerializer})
    def post(self, request: Request) -> Response:
        article = services.enregistrer(Article(), _valider(s.ArticleSerializer, request.data))
        return Response(s.ArticleSerializer(article).data, status=status.HTTP_201_CREATED)


class VueArticle(APIView):
    """PUT /api/referentiels/articles/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("articles", "MODIFIER")

    @extend_schema(request=s.ArticleSerializer, responses=s.ArticleSerializer)
    def put(self, request: Request, id_article: str) -> Response:
        article = obtenir_ou_404(
            selecteurs.articles(), "Cet article est introuvable.", id_article=id_article
        )
        donnees = _valider(s.ArticleSerializer, request.data, article)
        return Response(s.ArticleSerializer(services.enregistrer(article, donnees)).data)


# --- Corps d'état et gammes (EF-REF-05, EF-REF-09) --------------------------
class VueCorpsEtat(APIView):
    """GET et POST /api/gammes/corps-etat."""

    def get_permissions(self) -> list[Any]:
        return droit("corps-etat", "CREER" if self.request.method == "POST" else "LIRE")

    @extend_schema(responses=s.CorpsEtatSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.CorpsEtatSerializer(selecteurs.corps_etat(), many=True).data)

    @extend_schema(request=s.CorpsEtatSerializer, responses={201: s.CorpsEtatSerializer})
    def post(self, request: Request) -> Response:
        corps = services.enregistrer(CorpsEtat(), _valider(s.CorpsEtatSerializer, request.data))
        return Response(s.CorpsEtatSerializer(corps).data, status=status.HTTP_201_CREATED)


class VueUnCorpsEtat(APIView):
    """PUT /api/gammes/corps-etat/{code}."""

    def get_permissions(self) -> list[Any]:
        return droit("corps-etat", "MODIFIER")

    @extend_schema(request=s.CorpsEtatSerializer, responses=s.CorpsEtatSerializer)
    def put(self, request: Request, code: str) -> Response:
        corps = obtenir_ou_404(
            selecteurs.corps_etat(), "Ce corps d'état est introuvable.", code_corps_etat=code
        )
        donnees = _valider(s.CorpsEtatSerializer, request.data, corps)
        donnees.pop("code_corps_etat", None)  # la clé ne change pas
        return Response(s.CorpsEtatSerializer(services.enregistrer(corps, donnees)).data)


class VueGammes(APIView):
    """GET /api/gammes."""

    def get_permissions(self) -> list[Any]:
        return droit("gammes", "LIRE")

    @extend_schema(responses=s.GammeSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.GammeSerializer(selecteurs.gammes(), many=True).data)


class VueGamme(APIView):
    """GET /api/gammes/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("gammes", "LIRE")

    @extend_schema(responses=s.GammeSerializer)
    def get(self, request: Request, id_gamme: str) -> Response:
        return Response(s.GammeSerializer(_gamme_lue(id_gamme)).data)


class VueEtapesGamme(APIView):
    """GET et PUT /api/gammes/{id}/etapes — PUT remplace les étapes d'un
    brouillon (une gamme publiée ne se modifie plus)."""

    def get_permissions(self) -> list[Any]:
        return droit("gammes", "MODIFIER" if self.request.method == "PUT" else "LIRE")

    @extend_schema(responses=s.EtapeModeleSerializer(many=True))
    def get(self, request: Request, id_gamme: str) -> Response:
        _gamme_lue(id_gamme)
        etapes = selecteurs.etapes_de_gamme(id_gamme)
        return Response(s.EtapeModeleSerializer(etapes, many=True).data)

    @extend_schema(request=s.EtapesEntreeSerializer, responses=s.EtapeModeleSerializer(many=True))
    def put(self, request: Request, id_gamme: str) -> Response:
        donnees = _valider(s.EtapesEntreeSerializer, request.data)
        services.remplacer_etapes(id_gamme, donnees["etapes"])
        etapes = selecteurs.etapes_de_gamme(id_gamme)
        return Response(s.EtapeModeleSerializer(etapes, many=True).data)


class VueVersionGamme(APIView):
    """POST /api/gammes/{id}/versions — brouillon de la version suivante."""

    def get_permissions(self) -> list[Any]:
        return droit("gammes", "CREER")

    @extend_schema(request=None, responses={201: s.GammeSerializer})
    def post(self, request: Request, id_gamme: str) -> Response:
        brouillon = services.nouvelle_version(id_gamme)
        return Response(
            s.GammeSerializer(_gamme_lue(str(brouillon.pk))).data, status=status.HTTP_201_CREATED
        )


class VuePublicationGamme(APIView):
    """POST /api/gammes/{id}/publication — EF-REF-09 (droit VALIDER)."""

    def get_permissions(self) -> list[Any]:
        return droit("gammes", "VALIDER")

    @extend_schema(request=None, responses=s.GammeSerializer)
    def post(self, request: Request, id_gamme: str) -> Response:
        services.publier(id_gamme)
        return Response(s.GammeSerializer(_gamme_lue(id_gamme)).data)


class VueArchivageGamme(APIView):
    """POST /api/gammes/{id}/archivage."""

    def get_permissions(self) -> list[Any]:
        return droit("gammes", "VALIDER")

    @extend_schema(request=None, responses=s.GammeSerializer)
    def post(self, request: Request, id_gamme: str) -> Response:
        services.archiver(id_gamme)
        return Response(s.GammeSerializer(_gamme_lue(id_gamme)).data)


# --- Listes de l'écran Stock et de l'avancement ------------------------------
class VueTypesMouvement(APIView):
    """GET /api/types-mouvement."""

    def get_permissions(self) -> list[Any]:
        return droit("types-mouvement", "LIRE")

    @extend_schema(responses=s.TypeMouvementSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.TypeMouvementSerializer(selecteurs.types_mouvement(), many=True).data)


class VueMotifsBlocage(APIView):
    """GET /api/motifs-blocage."""

    def get_permissions(self) -> list[Any]:
        return droit("motifs-blocage", "LIRE")

    @extend_schema(responses=s.MotifBlocageSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.MotifBlocageSerializer(selecteurs.motifs_blocage(), many=True).data)


# --- Règles de validation (EF-REF-08) ---------------------------------------
class VueRegles(APIView):
    """GET et POST /api/parametrage/regles."""

    def get_permissions(self) -> list[Any]:
        return droit("regles", "CREER" if self.request.method == "POST" else "LIRE")

    @extend_schema(responses=s.RegleSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(s.RegleSerializer(selecteurs.regles(), many=True).data)

    @extend_schema(request=s.RegleSerializer, responses={201: s.RegleSerializer})
    def post(self, request: Request) -> Response:
        regle = services.enregistrer(RegleValidation(), _valider(s.RegleSerializer, request.data))
        return Response(s.RegleSerializer(regle).data, status=status.HTTP_201_CREATED)


class VueRegle(APIView):
    """PUT /api/parametrage/regles/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("regles", "MODIFIER")

    @extend_schema(request=s.RegleSerializer, responses=s.RegleSerializer)
    def put(self, request: Request, id_regle: str) -> Response:
        regle = obtenir_ou_404(
            selecteurs.regles(), "Cette règle est introuvable.", id_regle=id_regle
        )
        donnees = _valider(s.RegleSerializer, request.data, regle)
        return Response(s.RegleSerializer(services.enregistrer(regle, donnees)).data)
