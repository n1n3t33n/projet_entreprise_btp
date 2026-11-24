"""Événements du stock qui deviennent des notifications (EF-NOT-01) : sortie
à valider, sortie refusée, stock négatif."""

from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.notifications.models import Notification
from domaines.stock.tests.outils import corps_mouvement, corps_sortie

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


def test_une_sortie_a_valider_previent_le_gestionnaire(
    client_authentifie: Client, chantier_stock: dict[str, Any], fabrique_utilisateur: Any
) -> None:
    gestionnaire = fabrique_utilisateur(role="GESTIONNAIRE_STOCK")
    auteur = client_authentifie()
    auteur.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "500"), format="json"
    )
    sortie = auteur.post(
        "/api/mouvements", corps_sortie(chantier_stock, "150"), format="json"
    ).json()
    notification = Notification.objects.get(type_notification_id="SORTIE_A_VALIDER")
    assert notification.utilisateur_id == gestionnaire.pk
    assert str(notification.id_objet) == sortie["uuid"]
    assert "Ciment" in notification.message and "150" in notification.message


def test_une_sortie_refusee_previent_celui_qui_l_a_saisie(
    client_authentifie: Client, chantier_stock: dict[str, Any]
) -> None:
    auteur = client_authentifie()
    auteur.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "500"), format="json"
    )
    sortie = auteur.post(
        "/api/mouvements", corps_sortie(chantier_stock, "150"), format="json"
    ).json()
    client_authentifie().post(
        f"/api/mouvements/{sortie['uuid']}/validation",
        {"decision": "REFUSE", "motif": "Quantité excessive."},
        format="json",
    )
    refus = Notification.objects.get(type_notification_id="SORTIE_REFUSEE")
    assert refus.utilisateur_id == auteur.utilisateur.pk  # type: ignore[attr-defined]
    assert refus.message.endswith("Quantité excessive.")


def test_un_stock_negatif_previent_par_son_alerte(
    client_authentifie: Client, chantier_stock: dict[str, Any], fabrique_utilisateur: Any
) -> None:
    gestionnaire = fabrique_utilisateur(role="GESTIONNAIRE_STOCK")
    client_authentifie().post(
        "/api/mouvements",
        corps_mouvement(chantier_stock, "SOR_PERTE", "3", motif="Casse"),
        format="json",
    )
    notification = Notification.objects.get(
        type_notification_id="STOCK_NEGATIF", utilisateur=gestionnaire
    )
    assert notification.alerte is not None
    assert notification.alerte.type_alerte == "STOCK_NEGATIF"
