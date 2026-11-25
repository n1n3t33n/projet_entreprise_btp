"""Sauvegarde chiffrée et restauration (EF-ADM-01, Q-BG).

``pg_dump`` et ``pg_restore`` sont remplacés par des doublures : ces tests
vérifient le chiffrement, la conservation et les garde-fous, partout. La
restauration réelle (54 tables comparées) est un essai manuel documenté.
"""

import subprocess
from pathlib import Path
from typing import Any

import pytest
from cryptography.fernet import Fernet
from django.conf import settings
from django.test import override_settings

from socle import sauvegarde

CONTENU = b"PGDMP export factice"


class _Outils:
    """Doublure de subprocess.run : pg_dump écrit un export factice,
    pg_restore mémorise ce qu'il a reçu."""

    def __init__(self, code_retour: int = 0) -> None:
        self.code_retour = code_retour
        self.restaure: bytes | None = None
        self.environnement: dict[str, str] = {}

    def __call__(self, commande: list[str], **options: Any) -> subprocess.CompletedProcess[bytes]:
        self.environnement = options["env"]
        if "--file" in commande:
            Path(commande[commande.index("--file") + 1]).write_bytes(CONTENU)
        else:
            self.restaure = Path(commande[-1]).read_bytes()
        return subprocess.CompletedProcess(commande, self.code_retour, b"", b"erreur de l'outil")


@pytest.fixture
def outils(monkeypatch: pytest.MonkeyPatch) -> _Outils:
    doublure = _Outils()
    monkeypatch.setattr(sauvegarde.subprocess, "run", doublure)
    return doublure


@pytest.fixture
def reglages(tmp_path: Path) -> Any:
    with override_settings(
        SAUVEGARDE_CLE=Fernet.generate_key().decode(),
        SAUVEGARDE_DOSSIER=str(tmp_path),
        SAUVEGARDE_CONSERVATION=2,
    ):
        yield tmp_path


def test_la_sauvegarde_est_chiffree_et_se_restaure(outils: _Outils, reglages: Path) -> None:
    fichier = sauvegarde.sauvegarder()
    assert fichier.parent == reglages
    assert CONTENU not in fichier.read_bytes()  # rien de lisible sur disque
    assert outils.environnement["PGPASSWORD"] == str(settings.DATABASES["migration"]["PASSWORD"])
    sauvegarde.restaurer(fichier, "chantiersync_restauration")
    assert outils.restaure == CONTENU


def test_seules_les_plus_recentes_sont_gardees(outils: _Outils, reglages: Path) -> None:
    for jour in ("20260101", "20260102", "20260103"):
        (reglages / f"{sauvegarde.PREFIXE}{jour}-000000{sauvegarde.SUFFIXE}").write_bytes(b"x")
    sauvegarde.sauvegarder()
    restants = sorted(p.name for p in reglages.glob(f"*{sauvegarde.SUFFIXE}"))
    assert len(restants) == 2
    assert not any("20260101" in nom or "20260102" in nom for nom in restants)


def test_sans_cle_rien_ne_se_sauvegarde(outils: _Outils, tmp_path: Path) -> None:
    with override_settings(SAUVEGARDE_CLE="", SAUVEGARDE_DOSSIER=str(tmp_path)):
        with pytest.raises(sauvegarde.ErreurSauvegarde, match="SAUVEGARDE_CLE"):
            sauvegarde.sauvegarder()


def test_une_autre_cle_ne_dechiffre_pas(outils: _Outils, reglages: Path) -> None:
    fichier = sauvegarde.sauvegarder()
    with override_settings(SAUVEGARDE_CLE=Fernet.generate_key().decode()):
        with pytest.raises(sauvegarde.ErreurSauvegarde, match="ne se déchiffre pas"):
            sauvegarde.restaurer(fichier, "chantiersync_restauration")


def test_la_base_principale_n_est_pas_ecrasee_sans_le_demander(
    outils: _Outils, reglages: Path
) -> None:
    fichier = sauvegarde.sauvegarder()
    principale = str(settings.DATABASES["default"]["NAME"])
    with pytest.raises(sauvegarde.ErreurSauvegarde, match="base principale"):
        sauvegarde.restaurer(fichier, principale)
    sauvegarde.restaurer(fichier, principale, ecraser_principale=True)
    assert outils.restaure == CONTENU


def test_un_echec_de_l_outil_est_lisible_et_sans_secret(
    monkeypatch: pytest.MonkeyPatch, reglages: Path
) -> None:
    monkeypatch.setattr(sauvegarde.subprocess, "run", _Outils(code_retour=1))
    with pytest.raises(sauvegarde.ErreurSauvegarde) as erreur:
        sauvegarde.sauvegarder()
    message = str(erreur.value)
    assert message.startswith("pg_dump a échoué")
    mot_de_passe = str(settings.DATABASES["migration"]["PASSWORD"])
    assert not mot_de_passe or mot_de_passe not in message
