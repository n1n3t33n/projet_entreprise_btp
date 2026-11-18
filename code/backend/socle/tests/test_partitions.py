"""Calendrier des partitions mensuelles (rapport B0 § 4.5)."""

from datetime import date

from socle.base_de_donnees.partitions import ajouter_mois, mois_a_couvrir


def test_ajouter_mois_passe_l_annee() -> None:
    assert ajouter_mois(date(2026, 11, 18), 3) == date(2027, 2, 1)
    assert ajouter_mois(date(2026, 1, 31), -1) == date(2025, 12, 1)


def test_mois_a_couvrir_un_passe_le_courant_et_l_avance() -> None:
    mois = mois_a_couvrir(date(2026, 11, 18), mois_avance=3)
    assert mois == [
        date(2026, 10, 1),
        date(2026, 11, 1),
        date(2026, 12, 1),
        date(2027, 1, 1),
        date(2027, 2, 1),
    ]
