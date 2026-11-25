"""Réglages de la suite de tests (pytest-django).

La base de test « test_chantiersync » est créée et détruite à chaque
lancement : jamais une base contenant des données à préserver.

Pourquoi la connexion ``default`` utilise ici le rôle de MIGRATION : c'est la
connexion par laquelle pytest-django crée la base de test et y applique les
migrations ; elle doit donc agir sous le rôle propriétaire. Les tests
d'immuabilité repassent explicitement sous le rôle applicatif avec
« SET ROLE » pour prouver que les opérations interdites échouent (RG-S8).
"""

import secrets

from socle import environnement as env

from .base import *  # noqa: F403
from .base import DATABASES, LOGGING, REST_FRAMEWORK

# Clé aléatoire à chaque lancement si aucune n'est fournie : les tests ne
# doivent dépendre d'aucun secret réel.
SECRET_KEY = env.texte_facultatif("DJANGO_SECRET_KEY") or secrets.token_urlsafe(50)

DATABASES["default"] = {
    **DATABASES["migration"],
    "TEST": {"NAME": "test_chantiersync"},
}
DATABASES["migration"] = {**DATABASES["migration"], "TEST": {"MIRROR": "default"}}

# Hachage rapide : les tests créent beaucoup de comptes.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Taux connus et bas pour pouvoir tester la limitation (exigence 6.3).
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        "anonyme": "1000/min",
        "utilisateur": "1000/min",
        "connexion_ip": "1000/min",
        "connexion_identifiant": "5/min",
        "synchronisation": "1000/min",
    },
}

# Pas de manifeste des fichiers statiques en test (« collectstatic » n'est
# lancé qu'à la publication).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Cache en mémoire en test : la suite tourne dans un seul processus, et de
# nombreux tests n'ouvrent pas la base (le cache en base l'exigerait). La
# table du cache partagé est vérifiée par le test de schéma (django_cache).
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
ALLOWED_HOSTS = ["testserver", "localhost"]

# Les journaux restent émis (les tests de masquage les capturent).
LOGGING["root"]["level"] = "INFO"  # type: ignore[index]
