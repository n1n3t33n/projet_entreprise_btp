"""Le schéma réellement créé en base suit le MPD au nom près (contrainte 4.1).

Ces tests interrogent le catalogue PostgreSQL de la base de test, construite
uniquement par les migrations : ce qui est vérifié ici est ce qui existera
en production.
"""

import pytest
from django.apps import apps
from django.db import connection, models

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

# Tables du MPD présentes en B1 : les 10 du MPD-1 et les 2 tables socles du
# MPD-2 dont dépend l'identité.
TABLES_MPD_B1 = {
    "utilisateur",
    "equipe",
    "role",
    "permission",
    "perimetre",
    "appareil",
    "journal_audit",
    "membre_equipe",
    "droit_accorde",
    "affectation_role",
    "chantier",
    "magasin",
}

# Tables internes de Django tolérées (écart Q7-4 au strict minimum) : pas de
# django_session grâce aux cookies signés (arbitrage Q5).
TABLES_DJANGO = {
    "django_migrations",
    "django_content_type",
    "auth_permission",
    "auth_group",
    "auth_group_permissions",
    "django_admin_log",
}

CONTRAINTES_MPD = {
    "uq_utilisateur_identifiant",
    "ck_utilisateur_statut",
    "uq_equipe_code",
    "ck_permission_action",
    "ck_appareil_statut",
    "ck_droit_accorde_portee",
    "uq_chantier_code",
    "ck_chantier_statut",
    "uq_magasin_code",
}

INDEX_MPD = {
    "ix_perimetre_chantier_id_chantier",
    "ix_perimetre_magasin_id_magasin",
    "ix_appareil_utilisateur_id_utilisateur",
    "ix_journal_audit_utilisateur_id_utilisateur",
    "ix_magasin_chantier_id_chantier",
}


def _requete(sql: str) -> set[str]:
    with connection.cursor() as curseur:
        curseur.execute(sql)
        return {ligne[0] for ligne in curseur.fetchall()}


def test_seules_les_tables_attendues_existent() -> None:
    tables = _requete(
        "SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
        "WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p') AND NOT c.relispartition"
    )
    assert tables == TABLES_MPD_B1 | TABLES_DJANGO


def test_les_contraintes_portent_les_noms_du_mpd() -> None:
    contraintes = _requete("SELECT conname FROM pg_constraint")
    assert CONTRAINTES_MPD <= contraintes


def test_les_index_portent_les_noms_du_mpd() -> None:
    index = _requete("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
    assert INDEX_MPD <= index


def test_aucun_index_hors_mpd_sur_les_cles_varchar() -> None:
    index = _requete(
        "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' "
        "AND indexname LIKE '%%_like' AND tablename IN ('role', 'permission')"
    )
    assert index == set()


def test_les_cles_composites_du_mpd_sont_respectees() -> None:
    with connection.cursor() as curseur:
        curseur.execute(
            "SELECT tc.table_name, string_agg(kcu.column_name, ',' ORDER BY kcu.ordinal_position) "
            "FROM information_schema.table_constraints tc "
            "JOIN information_schema.key_column_usage kcu "
            "  ON kcu.constraint_name = tc.constraint_name AND kcu.table_name = tc.table_name "
            "WHERE tc.constraint_type = 'PRIMARY KEY' "
            "AND tc.table_name IN ('droit_accorde', 'affectation_role', 'membre_equipe', 'journal_audit') "
            "GROUP BY tc.table_name"
        )
        cles = dict(curseur.fetchall())
    assert cles == {
        "droit_accorde": "permission_code_permission,role_code_role",
        "affectation_role": "role_code_role,perimetre_id_perimetre,utilisateur_id_utilisateur",
        "membre_equipe": "utilisateur_id_utilisateur,equipe_id_equipe",
        "journal_audit": "id_entree,horodatage",
    }


def test_aucune_quantite_en_virgule_flottante() -> None:
    """MPD § 6.5 : numeric(14,3) pour les quantités, jamais de flottant."""
    flottants = [
        f"{modele.__name__}.{champ.name}"
        for modele in apps.get_models()
        if modele.__module__.startswith("domaines.")
        for champ in modele._meta.get_fields()
        if isinstance(champ, models.FloatField)
    ]
    assert flottants == []


def test_le_referentiel_initial_contient_les_neuf_roles() -> None:
    from domaines.identite.models import Role

    assert set(Role.objects.values_list("code_role", flat=True)) == {
        "DIRECTION",
        "ADMINISTRATEUR",
        "COMMERCIAL",
        "RESPONSABLE_TECHNIQUE",
        "ACQUEREUR",
        "MAGASINIER",
        "TECHNICIEN",
        "CHEF_CHANTIER",
        "GESTIONNAIRE_STOCK",
    }
