"""Réglages communs à tous les environnements du backend ChantierSync.

Toute valeur vient de l'environnement (arbitrage Q6 : PaaS-agnostique) ; ce
fichier ne contient aucun secret ni aucun chemin disque de données. Les
fichiers developpement.py, test.py et production.py ne font que surcharger
ce qui diffère.
"""

from pathlib import Path

from dotenv import load_dotenv

from socle import environnement as env

# Racine du backend (code/backend/). Sert uniquement à trouver le fichier .env
# local et les fichiers statiques collectés, jamais à stocker des données.
RACINE = Path(__file__).resolve().parent.parent.parent

# En développement, un fichier .env local (ignoré par git) fournit les
# variables. Sur le PaaS il n'existe pas : les variables de la plateforme
# priment toujours (override=False).
load_dotenv(RACINE / ".env", override=False)

SECRET_KEY = env.texte("DJANGO_SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = env.liste("DJANGO_HOTES_AUTORISES")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
# Le framework de permissions de Django n'est PAS utilisé (décision 4.9 du
# rapport B0) : les droits viennent des tables role / permission /
# droit_accorde / affectation_role du MPD-1. « django.contrib.auth » reste
# installé parce que le modèle utilisateur personnalisé et l'administration
# l'exigent ; ses tables auth_permission et auth_group restent vides.
# « django.contrib.sessions » n'est volontairement PAS installé : les sessions
# de l'administration sont des cookies signés (arbitrage Q5), donc aucune
# table django_session (écart Q7-4 au strict minimum).
APPLICATIONS_DJANGO = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
APPLICATIONS_TIERCES = [
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
]
# Une application par domaine du MERISE (README de modélisation § 7) plus le
# socle technique. L'ordre suit le graphe des dépendances (rapport B0 § 5.1) :
# organisation n'a aucune dépendance, identité en dépend, etc.
APPLICATIONS_CHANTIERSYNC = [
    "socle",
    "domaines.organisation",
    "domaines.identite",
    "domaines.referentiels",
    "domaines.stock",
    "domaines.avancement",
    "domaines.synchronisation",
    "domaines.notifications",
    "domaines.pilotage",
    "domaines.acquereur",
]
INSTALLED_APPS = APPLICATIONS_DJANGO + APPLICATIONS_TIERCES + APPLICATIONS_CHANTIERSYNC

MIDDLEWARE = [
    # Identifiant de corrélation et journal de chaque requête (exigence 6.1) :
    # en premier, pour mesurer la durée totale et couvrir toutes les réponses.
    "socle.journalisation.correlation.MiddlewareCorrelation",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # CORS avant CommonMiddleware, comme l'exige django-cors-headers.
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # En-têtes de session du mobile (jeton renouvelé, heure du serveur).
    "domaines.identite.middleware.MiddlewareEnTetesSession",
]

ROOT_URLCONF = "configuration.urls"
WSGI_APPLICATION = "configuration.wsgi.application"
# Base compatible ASGI dès B1 (arbitrage Q3) ; aucun WebSocket.
ASGI_APPLICATION = "configuration.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Base de données PostgreSQL 16
# ---------------------------------------------------------------------------


def _connexion(prefixe: str) -> dict[str, object]:
    """Décrit une connexion à la base commune avec les identifiants ``prefixe``.

    Deux connexions coexistent (rapport B0 § 4.4) :
      * ``default`` : rôle applicatif, NON propriétaire, utilisé en marche ;
      * ``migration`` : rôle de migration, qui agit sous le rôle propriétaire
        (option ``-c role=…``), utilisé par « migrate --database migration ».
    """
    options: dict[str, str] = {}
    role = env.texte_facultatif(f"{prefixe}_ROLE")
    if role:
        options["options"] = f"-c role={role}"
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.texte("DB_NOM"),
        "USER": env.texte(f"{prefixe}_UTILISATEUR"),
        "PASSWORD": env.texte(f"{prefixe}_MOT_DE_PASSE", ""),
        "HOST": env.texte("DB_HOTE", "127.0.0.1"),
        "PORT": env.texte("DB_PORT", "5432"),
        "CONN_MAX_AGE": env.entier("DB_DUREE_CONNEXION", 60),
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": options,
        "TEST": {"NAME": "test_chantiersync"},
    }


DATABASES = {
    "default": _connexion("DB"),
    "migration": _connexion("DB_MIGRATION"),
}

# Noms des rôles PostgreSQL utilisés par les migrations qui posent les droits
# (GRANT / REVOKE) : jamais écrits en dur dans les migrations.
BD_ROLE_APPLICATION = env.texte("BD_ROLE_APPLICATION", "chantiersync_application")
BD_ROLE_PROPRIETAIRE = env.texte("BD_ROLE_PROPRIETAIRE", "chantiersync_proprietaire")

# Toutes les clés primaires du MPD sont explicites ; ce réglage ne sert qu'aux
# tables internes de Django.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Les noms d'index du MPD (ex. « ix_appareil_utilisateur_id_utilisateur »)
# dépassent la limite de 30 caractères que Django impose pour rester
# compatible avec Oracle. PostgreSQL accepte 63 caractères et le MPD fait foi
# sur les noms (contrainte 4.1) : seul ce contrôle de portabilité est
# neutralisé, aucun autre.
SILENCED_SYSTEM_CHECKS = ["models.E034"]

# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------
# Modèle utilisateur personnalisé branché sur la table « utilisateur » du MPD-1.
AUTH_USER_MODEL = "identite.Utilisateur"

# EF-AUT-04 (mot de passe robuste) : validateurs de Django, messages en français.
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {"user_attributes": ("identifiant", "nom", "prenom")},
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Jetons signés liés à l'appareil (arbitrage Q2) : durées paramétrables.
JETON_DUREE_MOBILE_JOURS = env.entier("JETON_DUREE_MOBILE_JOURS", 14)
JETON_DUREE_WEB_HEURES = env.entier("JETON_DUREE_WEB_HEURES", 8)
JETON_RENOUVELLEMENT_HEURES = env.entier("JETON_RENOUVELLEMENT_HEURES", 24)

# Sessions de l'administration : cookies signés, aucune table (arbitrage Q5).
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 8 * 3600

# ---------------------------------------------------------------------------
# API REST
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Jeton porteur uniquement : aucune session sur l'API, donc pas de CSRF.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "domaines.identite.authentification.AuthentificationParJeton",
    ],
    # Refus par défaut : chaque vue déclare en plus son droit ADroit(...)
    # (EF-AUT-07) ou, pour les rares vues publiques, AllowAny explicitement.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_THROTTLE_CLASSES": [
        "socle.limitation.LimitationAnonyme",
        "socle.limitation.LimitationUtilisateur",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anonyme": env.texte("LIMITE_ANONYME", "60/min"),
        "utilisateur": env.texte("LIMITE_UTILISATEUR", "600/min"),
        "connexion_ip": env.texte("LIMITE_CONNEXION_IP", "20/min"),
        "connexion_identifiant": env.texte("LIMITE_CONNEXION_IDENTIFIANT", "10/min"),
        # Lots de synchronisation par appareil (Q-AL).
        "synchronisation": env.texte("LIMITE_SYNCHRONISATION", "30/min"),
    },
    "NUM_PROXIES": env.entier("NOMBRE_MANDATAIRES", 0),
    # Format d'erreur unique { motif, message, details? } (rapport B0 § 3).
    "EXCEPTION_HANDLER": "socle.erreurs.gestionnaire_exceptions",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Décimaux numeric(14,3) transportés en chaîne, comme le web les attend.
    "COERCE_DECIMAL_TO_STRING": True,
    "UNAUTHENTICATED_USER": "django.contrib.auth.models.AnonymousUser",
}

# Documentation générée depuis le code (exigence 6.9).
SPECTACULAR_SETTINGS = {
    "TITLE": "API ChantierSync",
    "DESCRIPTION": (
        "Contrat de l'API REST de ChantierSync, généré depuis le code. "
        "Il fait foi pour le CONTRAT d'API ; le schéma de données, lui, est "
        "défini par le modèle physique (MPD) de la modélisation."
    ),
    "VERSION": "B1",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api",
    "COMPONENT_SPLIT_REQUEST": True,
    # Noms stables pour les listes partagées : {ACTIF, INACTIF} sert au compte
    # comme au chantier ; sans ces noms, l'outil inventerait « Statut4c5Enum ».
    "ENUM_NAME_OVERRIDES": {
        "StatutActiviteEnum": "domaines.identite.constantes.STATUTS_UTILISATEUR",
        "StatutLogementEnum": "domaines.organisation.constantes.STATUTS_LOGEMENT",
    },
}

# ---------------------------------------------------------------------------
# Limitation du taux : compteurs en mémoire locale (arbitrage Q5).
# DETTE : correct pour un seul processus ; un cache partagé sera requis avant
# toute montée en charge multi-processus.
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "chantiersync",
    }
}

# ---------------------------------------------------------------------------
# CORS du poste de pilotage web (rapport B0 § 3.7)
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.liste("CORS_ORIGINES_AUTORISEES")
CORS_ALLOW_CREDENTIALS = False  # jeton porteur, aucun cookie sur l'API
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_METHODS = ("GET", "POST", "PUT", "OPTIONS")
CORS_ALLOW_HEADERS = ("authorization", "content-type", "x-request-id")
CORS_EXPOSE_HEADERS = (
    "X-Request-ID",
    "Retry-After",
    "X-Jeton-Renouvele",
    "X-Horodatage-Serveur",
)

# ---------------------------------------------------------------------------
# Internationalisation : Abidjan est en UTC+0 sans heure d'été ; les
# horodatages sont stockés en timestamptz (MPD) et servis en ISO 8601.
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Fichiers statiques (admin, Swagger, ReDoc) servis par whitenoise : aucun
# serveur de fichiers ni disque persistant requis sur le PaaS.
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
# Hors production, whitenoise sert les fichiers directement depuis les
# applications ; STATIC_ROOT (dossier de « collectstatic ») n'est défini
# qu'en production.
WHITENOISE_USE_FINDERS = True
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ---------------------------------------------------------------------------
# Sécurité commune
# ---------------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
# Les traces d'erreur ne doivent jamais exposer de secret (exigence 6.1).
DEFAULT_EXCEPTION_REPORTER_FILTER = "socle.journalisation.masquage.FiltreRapportErreur"

# ---------------------------------------------------------------------------
# Alertes techniques par courriel (exigence 6.7). SMTP et destinataires
# viennent de l'environnement ; en développement, le courriel s'affiche dans
# la console (developpement.py). Sans destinataire, l'alerte est seulement
# journalisée.
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env.texte("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env.texte("EMAIL_HOTE", "localhost")
EMAIL_PORT = env.entier("EMAIL_PORT", 587)
EMAIL_HOST_USER = env.texte("EMAIL_UTILISATEUR", "")
EMAIL_HOST_PASSWORD = env.texte("EMAIL_MOT_DE_PASSE", "")
EMAIL_USE_TLS = env.booleen("EMAIL_TLS", True)
EMAIL_TIMEOUT = env.entier("EMAIL_DELAI_SECONDES", 10)
ALERTES_EXPEDITEUR = env.texte("ALERTES_EXPEDITEUR", "alertes@chantiersync.invalid")
ALERTES_DESTINATAIRES = env.liste("ALERTES_DESTINATAIRES")
# Seuil « erreurs serveur répétées » : N erreurs 5xx dans la fenêtre.
ALERTES_SEUIL_ERREURS = env.entier("ALERTES_SEUIL_ERREURS", 5)
ALERTES_FENETRE_MINUTES = env.entier("ALERTES_FENETRE_MINUTES", 5)
# Au plus une alerte par type pendant cet intervalle.
ALERTES_INTERVALLE_MINUTES = env.entier("ALERTES_INTERVALLE_MINUTES", 15)

# Partitions mensuelles créées d'avance par « creer_partitions ».
PARTITIONS_MOIS_AVANCE = env.entier("PARTITIONS_MOIS_AVANCE", 3)

# ---------------------------------------------------------------------------
# Journalisation structurée JSON (exigence 6.1)
# ---------------------------------------------------------------------------
NIVEAU_JOURNAL = env.texte("NIVEAU_JOURNAL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        # Masquage des secrets appliqué à TOUT enregistrement, quel qu'il soit.
        "masquage": {"()": "socle.journalisation.masquage.FiltreMasquage"},
    },
    "formatters": {
        "json": {"()": "socle.journalisation.formateur.FormateurJson"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["masquage"],
        },
    },
    "root": {"handlers": ["console"], "level": NIVEAU_JOURNAL},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        # Le journal de chaque requête est écrit par MiddlewareCorrelation, et
        # la trace d'une erreur par socle.erreurs (avec le numéro de suivi) :
        # celui de Django ferait doublon, sans ce numéro.
        "django.request": {"handlers": ["console"], "level": "CRITICAL", "propagate": False},
        "django.server": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "chantiersync": {"handlers": ["console"], "level": NIVEAU_JOURNAL, "propagate": False},
    },
}
