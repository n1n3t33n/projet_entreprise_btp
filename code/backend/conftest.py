"""Fixtures partagées de la suite pytest-django.

La base de test « test_chantiersync » est créée par pytest-django sous le rôle
propriétaire (réglages de test) et reçoit TOUTES les migrations, y compris les
fonctions SQL, les déclencheurs et le référentiel initial des rôles et
permissions (identite 0004). Chaque test tourne dans une transaction annulée
à la fin : aucune donnée ne survit d'un test à l'autre.

Remarque : un test « transactionnel » (transaction=True) viderait les tables
par TRUNCATE et échouerait volontairement sur le journal d'audit immuable.
On ne l'utilise donc pas.
"""

from collections.abc import Callable, Iterator
from typing import Any

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

MOT_DE_PASSE_TEST = "Chantier-Test-2026!"


@pytest.fixture(autouse=True)
def _vider_cache() -> Iterator[None]:
    """Les compteurs de limitation du taux et l'anti-répétition des alertes
    vivent dans le cache local, les métriques en mémoire : on repart de zéro
    à chaque test."""
    from socle.metriques import COMPTEURS

    cache.clear()
    COMPTEURS.reinitialiser()
    yield
    cache.clear()
    COMPTEURS.reinitialiser()


@pytest.fixture
def chantier(db: Any) -> Any:
    from domaines.organisation.models import Chantier

    return Chantier.objects.create(code="CH-TEST", nom="Chantier de test")


@pytest.fixture
def magasin(chantier: Any) -> Any:
    from domaines.organisation.models import Magasin

    return Magasin.objects.create(code="MAG-TEST", nom="Magasin de test", chantier=chantier)


@pytest.fixture
def perimetre_global(db: Any) -> Any:
    from domaines.identite.models import Perimetre

    return Perimetre.objects.create(libelle="Tout le programme")


@pytest.fixture
def perimetre_chantier(chantier: Any) -> Any:
    from domaines.identite.models import Perimetre

    return Perimetre.objects.create(libelle="Chantier de test", chantier=chantier)


@pytest.fixture
def fabrique_utilisateur(perimetre_global: Any) -> Callable[..., Any]:
    """Crée un compte actif avec un rôle sur un périmètre."""
    from domaines.identite.models import AffectationRole, Utilisateur

    compteur = {"n": 0}

    def fabriquer(
        role: str = "ADMINISTRATEUR",
        perimetre: Any = None,
        identifiant: str | None = None,
        statut: str = "ACTIF",
        **champs: Any,
    ) -> Any:
        compteur["n"] += 1
        utilisateur = Utilisateur.objects.create_user(
            identifiant=identifiant or f"compte.{compteur['n']}",
            password=MOT_DE_PASSE_TEST,
            nom=champs.pop("nom", "Testeur"),
            prenom=champs.pop("prenom", f"Personne{compteur['n']}"),
            statut=statut,
            **champs,
        )
        if role:
            AffectationRole.objects.create(
                role_id=role, perimetre=perimetre or perimetre_global, utilisateur=utilisateur
            )
        return utilisateur

    return fabriquer


@pytest.fixture
def client_api() -> APIClient:
    return APIClient()


@pytest.fixture
def client_authentifie(fabrique_utilisateur: Callable[..., Any]) -> Callable[..., APIClient]:
    """Client porteur d'un jeton valide pour un compte du rôle demandé."""
    from domaines.identite.authentification import emettre_jeton

    def construire(role: str = "ADMINISTRATEUR", appareil: Any = None, **champs: Any) -> APIClient:
        utilisateur = champs.pop("utilisateur", None) or fabrique_utilisateur(role=role, **champs)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {emettre_jeton(utilisateur, appareil)}")
        client.utilisateur = utilisateur  # type: ignore[attr-defined]
        return client

    return construire


@pytest.fixture
def fabrique_appareil(fabrique_utilisateur: Callable[..., Any]) -> Callable[..., Any]:
    """Enrôle un appareil (jeton mobile) pour un compte donné ou neuf."""
    from domaines.identite.models import Appareil

    compteur = {"n": 0}

    def fabriquer(utilisateur: Any = None, role: str = "ADMINISTRATEUR") -> Any:
        compteur["n"] += 1
        return Appareil.objects.create(
            empreinte_materiel=f"empreinte-{compteur['n']}",
            plateforme="android",
            version_application="1.0.0",
            utilisateur=utilisateur or fabrique_utilisateur(role=role),
        )

    return fabriquer


@pytest.fixture
def client_mobile(
    client_authentifie: Callable[..., APIClient], fabrique_appareil: Callable[..., Any]
) -> Callable[..., APIClient]:
    """Client porteur d'un jeton mobile lié à un appareil enrôlé
    (``client.appareil``)."""

    def construire(utilisateur: Any = None, role: str = "ADMINISTRATEUR") -> APIClient:
        appareil = fabrique_appareil(utilisateur, role)
        client = client_authentifie(utilisateur=appareil.utilisateur, appareil=appareil)
        client.appareil = appareil  # type: ignore[attr-defined]
        return client

    return construire
