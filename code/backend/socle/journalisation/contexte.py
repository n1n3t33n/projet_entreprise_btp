"""Contexte de la requête en cours, porté par des ``contextvars``.

Pourquoi des contextvars et non des variables globales de thread : la base
doit rester compatible ASGI (arbitrage Q3). Un contextvar suit la requête
même lorsqu'elle passe d'un thread à une coroutine.
"""

from contextvars import ContextVar

# Identifiant de corrélation de la requête (en-tête X-Request-ID).
id_correlation: ContextVar[str | None] = ContextVar("id_correlation", default=None)

# Appareil de la requête et version de son application, posés par
# l'authentification d'un jeton mobile ; vides pour le web. Ils sont recopiés
# dans les journaux immuables (traçabilité du cahier des charges, Q-BD).
appareil: ContextVar[tuple[str, str] | None] = ContextVar("appareil", default=None)


def champs_appareil() -> dict[str, str]:
    """Champs à écrire dans un journal : ``appareil_id`` et
    ``version_application`` de la requête mobile, ou rien."""
    courant = appareil.get()
    if courant is None:
        return {}
    return {"appareil_id": courant[0], "version_application": courant[1]}
