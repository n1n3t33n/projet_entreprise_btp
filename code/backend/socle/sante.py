"""Points d'entrée de santé (exigence 6.2 du rapport B0).

- ``GET /api/sante/vivacite`` : le service répond (aucun accès à la base).
- ``GET /api/sante/aptitude`` : la base est joignable ET toutes les
  migrations sont appliquées.

Sans authentification, pour que la plateforme d'hébergement puisse les
interroger ; mais la réponse ne divulgue rien de l'infrastructure : ni
version, ni nom d'hôte, ni message d'erreur, seulement OK / KO.
"""

import logging

from django.db import DatabaseError, connection
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

journal = logging.getLogger("chantiersync.sante")

OK = "OK"
KO = "KO"
EN_RETARD = "EN_RETARD"


def verifier_base() -> str:
    """Interroge la base par une requête triviale."""
    try:
        with connection.cursor() as curseur:
            curseur.execute("SELECT 1")
            curseur.fetchone()
    except DatabaseError:
        journal.exception("base de données injoignable")
        return KO
    return OK


def verifier_migrations() -> str:
    """Vérifie qu'aucune migration n'attend d'être appliquée."""
    try:
        executeur = MigrationExecutor(connection)
        plan = executeur.migration_plan(executeur.loader.graph.leaf_nodes())
    except DatabaseError:
        journal.exception("état des migrations illisible")
        return KO
    return OK if not plan else EN_RETARD


@require_GET
def vivacite(request: HttpRequest) -> JsonResponse:
    """Le processus répond : rien d'autre n'est vérifié."""
    return JsonResponse({"statut": OK})


@require_GET
def aptitude(request: HttpRequest) -> JsonResponse:
    """Le service peut traiter des requêtes : base joignable, schéma à jour."""
    base = verifier_base()
    migrations = verifier_migrations() if base == OK else KO
    apte = base == OK and migrations == OK
    corps = {
        "statut": OK if apte else "INDISPONIBLE",
        "verifications": {"base_de_donnees": base, "migrations": migrations},
    }
    return JsonResponse(corps, status=200 if apte else 503)
