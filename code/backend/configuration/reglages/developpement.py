"""Réglages du poste de développement (Windows, PostgreSQL 16 local)."""

from .base import *  # noqa: F403

DEBUG = True

# Les alertes techniques s'affichent dans la console au lieu de partir par SMTP.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
