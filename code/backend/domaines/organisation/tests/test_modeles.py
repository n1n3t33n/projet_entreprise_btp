"""Contraintes du MPD-2 sur chantier et magasin, vérifiées par la base."""

import pytest
from django.db import IntegrityError, transaction

from domaines.organisation.models import Chantier, Magasin

pytestmark = pytest.mark.django_db


def test_le_code_d_un_chantier_est_unique(chantier: Chantier) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Chantier.objects.create(code=chantier.code, nom="Doublon")


def test_un_statut_hors_liste_est_refuse_par_la_base() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Chantier.objects.create(code="CH-X", nom="X", statut="INVENTE")


def test_le_code_d_un_magasin_est_unique(magasin: Magasin) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Magasin.objects.create(code=magasin.code, nom="Doublon", chantier=magasin.chantier)


def test_un_chantier_portant_un_magasin_ne_se_supprime_pas(magasin: Magasin) -> None:
    from django.db.models import ProtectedError

    with pytest.raises(ProtectedError):
        magasin.chantier.delete()
