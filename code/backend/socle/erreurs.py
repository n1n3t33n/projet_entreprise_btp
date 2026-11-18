"""Format d'erreur unique de l'API et gestionnaire d'exceptions DRF.

Toute erreur renvoyée par l'API a la même forme, celle que les deux fronts
lisent déjà pour la connexion (rapport B0 § 3.1) :

    { "motif": "UPPER_SNAKE", "message": "phrase en français",
      "details": {...}?, "secondes_restantes": n?, "id_correlation": "..."? }

``motif`` est un code stable destiné au programme client ; ``message`` est
destiné à l'utilisateur : il ne contient JAMAIS de code interne, de nom de
table ou de référence de modélisation (charte § 8, défaut I-03 à ne pas
reproduire).
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from django.http import Http404, HttpRequest, JsonResponse
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import set_rollback

from socle.journalisation import contexte

journal = logging.getLogger("chantiersync.erreurs")

# Messages par défaut, rédigés pour l'utilisateur final.
MESSAGES = {
    "DONNEES_INVALIDES": "Certaines informations sont manquantes ou incorrectes.",
    "NON_AUTHENTIFIE": "Connectez-vous pour continuer.",
    "JETON_INVALIDE": "Votre session n'est plus valide. Connectez-vous à nouveau.",
    "ACCES_REFUSE": "Vous n'avez pas les droits nécessaires pour cette action.",
    "INTROUVABLE": "L'élément demandé est introuvable.",
    "METHODE_NON_AUTORISEE": "Cette opération n'est pas possible ici.",
    "TROP_DE_REQUETES": "Trop de demandes en peu de temps. Patientez un instant.",
    "FORMAT_NON_PRIS_EN_CHARGE": "Le format des données envoyées n'est pas accepté.",
    "ERREUR_INTERNE": (
        "Une erreur inattendue est survenue. Réessayez ; si le problème persiste, "
        "communiquez le numéro de suivi au support."
    ),
}


@dataclass
class ErreurApi(Exception):  # noqa: N818 - nom métier volontairement français
    """Erreur métier levée par un service, traduite telle quelle en réponse.

    Les services lèvent cette exception plutôt que de fabriquer des réponses
    HTTP : la logique reste hors des vues (règle Django du projet).
    """

    statut: int
    motif: str
    message: str
    details: dict[str, Any] | None = None
    secondes_restantes: int | None = None
    en_tetes: dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.motif


def corps_erreur(
    motif: str,
    message: str | None = None,
    details: dict[str, Any] | None = None,
    secondes_restantes: int | None = None,
) -> dict[str, Any]:
    """Construit le corps JSON d'une erreur au format unique."""
    corps: dict[str, Any] = {"motif": motif, "message": message or MESSAGES[motif]}
    if details:
        corps["details"] = details
    if secondes_restantes is not None:
        corps["secondes_restantes"] = secondes_restantes
    return corps


def _reponse(
    statut: int, corps: dict[str, Any], en_tetes: dict[str, str] | None = None
) -> Response:
    reponse = Response(corps, status=statut)
    for nom, valeur in (en_tetes or {}).items():
        reponse[nom] = valeur
    return reponse


def gestionnaire_exceptions(exc: Exception, context: dict[str, Any]) -> Response:
    """Traduit toute exception levée par une vue DRF au format unique."""
    set_rollback()
    en_tete_auth = getattr(exc, "auth_header", None)
    en_tetes = {"WWW-Authenticate": en_tete_auth} if en_tete_auth else {}

    if isinstance(exc, ErreurApi):
        corps = corps_erreur(exc.motif, exc.message, exc.details, exc.secondes_restantes)
        return _reponse(exc.statut, corps, {**en_tetes, **exc.en_tetes})
    if isinstance(exc, exceptions.ValidationError):
        details = exc.detail if isinstance(exc.detail, dict) else {"non_field_errors": exc.detail}
        return _reponse(
            status.HTTP_400_BAD_REQUEST, corps_erreur("DONNEES_INVALIDES", details=details)
        )
    if isinstance(exc, exceptions.NotAuthenticated):
        return _reponse(status.HTTP_401_UNAUTHORIZED, corps_erreur("NON_AUTHENTIFIE"), en_tetes)
    if isinstance(exc, exceptions.AuthenticationFailed):
        # L'authentification place son motif précis (JETON_EXPIRE,
        # APPAREIL_REVOQUE…) dans le code de l'exception : le mobile en a
        # besoin pour savoir s'il doit effacer ses données (SQ-5 étape 15).
        code = exc.get_codes()
        if isinstance(code, str) and code != "authentication_failed":
            corps = corps_erreur(code, str(exc.detail))
        else:
            corps = corps_erreur("JETON_INVALIDE")
        return _reponse(status.HTTP_401_UNAUTHORIZED, corps, en_tetes)
    if isinstance(exc, exceptions.PermissionDenied):
        return _reponse(status.HTTP_403_FORBIDDEN, corps_erreur("ACCES_REFUSE"))
    if isinstance(exc, exceptions.NotFound | Http404):
        return _reponse(status.HTTP_404_NOT_FOUND, corps_erreur("INTROUVABLE"))
    if isinstance(exc, exceptions.MethodNotAllowed):
        return _reponse(status.HTTP_405_METHOD_NOT_ALLOWED, corps_erreur("METHODE_NON_AUTORISEE"))
    if isinstance(exc, exceptions.UnsupportedMediaType | exceptions.ParseError):
        return _reponse(status.HTTP_400_BAD_REQUEST, corps_erreur("FORMAT_NON_PRIS_EN_CHARGE"))
    if isinstance(exc, exceptions.Throttled):
        # DRF pose « wait » à l'exécution ; les stubs de typage l'ignorent.
        attente = int(getattr(exc, "wait", None) or 1)
        return _reponse(
            status.HTTP_429_TOO_MANY_REQUESTS,
            corps_erreur("TROP_DE_REQUETES", secondes_restantes=attente),
            {"Retry-After": str(attente)},
        )
    if isinstance(exc, exceptions.APIException):
        return _reponse(exc.status_code, corps_erreur("DONNEES_INVALIDES"))

    # Toute autre exception : trace complète dans le journal (6.1), réponse
    # neutre au client avec un numéro de suivi, aucun détail interne.
    journal.exception("erreur inattendue pendant le traitement d'une requête")
    corps = corps_erreur("ERREUR_INTERNE")
    corps["id_correlation"] = contexte.id_correlation.get()
    return _reponse(status.HTTP_500_INTERNAL_SERVER_ERROR, corps)


def page_introuvable(request: HttpRequest, exception: Exception) -> JsonResponse:
    """404 hors des vues DRF (adresse inconnue) : même format JSON."""
    return JsonResponse(corps_erreur("INTROUVABLE"), status=404)


def erreur_serveur(request: HttpRequest) -> JsonResponse:
    """500 hors des vues DRF : même format, avec le numéro de suivi."""
    corps = corps_erreur("ERREUR_INTERNE")
    corps["id_correlation"] = contexte.id_correlation.get()
    return JsonResponse(corps, status=500)
