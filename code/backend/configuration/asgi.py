"""Point d'entrée ASGI.

Maintenu dès B1 (arbitrage Q3, option 3) pour que le passage éventuel au
temps réel en B6 ne demande pas de refonte : le code n'utilise que des
``contextvars`` (jamais de variable globale de thread) et aucun appel
bloquant caché. Aucun WebSocket n'est servi en B1.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configuration.reglages.production")

application = get_asgi_application()
