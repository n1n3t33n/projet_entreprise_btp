"""Contexte de la requête en cours, porté par des ``contextvars``.

Pourquoi des contextvars et non des variables globales de thread : la base
doit rester compatible ASGI (arbitrage Q3). Un contextvar suit la requête
même lorsqu'elle passe d'un thread à une coroutine.
"""

from contextvars import ContextVar

# Identifiant de corrélation de la requête (en-tête X-Request-ID).
id_correlation: ContextVar[str | None] = ContextVar("id_correlation", default=None)
