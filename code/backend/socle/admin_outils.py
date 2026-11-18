"""Outils communs de l'administration Django (exigence 6.10, arbitrage Q5).

L'accès à l'administration ne passe PAS par ``is_staff`` stocké en base : le
modèle utilisateur calcule ``is_staff`` et ``has_perm`` à partir de la
matrice des droits (permission « technique / admin »). Ce module ne fournit
que la forme « lecture seule », pour les modèles que l'admin peut montrer
mais jamais modifier (utilisateur, appareil, chantier, magasin) : toute
action sensible passe par l'API, qui l'inscrit au journal d'audit.
"""

from typing import Any

from django.contrib import admin
from django.http import HttpRequest


class AdminLectureSeule(admin.ModelAdmin):  # type: ignore[type-arg]
    """Modèle consultable dans l'admin, jamais créé, modifié ni supprimé."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False
