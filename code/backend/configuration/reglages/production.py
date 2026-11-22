"""Réglages de production (PaaS, puis éventuellement VPS ou serveurs de
l'entreprise). Tout vient de l'environnement ; DEBUG reste faux.

Étapes de publication à déclarer sur la plateforme (arbitrage Q6) :
  1. python manage.py collectstatic --noinput
  2. python manage.py migrate --database migration
  3. python manage.py creer_partitions
Tâches planifiées (chaque passage est tracé dans execution_traitement, 6.5) :
  * chaque jour : python manage.py lancer_traitement creer_partitions
  * chaque jour : python manage.py lancer_traitement cycler_fiches_route
  * chaque nuit : python manage.py lancer_traitement consolider_avancement
  * chaque heure : python manage.py lancer_traitement relancer_validations
"""

from socle import environnement as env

from .base import *  # noqa: F403
from .base import RACINE

DEBUG = False

# Dossier rempli par « collectstatic » à la publication (déjà ignoré par git :
# code/.gitignore, « /backend/staticfiles/ »).
STATIC_ROOT = RACINE / "staticfiles"
WHITENOISE_USE_FINDERS = False

# HTTPS imposé ; la plateforme termine TLS devant l'application.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.booleen("DJANGO_REDIRECTION_HTTPS", True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.entier("DJANGO_HSTS_SECONDES", 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
CSRF_TRUSTED_ORIGINS = env.liste("DJANGO_ORIGINES_CSRF")
