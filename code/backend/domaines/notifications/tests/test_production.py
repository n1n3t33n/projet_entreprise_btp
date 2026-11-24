"""Production des notifications à partir d'un événement publié (EF-NOT-01,
Q-AP, Q-AQ) : destinataires par rôle et périmètre, personne concernée,
avis unique, robustesse."""

import uuid
from typing import Any
from unittest import mock

import pytest

from domaines.identite.models import Perimetre
from domaines.notifications.models import Notification
from domaines.notifications.services import production
from socle.evenements import EvenementMetier, publier

pytestmark = pytest.mark.django_db


def _destinataires(code: str) -> set[Any]:
    return set(
        Notification.objects.filter(type_notification_id=code).values_list(
            "utilisateur_id", flat=True
        )
    )


def test_les_titulaires_dont_le_perimetre_couvre_le_lieu_sont_prevenus(
    fabrique_utilisateur: Any, magasin: Any, perimetre_chantier: Any
) -> None:
    autre = Perimetre.objects.create(
        libelle="Autre magasin",
        magasin=type(magasin).objects.create(code="M2", nom="Magasin 2", chantier=magasin.chantier),
    )
    au_magasin = fabrique_utilisateur(
        role="GESTIONNAIRE_STOCK",
        perimetre=Perimetre.objects.create(libelle="Magasin", magasin=magasin),
    )
    au_chantier = fabrique_utilisateur(role="GESTIONNAIRE_STOCK", perimetre=perimetre_chantier)
    partout = fabrique_utilisateur(role="GESTIONNAIRE_STOCK")
    ailleurs = fabrique_utilisateur(role="GESTIONNAIRE_STOCK", perimetre=autre)
    sans_role = fabrique_utilisateur(role="MAGASINIER")
    publier(
        EvenementMetier(
            code="STOCK_NEGATIF",
            id_chantier=magasin.chantier_id,
            id_magasin=magasin.pk,
            contexte={"message": "Ciment : stock négatif (-3)."},
        )
    )
    recus = _destinataires("STOCK_NEGATIF")
    assert {au_magasin.pk, au_chantier.pk, partout.pk} <= recus
    assert ailleurs.pk not in recus
    assert sans_role.pk not in recus
    assert Notification.objects.filter(message="Ciment : stock négatif (-3).").exists()


def test_l_auteur_n_est_pas_prevenu_de_sa_propre_action(fabrique_utilisateur: Any) -> None:
    chef = fabrique_utilisateur(role="CHEF_CHANTIER")
    collegue = fabrique_utilisateur(role="CHEF_CHANTIER")
    publier(EvenementMetier(code="ETAPE_BLOQUEE", auteur=chef, contexte={"etape": "Murs"}))
    assert _destinataires("ETAPE_BLOQUEE") == {collegue.pk}


def test_la_personne_concernee_est_seule_prevenue(fabrique_utilisateur: Any) -> None:
    technicien = fabrique_utilisateur(role="TECHNICIEN")
    fabrique_utilisateur(role="CHEF_CHANTIER")
    publier(
        EvenementMetier(
            code="ETAPE_REJETEE",
            personne=technicien,
            contexte={"etape": "Fondations", "logement": "A01", "motif": "Ferraillage."},
        )
    )
    notification = Notification.objects.get()
    assert notification.utilisateur_id == technicien.pk
    assert notification.message == (
        "Fondations du logement A01 a été rejetée au contrôle : Ferraillage."
    )


def test_un_avis_unique_n_est_produit_qu_une_fois(fabrique_utilisateur: Any) -> None:
    fabrique_utilisateur(role="CHEF_CHANTIER")
    evenement = EvenementMetier(code="ETAPE_EN_RETARD", id_objet=uuid.uuid4(), unique=True)
    publier(evenement)
    publier(evenement)
    assert Notification.objects.count() == 1


def test_un_champ_absent_reste_vide() -> None:
    assert production.rediger("{etape} du logement {logement}.", {"etape": "Murs"}) == (
        "Murs du logement ."
    )
    assert production.rediger("accolade {", {}) == "accolade {"


def test_un_evenement_sans_type_ne_produit_rien(fabrique_utilisateur: Any) -> None:
    fabrique_utilisateur(role="CHEF_CHANTIER")
    publier(EvenementMetier(code="INCONNU"))
    assert Notification.objects.count() == 0


def test_un_abonne_en_echec_ne_fait_pas_echouer_l_operation() -> None:
    with mock.patch.object(production, "produire", side_effect=RuntimeError("panne")):
        publier(EvenementMetier(code="ETAPE_BLOQUEE"))  # ne lève pas
