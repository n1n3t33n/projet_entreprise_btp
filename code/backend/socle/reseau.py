"""Adresse réseau du client, pour le journal d'audit (MPD-1 ``adresse_ip``).

Derrière la plateforme d'hébergement, l'adresse réelle arrive dans
``X-Forwarded-For`` ; on ne la croit que si des mandataires de confiance sont
déclarés (``NOMBRE_MANDATAIRES``), sinon n'importe quel client pourrait
inscrire l'adresse de son choix au journal d'audit.
"""

from django.conf import settings
from django.http import HttpRequest


def adresse_client(request: HttpRequest) -> str | None:
    """Rend l'adresse IP du client, ou ``None`` si elle est inconnue."""
    valeur = settings.REST_FRAMEWORK.get("NUM_PROXIES")
    mandataires = valeur if isinstance(valeur, int) else 0
    transmise = request.META.get("HTTP_X_FORWARDED_FOR")
    if mandataires and transmise:
        adresses = [adresse.strip() for adresse in transmise.split(",") if adresse.strip()]
        if adresses:
            return adresses[-min(mandataires, len(adresses))][:120]
    adresse = request.META.get("REMOTE_ADDR")
    return adresse[:120] if adresse else None
