"""Fixtures du domaine synchronisation : un appareil enrôlé et son jeton."""

from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.identite.models import Appareil


@pytest.fixture
def fabrique_appareil(fabrique_utilisateur: Any) -> Callable[..., Appareil]:
    compteur = {"n": 0}

    def fabriquer(utilisateur: Any = None, role: str = "ADMINISTRATEUR") -> Appareil:
        compteur["n"] += 1
        return Appareil.objects.create(
            empreinte_materiel=f"empreinte-{compteur['n']}",
            plateforme="android",
            version_application="1.0.0",
            utilisateur=utilisateur or fabrique_utilisateur(role=role),
        )

    return fabriquer


@pytest.fixture
def client_mobile(client_authentifie: Any, fabrique_appareil: Any) -> Callable[..., APIClient]:
    """Client porteur d'un jeton mobile (lié à un appareil enrôlé)."""

    def construire(utilisateur: Any = None, role: str = "ADMINISTRATEUR") -> APIClient:
        appareil = fabrique_appareil(utilisateur, role)
        client = client_authentifie(utilisateur=appareil.utilisateur, appareil=appareil)
        client.appareil = appareil  # type: ignore[attr-defined]
        return client

    return construire
