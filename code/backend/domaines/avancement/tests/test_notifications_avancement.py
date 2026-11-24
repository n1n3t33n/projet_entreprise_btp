"""Événements de l'avancement qui deviennent des notifications (EF-NOT-01,
EF-AVA-09) : étape à contrôler, rejetée, bloquée faute de matériel, en
retard (une seule fois)."""

from collections.abc import Callable
from datetime import timedelta
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.avancement.models import EtapeTravaux
from domaines.avancement.services import fiches, retards
from domaines.identite.models import DroitAccorde
from domaines.notifications.models import Notification
from domaines.organisation.models import Logement
from domaines.referentiels.models import Article, UniteMesure

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def etapes(
    chantier_avancement: dict[str, Any], logement: Logement, fabrique_utilisateur: Any
) -> list[EtapeTravaux]:
    DroitAccorde.objects.create(
        role_id="TECHNICIEN", permission_id="api.etapes.modifier", portee="GLOBALE"
    )
    liste = list(EtapeTravaux.objects.filter(logement=logement).order_by("etape_modele__ordre"))
    fiches.affecter(
        fabrique_utilisateur(), [e.pk for e in liste], chantier_avancement["technicien"], None
    )
    return liste


def _types(utilisateur: Any) -> list[str]:
    return list(
        Notification.objects.filter(utilisateur=utilisateur).values_list(
            "type_notification_id", flat=True
        )
    )


def test_declaration_a_controler_puis_rejet(
    client_authentifie: Client,
    chantier_avancement: dict[str, Any],
    etapes: list[EtapeTravaux],
    fabrique_utilisateur: Any,
) -> None:
    chef = fabrique_utilisateur(role="CHEF_CHANTIER")
    technicien = chantier_avancement["technicien"]
    fondations = etapes[0]  # étape à contrôle
    client_authentifie(utilisateur=technicien).post(
        f"/api/etapes/{fondations.pk}/declaration", {}, format="json"
    )
    assert _types(chef) == ["ETAPE_A_CONTROLER"]
    client_authentifie().post(
        f"/api/etapes/{fondations.pk}/validation",
        {"decision": "REFUSE", "motif": "Ferraillage à reprendre."},
        format="json",
    )
    rejet = Notification.objects.get(type_notification_id="ETAPE_REJETEE")
    assert rejet.utilisateur_id == technicien.pk
    assert rejet.id_objet == fondations.pk
    assert "Fondations" in rejet.message and "Ferraillage" in rejet.message


def test_un_manque_de_materiel_previent_le_gestionnaire_de_stock(
    client_authentifie: Client,
    chantier_avancement: dict[str, Any],
    etapes: list[EtapeTravaux],
    fabrique_utilisateur: Any,
) -> None:
    gestionnaire = fabrique_utilisateur(role="GESTIONNAIRE_STOCK")
    chef = fabrique_utilisateur(role="CHEF_CHANTIER")
    sac = UniteMesure.objects.create(code_unite="SAC", libelle="sac", type_unite="MASSE")
    ciment = Article.objects.create(
        code="A1", designation="Ciment", origine="ACHAT", unite_mesure=sac
    )
    client_authentifie(utilisateur=chantier_avancement["technicien"]).post(
        f"/api/etapes/{etapes[1].pk}/blocage",
        {"code_motif": "MANQUE_MATERIEL", "article_id_article": str(ciment.pk)},
        format="json",
    )
    assert _types(gestionnaire) == ["MANQUE_MATERIEL"]
    assert "Ciment" in Notification.objects.get(utilisateur=gestionnaire).message
    assert _types(chef) == ["ETAPE_BLOQUEE"]


def test_une_etape_en_retard_n_est_signalee_qu_une_fois(
    etapes: list[EtapeTravaux], fabrique_utilisateur: Any
) -> None:
    chef = fabrique_utilisateur(role="CHEF_CHANTIER")
    EtapeTravaux.objects.filter(pk=etapes[2].pk).update(
        date_prevue=timezone.localdate() - timedelta(days=3)
    )
    assert retards.signaler() == "1 étape(s) en retard annoncée(s)."
    retards.signaler()
    assert _types(chef) == ["ETAPE_EN_RETARD"]
