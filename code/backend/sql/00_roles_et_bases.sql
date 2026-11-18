-- ============================================================================
-- ChantierSync — rôles PostgreSQL et base de développement.
--
-- À lancer UNE fois par un superutilisateur, avec les mots de passe fournis en
-- variables psql (aucun mot de passe n'est écrit dans ce fichier) :
--
--   psql -U postgres -h 127.0.0.1 ^
--        -v mdp_migration="..." -v mdp_application="..." ^
--        -f code/backend/sql/00_roles_et_bases.sql
--
-- Le script est rejouable : il ne recrée pas ce qui existe déjà et remet les
-- mots de passe aux valeurs fournies.
--
-- POURQUOI TROIS RÔLES (RG-S8, rapport B0 § 4.4, arbitrage Q4) :
-- le propriétaire d'une table garde des droits qu'aucun REVOKE ne lui retire
-- (il peut même désactiver un déclencheur). Pour que les journaux immuables le
-- soient vraiment, l'application ne doit JAMAIS être propriétaire :
--   * chantiersync_proprietaire : NOLOGIN, possède le schéma et toutes les
--     tables. CREATEDB lui permet de créer la base de test (pytest-django).
--   * chantiersync_migration    : LOGIN, membre du propriétaire ; se connecte
--     avec « -c role=chantiersync_proprietaire » pour que tout objet créé par
--     les migrations appartienne au propriétaire. Membre aussi du rôle
--     applicatif, pour que les tests puissent faire « SET ROLE » et prouver
--     que les opérations interdites échouent.
--   * chantiersync_application  : LOGIN, utilisé par Django en marche ; reçoit
--     seulement les droits accordés par les migrations (jamais TRUNCATE ni
--     UPDATE/DELETE sur les tables immuables).
--
-- Critère PaaS (arbitrage Q6) : cette séparation exige le droit de créer des
-- rôles. Sans lui, les déclencheurs protègent encore, mais pas le retrait des
-- droits : limite à documenter au moment du choix de la plateforme.
-- ============================================================================

\set ON_ERROR_STOP on

-- --- Rôles ------------------------------------------------------------------
SELECT 'CREATE ROLE chantiersync_proprietaire NOLOGIN CREATEDB'
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'chantiersync_proprietaire')
\gexec

SELECT format('CREATE ROLE chantiersync_application LOGIN PASSWORD %L', :'mdp_application')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'chantiersync_application')
\gexec

SELECT format('CREATE ROLE chantiersync_migration LOGIN PASSWORD %L', :'mdp_migration')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'chantiersync_migration')
\gexec

-- Mots de passe réalignés si les rôles existaient déjà.
SELECT format('ALTER ROLE chantiersync_application LOGIN PASSWORD %L', :'mdp_application')
\gexec
SELECT format('ALTER ROLE chantiersync_migration LOGIN PASSWORD %L', :'mdp_migration')
\gexec

-- Le rôle applicatif n'hérite de rien et ne peut rien créer.
ALTER ROLE chantiersync_application NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
ALTER ROLE chantiersync_migration NOSUPERUSER NOCREATEROLE;

GRANT chantiersync_proprietaire TO chantiersync_migration;
GRANT chantiersync_application TO chantiersync_migration;

-- --- Base de développement --------------------------------------------------
SELECT 'CREATE DATABASE chantiersync_dev OWNER chantiersync_proprietaire ENCODING ''UTF8'' TEMPLATE template0'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'chantiersync_dev')
\gexec

REVOKE ALL ON DATABASE chantiersync_dev FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE chantiersync_dev TO chantiersync_migration;
GRANT CONNECT ON DATABASE chantiersync_dev TO chantiersync_application;

-- Le reste des droits (schéma public, tables, privilèges par défaut) est posé
-- par la migration « socle 0001 », pour que la base de test créée par
-- pytest-django reçoive exactement les mêmes droits que celle-ci.
