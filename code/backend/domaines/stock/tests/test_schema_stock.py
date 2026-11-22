"""MPD-4 en base : journaux immuables (RG-S8) et contraintes du stock.

Comme pour le journal d'audit (identite/tests/test_immuabilite.py), deux
protections indépendantes sont prouvées sur la vraie base PostgreSQL :
  1. droits : sous le rôle applicatif, UPDATE, DELETE et TRUNCATE sont
     refusés sur ``mouvement_stock`` et ``evenement_validation`` (parent et
     partition), alors qu'INSERT réussit ;
  2. déclencheurs : même le propriétaire se voit refuser ces opérations.
"""

from collections.abc import Iterator
from decimal import Decimal
from typing import Any

import pytest
from django.conf import settings
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.utils import timezone

from domaines.stock.models import EvenementValidation, MouvementStock, SeuilStock

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def evenement(mouvement: MouvementStock, fabrique_utilisateur: Any) -> EvenementValidation:
    return EvenementValidation.objects.create(
        type_objet="mouvement_stock",
        decision="ACCEPTE",
        mouvement_stock=mouvement,
        utilisateur=fabrique_utilisateur(role="GESTIONNAIRE_STOCK"),
    )


@pytest.fixture
def role_applicatif() -> Iterator[None]:
    with connection.cursor() as curseur:
        curseur.execute(f'SET ROLE "{settings.BD_ROLE_APPLICATION}"')
    try:
        yield
    finally:
        with connection.cursor() as curseur:
            curseur.execute("RESET ROLE")


def _doit_echouer(sql: str, parametres: list[Any] | None = None) -> None:
    with pytest.raises(DatabaseError), transaction.atomic(), connection.cursor() as curseur:
        curseur.execute(sql, parametres)


def _partition() -> str:
    return "evenement_validation_" + timezone.now().strftime("%Y_%m")


# --- Immuabilité ---------------------------------------------------------------
@pytest.mark.parametrize("table", ["mouvement_stock", "evenement_validation", "partition"])
def test_le_role_applicatif_ne_peut_ni_modifier_ni_supprimer_ni_vider(
    evenement: EvenementValidation, role_applicatif: None, table: str
) -> None:
    nom = _partition() if table == "partition" else table
    colonne = "quantite_base = 1" if table == "mouvement_stock" else "motif = 'x'"
    _doit_echouer(f"UPDATE {nom} SET {colonne}")
    _doit_echouer(f"DELETE FROM {nom}")
    _doit_echouer(f"TRUNCATE {nom}")


@pytest.mark.parametrize("table", ["mouvement_stock", "evenement_validation"])
def test_meme_le_proprietaire_est_arrete_par_les_declencheurs(
    evenement: EvenementValidation, table: str
) -> None:
    colonne = "quantite_base = 1" if table == "mouvement_stock" else "motif = 'x'"
    _doit_echouer(f"UPDATE {table} SET {colonne}")
    _doit_echouer(f"DELETE FROM {table}")


def test_le_role_applicatif_peut_inscrire_un_evenement(
    mouvement: MouvementStock, fabrique_utilisateur: Any, role_applicatif: None
) -> None:
    valideur = fabrique_utilisateur(role="GESTIONNAIRE_STOCK")
    with connection.cursor() as curseur:
        curseur.execute(
            "INSERT INTO evenement_validation (uuid, type_objet, decision, horodatage_serveur, "
            "mouvement_stock_uuid, utilisateur_id_utilisateur) "
            "VALUES (gen_random_uuid(), 'mouvement_stock', 'REFUSE', now(), %s, %s)",
            [mouvement.pk, valideur.pk],
        )
    assert EvenementValidation.objects.filter(decision="REFUSE").count() == 1


def test_un_evenement_tombe_dans_la_partition_du_mois(evenement: EvenementValidation) -> None:
    with connection.cursor() as curseur:
        curseur.execute(f"SELECT count(*) FROM {_partition()}")  # noqa: S608
        assert curseur.fetchone()[0] == 1


# --- Contraintes ------------------------------------------------------------------
def _copie(mouvement: MouvementStock, **champs: Any) -> MouvementStock:
    valeurs: dict[str, Any] = {
        "quantite_saisie": Decimal("1"),
        "quantite_base": Decimal("1"),
        "type_mouvement": mouvement.type_mouvement,
        "article": mouvement.article,
        "magasin": mouvement.magasin,
        "utilisateur": mouvement.utilisateur,
        "stock_courant": mouvement.stock_courant,
        "unite_mesure": mouvement.unite_mesure,
        **champs,
    }
    return MouvementStock.objects.create(**valeurs)


def test_une_quantite_nulle_est_refusee_par_la_base(mouvement: MouvementStock) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        _copie(mouvement, quantite_saisie=Decimal("0"), quantite_base=Decimal("0"))


def test_un_statut_de_validation_hors_liste_est_refuse(mouvement: MouvementStock) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        _copie(mouvement, statut_validation="VALIDE")


def test_un_seul_seuil_par_article_et_par_magasin(mouvement: MouvementStock) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        SeuilStock.objects.create(magasin=mouvement.magasin, article=mouvement.article)


def test_un_mouvement_ne_s_annule_qu_une_fois(mouvement: MouvementStock) -> None:
    _copie(mouvement, motif="erreur de saisie", mouvement_annule=mouvement)
    with pytest.raises(IntegrityError), transaction.atomic():
        _copie(mouvement, motif="erreur de saisie", mouvement_annule=mouvement)
