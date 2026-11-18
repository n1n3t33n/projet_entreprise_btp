"""Socle 0001 — fonctions PostgreSQL partagées et droits du rôle applicatif.

Écrite à la main : Django ne sait exprimer ni fonctions PL/pgSQL, ni GRANT,
ni privilèges par défaut. Réversible (fonction ``retirer``).

Ce que pose cette migration (rapport B0 § 4.4 et § 4.5, arbitrage Q4) :

1. ``socle_rejeter_modification()`` — fonction de déclencheur qui refuse
   toute modification, suppression ou vidage d'un journal immuable (RG-S8 :
   « un mouvement ne se supprime ni ne se modifie »). Les tables immuables
   l'attachent en BEFORE UPDATE OR DELETE (par ligne) et BEFORE TRUNCATE (par
   instruction).

2. ``socle_creer_partition_mensuelle(table, mois)`` — crée la partition
   mensuelle d'un journal partitionné, lui pose son propre déclencheur
   TRUNCATE (un TRUNCATE visant directement une partition ne déclenche QUE les
   déclencheurs d'instruction de cette partition) et réaffirme ses droits :
   SELECT et INSERT seulement pour le rôle applicatif. SECURITY DEFINER : elle
   s'exécute avec les droits de son propriétaire, si bien que le rôle
   applicatif peut créer les partitions futures sans posséder aucune table.
   Hypothèse vérifiée au MPD : les trois tables partitionnées (journal_audit,
   evenement_validation, evenement_execution) sont toutes des journaux
   immuables, d'où le retrait systématique de UPDATE/DELETE.

3. Droits du schéma ``public`` : le rôle applicatif y lit et écrit les tables
   ordinaires (privilèges par défaut sur toute table future du propriétaire),
   mais n'y crée rien. Posés ici plutôt que dans le script SQL pour que la
   base de test de pytest-django reçoive exactement les mêmes droits.
"""

from django.conf import settings
from django.db import migrations
from psycopg import sql

from socle.base_de_donnees.sql import executer, role_application, role_proprietaire

FONCTION_REJET = """
CREATE OR REPLACE FUNCTION socle_rejeter_modification()
RETURNS trigger
LANGUAGE plpgsql
AS $fonction$
BEGIN
    -- RG-S8 : un journal immuable ne se modifie, ne se supprime ni ne se vide.
    -- Une erreur se corrige par une nouvelle entrée, jamais par une réécriture.
    RAISE EXCEPTION 'Journal non modifiable : % refusé sur la table %.', TG_OP, TG_TABLE_NAME
        USING ERRCODE = 'restrict_violation';
END;
$fonction$
"""

FONCTION_PARTITION = """
CREATE OR REPLACE FUNCTION socle_creer_partition_mensuelle(p_table text, p_mois date)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $fonction$
DECLARE
    -- Bornes en UTC explicite : l'heure de session ne doit jamais décaler
    -- une borne de partition.
    v_debut timestamptz := make_timestamptz(
        extract(year FROM p_mois)::int, extract(month FROM p_mois)::int, 1, 0, 0, 0, 'UTC');
    v_fin timestamptz := v_debut + interval '1 month';
    v_nom text := p_table || '_' || to_char(p_mois, 'YYYY_MM');
BEGIN
    -- Garde-fou : seule une table réellement partitionnée du schéma public
    -- est acceptée (la fonction tourne avec les droits du propriétaire).
    IF NOT EXISTS (
        SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relname = p_table AND c.relkind = 'p'
    ) THEN
        RAISE EXCEPTION 'La table % n''est pas une table partitionnée.', p_table;
    END IF;

    IF to_regclass(format('public.%I', v_nom)) IS NULL THEN
        EXECUTE format(
            'CREATE TABLE public.%I PARTITION OF public.%I FOR VALUES FROM (%L) TO (%L)',
            v_nom, p_table, v_debut, v_fin);
        -- Le déclencheur ligne UPDATE/DELETE du parent est cloné
        -- automatiquement sur la partition ; le déclencheur TRUNCATE, lui,
        -- ne l'est pas : on le pose ici, sur chaque partition.
        EXECUTE format(
            'CREATE TRIGGER %I BEFORE TRUNCATE ON public.%I '
            'FOR EACH STATEMENT EXECUTE FUNCTION socle_rejeter_modification()',
            'trg_' || v_nom || '_tronquer', v_nom);
    END IF;

    -- Un accès direct à une partition contrôle les droits de la partition :
    -- on les réaffirme à chaque passage (idempotent).
    EXECUTE format('REVOKE ALL ON public.%I FROM %I', v_nom, {role_application});
    EXECUTE format('GRANT SELECT, INSERT ON public.%I TO %I', v_nom, {role_application});
    RETURN v_nom;
END;
$fonction$
"""

SIGNATURE_PARTITION = "socle_creer_partition_mensuelle(text, date)"


def poser(apps: object, schema_editor: object) -> None:
    """Crée les fonctions et pose les droits du rôle applicatif."""
    application = role_application()
    proprietaire = role_proprietaire()
    executer(schema_editor, sql.SQL(FONCTION_REJET))
    executer(
        schema_editor,
        sql.SQL(FONCTION_PARTITION).format(
            role_application=sql.Literal(settings.BD_ROLE_APPLICATION)
        ),
    )
    executer(
        schema_editor,
        sql.SQL("REVOKE ALL ON FUNCTION " + SIGNATURE_PARTITION + " FROM PUBLIC"),
    )
    executer(
        schema_editor,
        sql.SQL("GRANT EXECUTE ON FUNCTION " + SIGNATURE_PARTITION + " TO {}").format(application),
    )
    # Schéma public : personne ne crée d'objet hors du propriétaire.
    executer(schema_editor, sql.SQL("REVOKE ALL ON SCHEMA public FROM PUBLIC"))
    executer(schema_editor, sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(application))
    # Tables déjà présentes (tables internes de Django créées avant) …
    executer(
        schema_editor,
        sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {}").format(
            application
        ),
    )
    executer(
        schema_editor,
        sql.SQL("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {}").format(application),
    )
    # … et toute table future créée par le propriétaire. Jamais TRUNCATE,
    # TRIGGER ni REFERENCES. Les tables immuables retirent ensuite UPDATE et
    # DELETE dans leur propre migration.
    executer(
        schema_editor,
        sql.SQL(
            "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
            "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {}"
        ).format(proprietaire, application),
    )
    executer(
        schema_editor,
        sql.SQL(
            "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
            "GRANT USAGE, SELECT ON SEQUENCES TO {}"
        ).format(proprietaire, application),
    )


def retirer(apps: object, schema_editor: object) -> None:
    """Retour arrière : retire droits par défaut et fonctions."""
    application = role_application()
    proprietaire = role_proprietaire()
    executer(
        schema_editor,
        sql.SQL(
            "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
            "REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM {}"
        ).format(proprietaire, application),
    )
    executer(
        schema_editor,
        sql.SQL(
            "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
            "REVOKE USAGE, SELECT ON SEQUENCES FROM {}"
        ).format(proprietaire, application),
    )
    executer(schema_editor, sql.SQL("DROP FUNCTION IF EXISTS " + SIGNATURE_PARTITION))
    executer(schema_editor, sql.SQL("DROP FUNCTION IF EXISTS socle_rejeter_modification()"))


class Migration(migrations.Migration):
    initial = True
    dependencies: list[tuple[str, str]] = []
    # Avant les tables internes de Django, pour que les droits par défaut
    # s'appliquent à toutes les tables créées ensuite.
    run_before = [("contenttypes", "0001_initial")]

    operations = [migrations.RunPython(poser, retirer)]
