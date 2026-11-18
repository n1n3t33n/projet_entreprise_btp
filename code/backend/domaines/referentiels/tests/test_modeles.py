"""Contraintes du MPD-2 et du MPD-3 vérifiées par la base (énumérés arbitrés
le 2026-11-18, Q-A ; écart Q-D)."""

from collections.abc import Callable
from decimal import Decimal
from typing import Any

import pytest
from django.db import IntegrityError, transaction

from domaines.organisation.models import Chantier, Logement, ParametreChantier, TypeLogement, Zone
from domaines.referentiels.models import Article, Gamme, RegleValidation, UniteMesure

pytestmark = pytest.mark.django_db


def _echoue(fabrique: Callable[[], Any]) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        fabrique()


def test_statut_du_chantier_ne_connait_plus_ouvert() -> None:
    _echoue(lambda: Chantier.objects.create(code="CH-O", nom="X", statut="OUVERT"))


def test_cycle_de_vie_du_logement(chantier: Chantier) -> None:
    zone = Zone.objects.create(code="Z1", nom="Îlot 1", type_zone="TRANCHE", chantier=chantier)
    villa = TypeLogement.objects.create(code_type="VILLA", libelle="Villa")
    logement = Logement.objects.create(numero="A01", zone=zone, type_logement=villa)
    assert logement.statut == "A_VENIR"
    _echoue(
        lambda: Logement.objects.create(
            numero="A02", zone=zone, type_logement=villa, statut="ACTIF"
        )
    )


def test_type_de_zone_contraint(chantier: Chantier) -> None:
    _echoue(lambda: Zone.objects.create(code="Z9", nom="X", type_zone="ETAGE", chantier=chantier))


def test_parametre_accepte_texte_et_libelle(chantier: Chantier) -> None:
    parametre = ParametreChantier.objects.create(
        chantier=chantier, cle="devise", valeur="XOF", type_valeur="TEXTE", libelle="Devise"
    )
    assert parametre.libelle == "Devise"
    _echoue(
        lambda: ParametreChantier.objects.create(
            chantier=chantier, cle="x", valeur="1", type_valeur="LISTE"
        )
    )


def test_unites_cinq_types() -> None:
    UniteMesure.objects.create(code_unite="M2", libelle="Mètre carré", type_unite="SURFACE")
    _echoue(lambda: UniteMesure.objects.create(code_unite="H", libelle="Heure", type_unite="TEMPS"))


def test_article_code_barre_unique_mais_facultatif() -> None:
    sac = UniteMesure.objects.create(code_unite="SAC", libelle="Sac", type_unite="UNITE")
    Article.objects.create(code="A1", designation="Ciment", origine="ACHAT", unite_mesure=sac)
    Article.objects.create(code="A2", designation="Sable", origine="ACHAT", unite_mesure=sac)
    Article.objects.create(
        code="A3", designation="Fer", origine="ACHAT", unite_mesure=sac, code_barre="123"
    )
    _echoue(
        lambda: Article.objects.create(
            code="A4", designation="Fer 2", origine="ACHAT", unite_mesure=sac, code_barre="123"
        )
    )
    _echoue(
        lambda: Article.objects.create(
            code="A5", designation="X", origine="IMPORT", unite_mesure=sac
        )
    )


def test_statut_de_gamme_contraint() -> None:
    villa = TypeLogement.objects.create(code_type="VILLA", libelle="Villa")
    _echoue(
        lambda: Gamme.objects.create(version=1, libelle="G", statut="PUBLIEE", type_logement=villa)
    )


def test_regle_de_validation_sans_contrainte_en_base() -> None:
    """Le MPD laisse type_evenement et operateur libres : la base accepte,
    c'est l'API qui contrôle (constantes.py)."""
    regle = RegleValidation.objects.create(
        type_evenement="AUTRE", champ_teste="x", operateur="CONTIENT", valeur_seuil=Decimal("1")
    )
    assert regle.pk
