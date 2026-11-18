"""Points d'entrée du domaine identité.

Chaque vue ne fait que : valider l'entrée (sérialiseur), appeler un service,
mettre la réponse en forme. Chaque vue déclare son droit ``ADroit(...)``
(EF-AUT-07) ; la connexion seule est publique (``AllowAny`` explicite).
Références : UC-4, SQ-5, CL-1, MPD-1 ; contrat web/mobile du rapport B0 § 3.2.
"""

import math
from typing import Any, NoReturn

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.identite.api import serialiseurs as s
from domaines.identite.constantes import (
    ACTION_CREER,
    ACTION_LIRE,
    ACTION_MODIFIER,
    AUDIT_DECONNEXION,
    MODULE_API,
    OBJET_UTILISATEUR,
)
from domaines.identite.models import Appareil, DroitAccorde, Perimetre, Permission, Role
from domaines.identite.permissions import ADroit
from domaines.identite.selecteurs import appareils as selecteur_appareils
from domaines.identite.selecteurs import audit as selecteur_audit
from domaines.identite.selecteurs import comptes as selecteur_comptes
from domaines.identite.services import appareils as service_appareils
from domaines.identite.services import audit as service_audit
from domaines.identite.services import comptes as service_comptes
from domaines.identite.services import matrice as service_matrice
from domaines.identite.services.appareils import DonneesAppareil
from domaines.identite.services.connexion import connecter
from domaines.identite.services.droits import affectations_actives, droits_effectifs
from socle.erreurs import ErreurApi
from socle.limitation import LimitationConnexionParIdentifiant, LimitationConnexionParIP
from socle.reseau import adresse_client

ERREURS = {400: s.ErreurSerializer, 401: s.ErreurSerializer, 403: s.ErreurSerializer}


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------
class VueConnexion(APIView):
    """POST /api/auth/connexion — connexion en ligne (SQ-5 étapes 2 à 5).

    Publique par nature. Limitée par IP et par identifiant (exigence 6.3) ;
    l'excès répond « 429 VERROUILLE » avec le délai restant, forme que le web
    affiche déjà (EF-AUT-04, arbitrage Q11).
    """

    authentication_classes: list[Any] = []
    permission_classes = [AllowAny]
    throttle_classes = [LimitationConnexionParIP, LimitationConnexionParIdentifiant]

    def throttled(self, request: Request, wait: float | None) -> NoReturn:
        attente = max(1, math.ceil(wait or 1))
        raise ErreurApi(
            statut=429,
            motif="VERROUILLE",
            message="Trop de tentatives de connexion. Patientez avant de réessayer.",
            secondes_restantes=attente,
            en_tetes={"Retry-After": str(attente)},
        )

    @extend_schema(
        request=s.ConnexionEntreeSerializer,
        responses={200: s.SessionSerializer, **ERREURS, 429: s.ErreurSerializer},
        auth=[],
    )
    def post(self, request: Request) -> Response:
        entree = s.ConnexionEntreeSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        donnees = entree.validated_data
        bloc = donnees.get("appareil")
        resultat = connecter(
            identifiant=donnees["identifiant"],
            mot_de_passe=donnees["mot_de_passe"],
            donnees_appareil=DonneesAppareil(**bloc) if bloc else None,
            adresse_ip=adresse_client(request),
        )
        # On passe les OBJETS au sérialiseur englobant : c'est lui qui met en
        # forme l'utilisateur et les droits (une seule sérialisation).
        corps = {
            "jeton": resultat.jeton,
            "utilisateur": resultat.utilisateur,
            "connecte_le": resultat.connecte_le,
            "id_appareil": resultat.appareil.pk if resultat.appareil else None,
            "droits": droits_effectifs(resultat.utilisateur),
        }
        return Response(s.SessionSerializer(corps).data)


class VueDeconnexion(APIView):
    """POST /api/auth/deconnexion — trace la déconnexion (RG-D9).

    Limite documentée (arbitrage Q2) : le jeton web reste valable jusqu'à
    ses 8 h ; c'est le client qui l'oublie.
    """

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "session", ACTION_LIRE)]

    @extend_schema(request=None, responses={204: None, 401: s.ErreurSerializer})
    def post(self, request: Request) -> Response:
        service_audit.consigner(
            request.user, AUDIT_DECONNEXION, OBJET_UTILISATEUR, adresse_client(request)
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class VueMoi(APIView):
    """GET /api/auth/moi — profil, affectations et droits effectifs.

    Sert au mobile pour remplacer sa table de navigation codée en dur
    (``ongletsPour``, I-06) par la donnée de la matrice, comme le web.
    """

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "session", ACTION_LIRE)]

    @extend_schema(responses={200: s.ProfilSerializer, 401: s.ErreurSerializer})
    def get(self, request: Request) -> Response:
        utilisateur = request.user
        id_appareil = getattr(request.auth, "id_appareil", None)
        appareil = (
            Appareil.objects.select_related("utilisateur").filter(pk=id_appareil).first()
            if id_appareil
            else None
        )
        corps = {
            "utilisateur": utilisateur,
            "affectations": list(affectations_actives(utilisateur)),
            "droits": droits_effectifs(utilisateur),
            "appareil": appareil,
            "horodatage_serveur": timezone.now(),
        }
        return Response(s.ProfilSerializer(corps).data)


# ---------------------------------------------------------------------------
# Comptes et périmètres (EF-AUT-01, EF-AUT-02)
# ---------------------------------------------------------------------------
class VuePerimetres(APIView):
    """GET /api/auth/perimetres."""

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "perimetres", ACTION_LIRE)]

    @extend_schema(responses={200: s.PerimetreSerializer(many=True), **ERREURS})
    def get(self, request: Request) -> Response:
        perimetres = Perimetre.objects.order_by("libelle")
        return Response(s.PerimetreSerializer(perimetres, many=True).data)


def _saisie(donnees: dict[str, Any]) -> service_comptes.SaisieCompte:
    return service_comptes.SaisieCompte(
        identifiant=donnees["identifiant"],
        nom=donnees["nom"],
        prenom=donnees["prenom"],
        fonction=donnees.get("fonction", ""),
        statut=donnees["statut"],
        code_role=donnees["role_code_role"],
        id_perimetre=str(donnees["perimetre_id_perimetre"]),
        mot_de_passe=donnees.get("mot_de_passe"),
    )


class VueComptes(APIView):
    """GET /api/auth/comptes (lister) et POST /api/auth/comptes (créer)."""

    def get_permissions(self) -> list[Any]:
        action = ACTION_CREER if self.request.method == "POST" else ACTION_LIRE
        return [IsAuthenticated(), ADroit(MODULE_API, "comptes", action)()]

    @extend_schema(responses={200: s.UtilisateurSerializer(many=True), **ERREURS})
    def get(self, request: Request) -> Response:
        return Response(s.UtilisateurSerializer(selecteur_comptes.lister(), many=True).data)

    @extend_schema(
        request=s.CompteEntreeSerializer,
        responses={201: s.UtilisateurSerializer, **ERREURS},
    )
    def post(self, request: Request) -> Response:
        entree = s.CompteEntreeSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        utilisateur = service_comptes.creer(
            request.user, _saisie(entree.validated_data), adresse_client(request)
        )
        return Response(s.UtilisateurSerializer(utilisateur).data, status=status.HTTP_201_CREATED)


class VueCompte(APIView):
    """PUT /api/auth/comptes/{id} — modifier ou désactiver un compte."""

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "comptes", ACTION_MODIFIER)]

    @extend_schema(
        request=s.CompteEntreeSerializer,
        responses={200: s.UtilisateurSerializer, 404: s.ErreurSerializer, **ERREURS},
    )
    def put(self, request: Request, id_utilisateur: str) -> Response:
        entree = s.CompteEntreeSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        utilisateur = service_comptes.modifier(
            request.user, id_utilisateur, _saisie(entree.validated_data), adresse_client(request)
        )
        return Response(s.UtilisateurSerializer(utilisateur).data)


# ---------------------------------------------------------------------------
# Matrice des droits (EF-AUT-02, EF-AUT-07)
# ---------------------------------------------------------------------------
class VueRoles(APIView):
    """GET /api/droits/roles."""

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "droits", ACTION_LIRE)]

    @extend_schema(responses={200: s.RoleSerializer(many=True), **ERREURS})
    def get(self, request: Request) -> Response:
        return Response(s.RoleSerializer(Role.objects.order_by("code_role"), many=True).data)


class VuePermissions(APIView):
    """GET /api/droits/permissions."""

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "droits", ACTION_LIRE)]

    @extend_schema(responses={200: s.PermissionSerializer(many=True), **ERREURS})
    def get(self, request: Request) -> Response:
        permissions = Permission.objects.order_by("module", "ressource", "action")
        return Response(s.PermissionSerializer(permissions, many=True).data)


class VueDroitsAccordes(APIView):
    """GET /api/droits/accordes (lire) et PUT (remplacer) la matrice."""

    def get_permissions(self) -> list[Any]:
        action = ACTION_MODIFIER if self.request.method == "PUT" else ACTION_LIRE
        return [IsAuthenticated(), ADroit(MODULE_API, "droits", action)()]

    @extend_schema(responses={200: s.DroitAccordeSerializer(many=True), **ERREURS})
    def get(self, request: Request) -> Response:
        droits = DroitAccorde.objects.order_by("role_id", "permission_id")
        return Response(s.DroitAccordeSerializer(droits, many=True).data)

    @extend_schema(
        request=s.MatriceEntreeSerializer,
        responses={200: s.DroitAccordeSerializer(many=True), 409: s.ErreurSerializer, **ERREURS},
    )
    def put(self, request: Request) -> Response:
        entree = s.MatriceEntreeSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        lignes = [
            service_matrice.LigneDroit(
                code_role=ligne["role_id"],
                code_permission=ligne["permission_id"],
                portee=ligne["portee"],
            )
            for ligne in entree.validated_data["droits"]
        ]
        droits = service_matrice.remplacer(
            request.user, lignes, entree.validated_data.get("modules"), adresse_client(request)
        )
        return Response(s.DroitAccordeSerializer(droits, many=True).data)


# ---------------------------------------------------------------------------
# Appareils (EF-AUT-06, SQ-5 étapes 11-12)
# ---------------------------------------------------------------------------
class VueAppareils(APIView):
    """GET /api/appareils."""

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "appareils", ACTION_LIRE)]

    @extend_schema(responses={200: s.AppareilSerializer(many=True), **ERREURS})
    def get(self, request: Request) -> Response:
        return Response(s.AppareilSerializer(selecteur_appareils.lister(), many=True).data)


class VueRevocation(APIView):
    """POST /api/appareils/{id}/revocation — blocage immédiat et audit."""

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "appareils", ACTION_MODIFIER)]

    @extend_schema(
        request=None,
        responses={200: s.AppareilSerializer, 404: s.ErreurSerializer, **ERREURS},
    )
    def post(self, request: Request, id_appareil: str) -> Response:
        appareil = service_appareils.revoquer(request.user, id_appareil, adresse_client(request))
        return Response(s.AppareilSerializer(appareil).data)


# ---------------------------------------------------------------------------
# Journal d'audit (EF-AUT-08)
# ---------------------------------------------------------------------------
class VueAudit(APIView):
    """GET /api/audit?action=&auteur=&limite= — plus récentes d'abord."""

    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "audit", ACTION_LIRE)]

    @extend_schema(
        parameters=[
            OpenApiParameter("action", str, description="Action, en UPPER_SNAKE."),
            OpenApiParameter("auteur", str, description="Identifiant de l'auteur (uuid)."),
            OpenApiParameter("limite", int, description="Nombre maximal d'entrées (1 à 1000)."),
        ],
        responses={200: s.EntreeAuditSerializer(many=True), **ERREURS},
    )
    def get(self, request: Request) -> Response:
        filtre = s.FiltreAuditSerializer(data=request.query_params)
        filtre.is_valid(raise_exception=True)
        auteur = filtre.validated_data.get("auteur")
        entrees = selecteur_audit.lister(
            action=filtre.validated_data.get("action"),
            id_auteur=str(auteur) if auteur else None,
            limite=filtre.validated_data["limite"],
        )
        return Response(s.EntreeAuditSerializer(entrees, many=True).data)
