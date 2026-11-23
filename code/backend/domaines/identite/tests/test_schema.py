"""Le schéma réellement créé en base suit le MPD au nom près (contrainte 4.1).

Ces tests interrogent le catalogue PostgreSQL de la base de test, construite
uniquement par les migrations : ce qui est vérifié ici est ce qui existera
en production.
"""

import pytest
from django.apps import apps
from django.db import connection, models

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

# Tables du MPD présentes à ce jalon : MPD-1 (B1), MPD-2 et MPD-3 (B2), MPD-4 (B3), MPD-5 hors notifications (B4),
# MPD-6 côté serveur (B5).
TABLES_MPD = {
    # MPD-1
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
    # MPD-2
    "chantier",
    "magasin",
    "zone",
    "type_logement",
    "logement",
    "parametre_chantier",
    "acquereur",
    # MPD-3
    "categorie_article",
    "unite_mesure",
    "article",
    "conditionnement",
    "corps_etat",
    "gamme",
    "etape_modele",
    "type_mouvement",
    "motif_blocage",
    "regle_validation",
    # MPD-4
    "mouvement_stock",
    "evenement_validation",
    "seuil_stock",
    "stock_courant",
    "alerte",
    "inventaire",
    "ligne_inventaire",
    # MPD-5 (les trois tables de notification arrivent en B6)
    "etape_travaux",
    "evenement_execution",
    "fiche_route",
    "ligne_fiche_route",
    "avancement_agrege",
    # MPD-6 côté serveur (les six tables locales du mobile ne sont pas créées, Q7-3)
    "lot_synchronisation",
    "resultat_evenement",
    "curseur_reference",
    "anomalie_synchronisation",
}

# Tables techniques hors MPD, validées (écart Q9/Q-G : trace des traitements
# ordonnancés).
TABLES_TECHNIQUES = {"execution_traitement"}

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
    # MPD-6
    "ck_resultat_evenement_statut",
    "ck_anomalie_synchronisation_type_anomalie",
    "ck_anomalie_synchronisation_statut",
    # MPD-5 (+ écarts validés Q-V, Q-AA)
    "ck_etape_travaux_statut",
    "ck_fiche_route_type_cycle",
    "ck_fiche_route_statut",
    "ck_evenement_execution_statut_avant",
    "ck_evenement_execution_statut_apres",
    "ck_avancement_agrege_portee",
    "uq_avancement_agrege_portee_id_cible",
    "uq_etape_travaux_logement_etape_modele",
    # MPD-4 (+ écarts validés Q-L, Q-O)
    "ck_mouvement_stock_statut_validation",
    "ck_mouvement_stock_quantites_positives",
    "ck_evenement_validation_decision",
    "ck_stock_courant_niveau_alerte",
    "ck_alerte_type_alerte",
    "ck_alerte_niveau",
    "ck_alerte_statut",
    "ck_inventaire_statut",
    "ck_ligne_inventaire_statut",
    "uq_seuil_stock_magasin_article",
    "uq_utilisateur_identifiant",
    "ck_utilisateur_statut",
    "uq_equipe_code",
    "ck_permission_action",
    "ck_appareil_statut",
    "ck_droit_accorde_portee",
    "uq_chantier_code",
    "ck_chantier_statut",
    "uq_magasin_code",
    # MPD-2
    "ck_parametre_chantier_type_valeur",
    "ck_zone_type_zone",
    "uq_zone_code",
    "ck_logement_statut",
    # MPD-3
    "ck_unite_mesure_type_unite",
    "ck_article_origine",
    "uq_article_code",
    "uq_article_code_barre",
    "ck_gamme_statut",
    "uq_etape_modele_code",
}

INDEX_MPD = {
    # MPD-6 (+ écart Q7-5 : index sur uuid_evenement)
    "ix_lot_synchronisation_appareil_id_appareil",
    "ix_resultat_evenement_lot_synchronisation_id_lot",
    "ix_resultat_evenement_uuid_evenement",
    "ix_anomalie_synchronisation_appareil_id_appareil",
    "ix_anomalie_synchronisation_resultat_evenement_id_resultat",
    # MPD-5
    "ix_etape_travaux_logement_id_logement",
    "ix_etape_travaux_etape_modele_id_etape_modele",
    "ix_etape_travaux_statut",
    "ix_fiche_route_utilisateur_id_utilisateur",
    "ix_evenement_execution_etape_travaux_id_etape",
    "ix_evenement_execution_utilisateur_id_utilisateur",
    "ix_evenement_execution_motif_blocage_code_motif",
    "ix_evenement_execution_article_id_article",
    "ix_evenement_execution_avancement_agrege_id_avancement",
    # MPD-4
    "ix_mouvement_stock_type_mouvement_code_type_mouvement",
    "ix_mouvement_stock_article_id_article",
    "ix_mouvement_stock_magasin_id_magasin",
    "ix_mouvement_stock_logement_id_logement",
    "ix_mouvement_stock_utilisateur_id_utilisateur",
    "ix_mouvement_stock_stock_courant_seuil_stock_id_seuil",
    "ix_mouvement_stock_ligne_inventaire_id_ligne",
    "ix_mouvement_stock_a_valider",
    "ix_evenement_validation_mouvement_stock_uuid",
    "ix_evenement_validation_regle_validation_id_regle",
    "ix_evenement_validation_utilisateur_id_utilisateur",
    "ix_seuil_stock_magasin_id_magasin",
    "ix_seuil_stock_article_id_article",
    "ix_stock_courant_alerte",
    "ix_alerte_stock_courant_seuil_stock_id_seuil",
    "ix_inventaire_magasin_id_magasin",
    "ix_ligne_inventaire_inventaire_id_inventaire",
    "ix_ligne_inventaire_article_id_article",
    "ix_perimetre_chantier_id_chantier",
    "ix_perimetre_magasin_id_magasin",
    "ix_appareil_utilisateur_id_utilisateur",
    "ix_journal_audit_utilisateur_id_utilisateur",
    "ix_magasin_chantier_id_chantier",
    # MPD-2
    "ix_parametre_chantier_chantier_id_chantier",
    "ix_zone_chantier_id_chantier",
    "ix_logement_zone_id_zone",
    "ix_logement_type_logement_code_type",
    "ix_acquereur_logement_id_logement",
    # MPD-3
    "ix_article_categorie_article_code_categorie",
    "ix_article_unite_mesure_code_unite",
    "ix_gamme_type_logement_code_type",
    "ix_etape_modele_gamme_id_gamme",
    "ix_etape_modele_corps_etat_code_corps_etat",
}

# Nullité des clés étrangères tirée des cardinalités du MCD (règle I-32,
# validée le 2026-11-18) : (1,1) → NOT NULL, (0,1) → NULL.
NULLITE_CLES_ETRANGERES = {
    ("appareil", "utilisateur_id_utilisateur"): "NO",
    ("journal_audit", "utilisateur_id_utilisateur"): "NO",
    ("perimetre", "chantier_id_chantier"): "YES",
    ("perimetre", "magasin_id_magasin"): "YES",
    ("magasin", "chantier_id_chantier"): "NO",
    ("zone", "chantier_id_chantier"): "NO",
    ("logement", "zone_id_zone"): "NO",
    ("logement", "type_logement_code_type"): "NO",
    ("parametre_chantier", "chantier_id_chantier"): "NO",
    ("acquereur", "logement_id_logement"): "NO",
    ("article", "categorie_article_code_categorie"): "YES",
    ("article", "unite_mesure_code_unite"): "NO",
    ("gamme", "type_logement_code_type"): "NO",
    ("etape_modele", "gamme_id_gamme"): "NO",
    ("etape_modele", "corps_etat_code_corps_etat"): "NO",
    # MPD-4 (logement : NULL malgré le (1,1) du MCD, I-38)
    ("mouvement_stock", "type_mouvement_code_type_mouvement"): "NO",
    ("mouvement_stock", "article_id_article"): "NO",
    ("mouvement_stock", "magasin_id_magasin"): "NO",
    ("mouvement_stock", "utilisateur_id_utilisateur"): "NO",
    ("mouvement_stock", "stock_courant_seuil_stock_id_seuil"): "NO",
    ("mouvement_stock", "logement_id_logement"): "YES",
    ("mouvement_stock", "ligne_inventaire_id_ligne"): "YES",
    ("evenement_validation", "mouvement_stock_uuid"): "NO",
    ("evenement_validation", "regle_validation_id_regle"): "YES",
    ("evenement_validation", "utilisateur_id_utilisateur"): "NO",
    ("seuil_stock", "magasin_id_magasin"): "NO",
    ("seuil_stock", "article_id_article"): "NO",
    ("alerte", "stock_courant_seuil_stock_id_seuil"): "NO",
    ("inventaire", "magasin_id_magasin"): "NO",
    ("ligne_inventaire", "inventaire_id_inventaire"): "NO",
    ("ligne_inventaire", "article_id_article"): "NO",
    # MPD-5
    ("etape_travaux", "logement_id_logement"): "NO",
    ("etape_travaux", "etape_modele_id_etape_modele"): "NO",
    ("fiche_route", "utilisateur_id_utilisateur"): "NO",
    ("evenement_execution", "etape_travaux_id_etape"): "NO",
    ("evenement_execution", "utilisateur_id_utilisateur"): "NO",
    ("evenement_execution", "motif_blocage_code_motif"): "YES",
    ("evenement_execution", "article_id_article"): "YES",
    ("evenement_execution", "avancement_agrege_id_avancement"): "NO",
    ("evenement_execution", "pour_le_compte_de_id_utilisateur"): "YES",
    # MPD-6
    ("lot_synchronisation", "appareil_id_appareil"): "NO",
    ("resultat_evenement", "lot_synchronisation_id_lot"): "NO",
    ("curseur_reference", "appareil_id_appareil"): "NO",
    ("anomalie_synchronisation", "appareil_id_appareil"): "NO",
    ("anomalie_synchronisation", "resultat_evenement_id_resultat"): "YES",
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
    assert tables == TABLES_MPD | TABLES_DJANGO | TABLES_TECHNIQUES


def test_la_nullite_des_cles_etrangeres_suit_le_mcd() -> None:
    with connection.cursor() as curseur:
        curseur.execute(
            "SELECT table_name, column_name, is_nullable FROM information_schema.columns "
            "WHERE table_schema = 'public'"
        )
        colonnes = {(table, colonne): nulle for table, colonne, nulle in curseur.fetchall()}
    ecarts = {
        cle: (colonnes.get(cle), attendu)
        for cle, attendu in NULLITE_CLES_ETRANGERES.items()
        if colonnes.get(cle) != attendu
    }
    assert ecarts == {}


def test_les_contraintes_portent_les_noms_du_mpd() -> None:
    contraintes = _requete("SELECT conname FROM pg_constraint")
    assert CONTRAINTES_MPD <= contraintes


def test_les_index_portent_les_noms_du_mpd() -> None:
    index = _requete("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
    assert INDEX_MPD <= index


def test_aucun_index_hors_mpd_sur_les_cles_varchar() -> None:
    index = _requete(
        "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' "
        "AND indexname LIKE '%%_like' AND tablename NOT LIKE 'auth_%%' "
        "AND tablename NOT LIKE 'django_%%'"
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
            "AND tc.table_name IN ('droit_accorde', 'affectation_role', 'membre_equipe', "
            "'journal_audit', 'evenement_validation', 'stock_courant', "
            "'evenement_execution', 'ligne_fiche_route', 'curseur_reference') "
            "GROUP BY tc.table_name"
        )
        cles = dict(curseur.fetchall())
    assert cles == {
        "droit_accorde": "permission_code_permission,role_code_role",
        "affectation_role": "role_code_role,perimetre_id_perimetre,utilisateur_id_utilisateur",
        "membre_equipe": "utilisateur_id_utilisateur,equipe_id_equipe",
        "journal_audit": "id_entree,horodatage",
        "evenement_validation": "uuid,horodatage_serveur",
        "stock_courant": "seuil_stock_id_seuil",
        "evenement_execution": "uuid,horodatage_serveur",
        "ligne_fiche_route": "fiche_route_id_fiche,etape_travaux_id_etape",
        "curseur_reference": "appareil_id_appareil,type_donnee",
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
