"""Composition sûre d'ordres SQL contenant des noms de rôles ou de tables.

Les noms de rôles viennent des réglages (BD_ROLE_APPLICATION…), jamais écrits
en dur dans une migration. Un nom ne peut pas être passé comme paramètre SQL :
on le cite donc avec ``psycopg.sql.Identifier``, ce qui interdit toute
injection même si la variable d'environnement était malveillante.
"""

from typing import Any

from django.conf import settings
from psycopg import sql


def role_application() -> sql.Identifier:
    """Rôle d'exécution de Django (non propriétaire des tables)."""
    return sql.Identifier(settings.BD_ROLE_APPLICATION)


def role_proprietaire() -> sql.Identifier:
    """Rôle propriétaire du schéma et des tables."""
    return sql.Identifier(settings.BD_ROLE_PROPRIETAIRE)


def executer(schema_editor: Any, requete: sql.Composable) -> None:
    """Exécute un ordre composé sur la connexion de la migration en cours.

    L'ordre est rendu en texte avec la connexion psycopg réelle (citation
    exacte des identifiants), puis exécuté sans paramètres : les « % » des
    corps de fonctions PL/pgSQL ne sont donc jamais pris pour des marqueurs.
    """
    connexion_brute = schema_editor.connection.connection
    schema_editor.execute(requete.as_string(connexion_brute), params=None)
