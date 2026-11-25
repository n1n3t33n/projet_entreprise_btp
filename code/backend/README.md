# Backend ChantierSync — Django REST + PostgreSQL 16

API du poste de pilotage web et de l'application mobile de chantier.
Modèle de données : `modélisation/` (le MPD fait foi). Contrat d'API :
[`contrat/CONTRAT.md`](contrat/CONTRAT.md). Rangement du code, trajet d'une
requête et où ajouter quoi : [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Organisation

```
code/backend/
├── configuration/        réglages par environnement, routes racines, WSGI/ASGI
├── socle/                service technique transverse : journaux JSON, santé,
│                         erreurs, limitation du taux, partitions, import CSV,
│                         traitements planifiés, métriques, alertes,
│                         registres de la synchronisation, événements
│                         métier, indicateurs de pilotage
├── domaines/             un dossier par domaine du MERISE
│   ├── identite/         MPD-1 : comptes, rôles, droits, appareils, audit
│   ├── organisation/     MPD-2 : chantiers, magasins, zones, logements, paramètres
│   ├── referentiels/     MPD-3 : catalogue, unités, gammes, mouvements, règles
│   ├── stock/            MPD-4 : mouvements immuables, validations, seuils,
│   │                     stock courant, alertes, inventaires
│   ├── avancement/       MPD-5 : étapes, journal d'exécution, fiches de route,
│   │                     avancement agrégé
│   ├── notifications/    MPD-5 : types, abonnements par rôle, notifications
│   ├── synchronisation/  MPD-6 (serveur) : lots, résultats, curseurs, anomalies
│   ├── pilotage/         rapport hebdomadaire, indicateurs d'usage (sans table)
│   └── acquereur/        espace acquéreur en lecture seule (sans table)
├── contrat/              contrat d'API OpenAPI généré et committé
├── sql/                  création des rôles PostgreSQL et de la base
└── requirements/         dépendances épinglées (base, dev, production)
```

Dans chaque domaine : `models/` (tables du MPD), `services/` (écritures et
règles métier), `selecteurs/` (lectures), `api/` (sérialiseurs, vues,
routes), `migrations/`, `tests/`. Le détail est dans
[`ARCHITECTURE.md`](ARCHITECTURE.md).

## Installation sur le poste de développement (Windows, PowerShell)

Prérequis : Python 3.13, PostgreSQL 16 en service local.

```powershell
# 1. Environnement virtuel et dépendances
python -m venv ..\venv ; ..\venv\Scripts\Activate.ps1
pip install -r requirements\dev.txt

# 2. Configuration : copier puis renseigner (secrets générés localement)
Copy-Item .env.example .env

# 3. Rôles et base (une fois, en superutilisateur PostgreSQL)
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h 127.0.0.1 `
    -v mdp_migration="<DB_MIGRATION_MOT_DE_PASSE>" -v mdp_application="<DB_MOT_DE_PASSE>" `
    -f sql\00_roles_et_bases.sql

# 4. Schéma : TOUJOURS par la connexion « migration » (rôle propriétaire)
python manage.py migrate --database migration

# 5. Données de démonstration (mot de passe : DEMO_MOT_DE_PASSE du .env)
python manage.py charger_demo

# 6. Serveur de développement (port 8000, attendu par le web)
python manage.py runserver 8000
```

Pourquoi `--database migration` : Django tourne avec un rôle PostgreSQL qui
n'est propriétaire d'aucune table et ne peut ni modifier ni vider les
journaux immuables (RG-S8). Les migrations, elles, passent par un rôle qui
agit sous le rôle propriétaire. Un simple `migrate` échoue donc, par
construction.

## Contrôles avant commit

```powershell
python -m ruff check . ; python -m black --check . ; python -m mypy .
python -m bandit -c pyproject.toml -r . ; python -m pip_audit -r requirements\dev.txt -r requirements\production.txt
python -m pytest --cov
```

La suite de tests crée et détruit sa propre base `test_chantiersync` ; elle
ne touche jamais la base de développement.

## Publication (PaaS)

Variables d'environnement : voir `.env.example` (aucun fichier n'est lu en
production), y compris le serveur SMTP et les destinataires des alertes
techniques (`ALERTES_DESTINATAIRES`) et les limites de débit
(`LIMITE_SYNCHRONISATION` : lots par minute et par appareil).

Étapes de publication :

```
python manage.py collectstatic --noinput
python manage.py migrate --database migration
python manage.py creer_partitions
```

Tâches planifiées, toutes par `python manage.py lancer_traitement <nom>` :
`creer_partitions`, `cycler_fiches_route` et `signaler_retards` chaque jour,
`consolider_avancement`, `purger_synchronisation` et `purger_notifications`
chaque nuit, `relancer_validations` chaque heure,
`preparer_rapport_hebdomadaire` chaque lundi, `sauvegarder_base` au moins
chaque jour (chaque heure sans sauvegarde continue de l'hébergeur). Chaque
passage est tracé dans la table
`execution_traitement` et visible dans `GET /api/metriques` ; un échec envoie
une alerte par courriel. Serveur : `gunicorn configuration.wsgi`.

## Sauvegarde et restauration (EF-ADM-01)

La clé de chiffrement est un secret, générée une fois et gardée hors du
dépôt (sans elle, aucune sauvegarde ne se relit) :

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Variables : `SAUVEGARDE_CLE`, `SAUVEGARDE_DOSSIER` (hors du dépôt),
`SAUVEGARDE_CONSERVATION`, et `SAUVEGARDE_OUTILS_PG` si `pg_dump` n'est pas
dans le PATH. La copie hors site du dossier se règle sur la plateforme
(stockage objet).

```powershell
python manage.py sauvegarder
```

Exercice de restauration, à faire régulièrement : créer une base vide, y
restaurer la dernière sauvegarde ; la commande compare ensuite chaque table
à la base principale et s'arrête en erreur au moindre écart.

```powershell
python manage.py restaurer --fichier <sauvegarde>.dump.chiffre --base chantiersync_restauration
```

Reprise après sinistre seulement : `--ecraser-la-base-principale`.

## Choisir l'hébergeur

Le code ne dépend d'aucun hébergeur. Vérifier pour chaque candidat, dans sa
documentation officielle :

| Critère | Pourquoi |
| --- | --- |
| **PostgreSQL 16 géré avec le droit de créer des rôles** (éliminatoire) | Les trois rôles portent l'immuabilité des journaux (RG-S8) ; sans eux, seuls les déclencheurs protègent |
| Sauvegarde continue (restauration à un instant donné) | Perte maximale d'une heure du cahier des charges ; `sauvegarder` n'en est que le complément |
| Localisation des données | Contrainte de localisation à préciser avec Italia |
| Tâches planifiées (cron) | Neuf traitements à lancer par `lancer_traitement` |
| Étape de publication avant démarrage | `collectstatic`, `migrate --database migration`, `creer_partitions` |
| HTTPS géré, en-tête `X-Forwarded-Proto` | `SECURE_PROXY_SSL_HEADER`, redirection HTTPS |
| Stockage hors site pour les sauvegardes | Copie hors site exigée (EF-ADM-01) |
| Disponibilité et prix mensuel | Cible 99 % par mois ; budget du pilote |
