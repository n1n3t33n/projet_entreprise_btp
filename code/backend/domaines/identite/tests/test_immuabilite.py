"""RG-S8 : le journal d'audit est RÉELLEMENT immuable (arbitrage Q4).

Deux protections indépendantes sont prouvées, sur la vraie base PostgreSQL :
  1. droits : sous le rôle applicatif (SET ROLE), UPDATE, DELETE et TRUNCATE
     sont refusés, sur la table parente ET sur une partition, alors
     qu'INSERT réussit ;
  2. déclencheurs : même le propriétaire, qui a tous les droits, se voit
     refuser UPDATE, DELETE et TRUNCATE (parent et partition).
Chaque opération interdite est tentée dans un point de sauvegarde, annulé
après l'échec attendu.
"""

import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from domaines.identite.models import JournalAudit

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _partition_courante() -> str:
    return "journal_audit_" + timezone.now().strftime("%Y_%m")


@pytest.fixture
def entree(fabrique_utilisateur) -> JournalAudit:  # type: ignore[no-untyped-def]
    utilisateur = fabrique_utilisateur()
    return JournalAudit.objects.create(
        action="CONNEXION", type_objet="utilisateur", utilisateur=utilisateur
    )


@pytest.fixture
def role_applicatif() -> Iterator[None]:
    """Passe la connexion sous le rôle applicatif le temps du test."""
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


@pytest.mark.parametrize("table", ["journal_audit", "partition"])
def test_le_role_applicatif_ne_peut_ni_modifier_ni_supprimer_ni_vider(
    entree: JournalAudit, role_applicatif: None, table: str
) -> None:
    cible = "journal_audit" if table == "journal_audit" else _partition_courante()
    _doit_echouer(
        f"UPDATE {cible} SET action = 'FALSIFIE' WHERE id_entree = %s", [entree.id_entree]
    )
    _doit_echouer(f"DELETE FROM {cible} WHERE id_entree = %s", [entree.id_entree])
    _doit_echouer(f"TRUNCATE {cible}")


def test_le_role_applicatif_peut_ecrire_et_lire(
    entree: JournalAudit, role_applicatif: None
) -> None:
    with connection.cursor() as curseur:
        curseur.execute(
            "INSERT INTO journal_audit (id_entree, action, type_objet, horodatage, "
            "utilisateur_id_utilisateur) VALUES (%s, 'CONNEXION', 'utilisateur', now(), %s)",
            [uuid.uuid4(), entree.utilisateur_id],
        )
        curseur.execute("SELECT count(*) FROM journal_audit")
        assert curseur.fetchone()[0] >= 2


@pytest.mark.parametrize("table", ["journal_audit", "partition"])
def test_meme_le_proprietaire_est_arrete_par_les_declencheurs(
    entree: JournalAudit, table: str
) -> None:
    cible = "journal_audit" if table == "journal_audit" else _partition_courante()
    _doit_echouer(
        f"UPDATE {cible} SET action = 'FALSIFIE' WHERE id_entree = %s", [entree.id_entree]
    )
    _doit_echouer(f"DELETE FROM {cible} WHERE id_entree = %s", [entree.id_entree])
    _doit_echouer(f"TRUNCATE {cible}")


def test_l_orm_ne_peut_pas_non_plus_modifier(entree: JournalAudit) -> None:
    with pytest.raises(DatabaseError), transaction.atomic():
        JournalAudit.objects.filter(id_entree=entree.id_entree).update(action="FALSIFIE")


def test_aucune_table_du_journal_n_appartient_au_role_applicatif() -> None:
    with connection.cursor() as curseur:
        curseur.execute(
            "SELECT DISTINCT tableowner FROM pg_tables WHERE tablename LIKE 'journal_audit%%'"
        )
        proprietaires = {ligne[0] for ligne in curseur.fetchall()}
    assert proprietaires == {settings.BD_ROLE_PROPRIETAIRE}


def test_une_insertion_hors_de_toute_partition_est_refusee(fabrique_utilisateur) -> None:  # type: ignore[no-untyped-def]
    utilisateur = fabrique_utilisateur()
    _doit_echouer(
        "INSERT INTO journal_audit (id_entree, action, type_objet, horodatage, "
        "utilisateur_id_utilisateur) VALUES (%s, 'CONNEXION', 'utilisateur', "
        "'2001-01-01T00:00:00Z', %s)",
        [uuid.uuid4(), utilisateur.id_utilisateur],
    )


def test_creer_partitions_est_idempotente_et_pose_le_declencheur_tronquer() -> None:
    call_command("creer_partitions", "--mois-avance", "5")
    call_command("creer_partitions", "--mois-avance", "5")
    with connection.cursor() as curseur:
        curseur.execute(
            "SELECT count(*) FROM pg_inherits WHERE inhparent = 'journal_audit'::regclass"
        )
        nombre = curseur.fetchone()[0]
        curseur.execute(
            "SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal "
            "AND tgname LIKE 'trg_journal_audit_%%_tronquer'"
        )
        declencheurs = curseur.fetchone()[0]
    assert nombre >= 7  # un mois passé, le courant, cinq futurs
    assert declencheurs == nombre


def test_id_objet_existe_sur_chaque_partition() -> None:
    """Écart Q-C : la colonne ajoutée sur la table parente (identite 0005)
    est présente sur chaque partition, existante comme créée ensuite."""
    call_command("creer_partitions", "--mois-avance", "6")
    with connection.cursor() as curseur:
        curseur.execute(
            "SELECT c.relname, EXISTS (SELECT 1 FROM pg_attribute a WHERE a.attrelid = c.oid "
            "AND a.attname = 'id_objet' AND NOT a.attisdropped) "
            "FROM pg_inherits i JOIN pg_class c ON c.oid = i.inhrelid "
            "WHERE i.inhparent = 'journal_audit'::regclass"
        )
        partitions = dict(curseur.fetchall())
    assert len(partitions) >= 8
    assert all(partitions.values()), partitions


def test_le_role_applicatif_peut_creer_les_partitions(role_applicatif: None) -> None:
    """La fonction SECURITY DEFINER permet au rôle applicatif de préparer
    les mois futurs sans posséder aucune table (tâche planifiée du PaaS)."""
    call_command("creer_partitions", "--mois-avance", "8")
