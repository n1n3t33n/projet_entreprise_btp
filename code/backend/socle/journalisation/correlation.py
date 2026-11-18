"""Identifiant de corrélation et journal de chaque requête (exigence 6.1).

Pour chaque requête : identifiant de corrélation, utilisateur, appareil,
route, méthode, code de retour et durée. On journalise le GABARIT de route
(« /api/appareils/<uuid>/revocation ») et non l'URL brute, et jamais le corps
de la requête ou de la réponse : c'est le premier niveau de la garantie
« aucun secret dans les journaux ».
"""

import logging
import time
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from socle import metriques
from socle.journalisation import contexte

journal = logging.getLogger("chantiersync.requetes")

EN_TETE_CORRELATION = "X-Request-ID"


def _identifiant_valide(valeur: str | None) -> str:
    """Reprend l'identifiant fourni par le client s'il s'agit d'un UUID,
    sinon en crée un : on n'injecte jamais un texte arbitraire dans les
    journaux."""
    if valeur:
        try:
            return str(uuid.UUID(valeur))
        except ValueError:
            pass
    return str(uuid.uuid4())


def _route(request: HttpRequest) -> str:
    correspondance = getattr(request, "resolver_match", None)
    if correspondance is not None and correspondance.route:
        return "/" + correspondance.route.lstrip("/")
    return "non résolue"


def _id_utilisateur(request: HttpRequest) -> str | None:
    utilisateur = getattr(request, "user", None)
    if utilisateur is not None and utilisateur.is_authenticated:
        return str(utilisateur.pk)
    return None


class MiddlewareCorrelation:
    """Premier middleware : pose l'identifiant de corrélation, mesure la
    durée et écrit une ligne de journal par requête."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        identifiant = _identifiant_valide(request.headers.get(EN_TETE_CORRELATION))
        jeton_contexte = contexte.id_correlation.set(identifiant)
        request.id_correlation = identifiant  # type: ignore[attr-defined]
        debut = time.perf_counter()
        try:
            reponse = self.get_response(request)
            reponse[EN_TETE_CORRELATION] = identifiant
            statut = reponse.status_code
            duree_ms = round((time.perf_counter() - debut) * 1000, 1)
            # Compteurs d'exploitation (6.6) et alerte sur rafale de 5xx (6.7).
            metriques.enregistrer_requete(statut, duree_ms)
            niveau = (
                logging.ERROR
                if statut >= 500
                else logging.WARNING if statut >= 400 else logging.INFO
            )
            journal.log(
                niveau,
                "requête traitée",
                extra={
                    "id_utilisateur": _id_utilisateur(request),
                    "id_appareil": getattr(request, "id_appareil_journal", None),
                    "route": _route(request),
                    "methode": request.method,
                    "statut": statut,
                    "duree_ms": duree_ms,
                },
            )
            return reponse
        finally:
            contexte.id_correlation.reset(jeton_contexte)
