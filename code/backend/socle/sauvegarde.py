"""Sauvegarde chiffrée et restauration de la base (EF-ADM-01, Q-BG).

Cahier des charges § 9 : « sauvegardes automatiques et chiffrées avec copie
hors site ; restauration testée », perte maximale d'une heure, reprise en
quatre heures ou moins. Seule la sauvegarde continue de l'hébergeur tient la
perte maximale d'une heure (critère de choix, B7) ; ce module en est le
complément indépendant de l'hébergeur :

  * ``sauvegarder`` : export complet (``pg_dump``, format personnalisé) sous
    le rôle propriétaire, chiffré (``cryptography``, clé ``SAUVEGARDE_CLE``)
    dans ``SAUVEGARDE_DOSSIER`` ; seules les ``SAUVEGARDE_CONSERVATION``
    plus récentes sont gardées. La copie hors site du dossier relève de la
    plateforme (stockage objet) ;
  * ``restaurer`` : déchiffre et recharge une sauvegarde dans une base
    VIDE (jamais la base principale sans demande explicite), puis
    ``comparer`` vérifie table par table le nombre de lignes.

Le mot de passe de la base passe par l'environnement du processus fils
(``PGPASSWORD``), jamais par la ligne de commande ni par les journaux.
"""

import os

# Outils PostgreSQL appelés directement, sans interpréteur de commandes.
import subprocess  # nosec B404
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psycopg
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import connections
from django.utils import timezone
from psycopg import sql

PREFIXE = "chantiersync-"
SUFFIXE = ".dump.chiffre"
LONGUEUR_ERREUR = 500
REQUETE_TABLES = (
    "SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
    "WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p') AND NOT c.relispartition "
    "ORDER BY c.relname"
)


class ErreurSauvegarde(Exception):  # noqa: N818 - nom métier volontairement français
    """Échec lisible par l'exploitant (aucun secret dans le message)."""


@dataclass(frozen=True)
class Ecart:
    table: str
    source: int
    restauree: int | None


def _chiffreur() -> Fernet:
    cle = settings.SAUVEGARDE_CLE
    if not cle:
        raise ErreurSauvegarde(
            "La clé de chiffrement des sauvegardes (SAUVEGARDE_CLE) n'est pas définie."
        )
    try:
        return Fernet(cle)
    except (ValueError, TypeError) as erreur:
        raise ErreurSauvegarde(
            "La clé de chiffrement des sauvegardes n'est pas valide."
        ) from erreur


def _outil(nom: str) -> str:
    dossier = settings.SAUVEGARDE_OUTILS_PG
    if not dossier:
        return nom
    return str(Path(dossier) / (f"{nom}.exe" if os.name == "nt" else nom))


def _connexion(base: str | None = None) -> tuple[list[str], dict[str, str]]:
    """Arguments de connexion (rôle de migration agissant sous le rôle
    propriétaire) et environnement portant le mot de passe."""
    reglages = settings.DATABASES["migration"]
    arguments = [
        "--host",
        str(reglages["HOST"]),
        "--port",
        str(reglages["PORT"]),
        "--username",
        str(reglages["USER"]),
        "--role",
        settings.BD_ROLE_PROPRIETAIRE,
        "--dbname",
        base or str(reglages["NAME"]),
    ]
    return arguments, {**os.environ, "PGPASSWORD": str(reglages["PASSWORD"])}


def _executer(commande: list[str], environnement: dict[str, str]) -> None:
    # Liste d'arguments fixée par la configuration, sans interpréteur de commandes.
    resultat = subprocess.run(  # noqa: S603  # nosec B603
        commande, env=environnement, capture_output=True, check=False
    )
    if resultat.returncode != 0:
        detail = resultat.stderr.decode(errors="replace").strip()[:LONGUEUR_ERREUR]
        raise ErreurSauvegarde(f"{Path(commande[0]).name} a échoué : {detail}")


def sauvegarder() -> Path:
    """Crée une sauvegarde chiffrée et rend son chemin."""
    chiffreur = _chiffreur()
    dossier = Path(settings.SAUVEGARDE_DOSSIER)
    dossier.mkdir(parents=True, exist_ok=True)
    arguments, environnement = _connexion()
    with tempfile.TemporaryDirectory() as temporaire:
        brut = Path(temporaire) / "base.dump"
        _executer(
            [_outil("pg_dump"), "--format=custom", "--file", str(brut), *arguments], environnement
        )
        contenu = chiffreur.encrypt(brut.read_bytes())
    fichier = dossier / f"{PREFIXE}{timezone.localtime():%Y%m%d-%H%M%S}{SUFFIXE}"
    fichier.write_bytes(contenu)
    _elaguer(dossier)
    return fichier


def _elaguer(dossier: Path) -> None:
    """Ne garde que les ``SAUVEGARDE_CONSERVATION`` sauvegardes les plus
    récentes (le nom porte la date, l'ordre alphabétique est chronologique)."""
    fichiers = sorted(dossier.glob(f"{PREFIXE}*{SUFFIXE}"))
    for ancien in fichiers[: max(len(fichiers) - settings.SAUVEGARDE_CONSERVATION, 0)]:
        ancien.unlink()


def restaurer(fichier: Path, base: str, ecraser_principale: bool = False) -> None:
    """Recharge une sauvegarde dans ``base``, qui doit exister (vide de
    préférence). La base principale n'est écrasée que sur demande expresse."""
    if base == settings.DATABASES["default"]["NAME"] and not ecraser_principale:
        raise ErreurSauvegarde(
            "Restaurer sur la base principale écrase toutes ses données : "
            "relancez avec --ecraser-la-base-principale si c'est voulu."
        )
    chiffreur = _chiffreur()
    try:
        brut = chiffreur.decrypt(Path(fichier).read_bytes())
    except InvalidToken as erreur:
        raise ErreurSauvegarde(
            "Ce fichier ne se déchiffre pas avec la clé actuelle (clé différente ou "
            "fichier abîmé)."
        ) from erreur
    arguments, environnement = _connexion(base)
    with tempfile.TemporaryDirectory() as temporaire:
        dechiffre = Path(temporaire) / "base.dump"
        dechiffre.write_bytes(brut)
        _executer(
            [_outil("pg_restore"), "--no-owner", "--exit-on-error", *arguments, str(dechiffre)],
            environnement,
        )


def _compter(curseur: Any) -> dict[str, int]:
    curseur.execute(REQUETE_TABLES)
    tables = [ligne[0] for ligne in curseur.fetchall()]
    comptes: dict[str, int] = {}
    for table in tables:
        curseur.execute(sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table)))
        comptes[table] = curseur.fetchone()[0]
    return comptes


def comparer(base: str) -> tuple[int, list[Ecart]]:
    """Compare le nombre de lignes de chaque table entre la base principale
    et ``base`` ; rend (tables comparées, écarts). Vide = restauration
    fidèle (à lancer juste après la sauvegarde)."""
    with connections["migration"].cursor() as curseur:
        source = _compter(curseur)
    reglages = settings.DATABASES["migration"]
    with (
        psycopg.connect(
            host=str(reglages["HOST"]),
            port=str(reglages["PORT"]),
            user=str(reglages["USER"]),
            password=str(reglages["PASSWORD"]),
            dbname=base,
            options=f"-c role={settings.BD_ROLE_PROPRIETAIRE}",
        ) as connexion,
        connexion.cursor() as curseur,
    ):
        restauree = _compter(curseur)
    ecarts = [
        Ecart(table, nombre, restauree.get(table))
        for table, nombre in source.items()
        if restauree.get(table) != nombre
    ]
    return len(source), ecarts


def traitement() -> str:
    """Traitement planifié ``sauvegarder_base`` ; rend son bilan."""
    fichier = sauvegarder()
    return f"Sauvegarde chiffrée créée : {fichier.name} ({fichier.stat().st_size} octets)."
