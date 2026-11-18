"""Exigence 6.1 : journaux JSON, corrélation, aucun secret journalisé."""

import json
import logging
import sys

from socle.journalisation import contexte
from socle.journalisation.formateur import FormateurJson
from socle.journalisation.masquage import MASQUE, FiltreMasquage, masquer_texte, masquer_valeur


def _enregistrement(message: str, *args: object, **extra: object) -> logging.LogRecord:
    enregistrement = logging.LogRecord(
        "chantiersync.test", logging.INFO, __file__, 1, message, args or None, None
    )
    for cle, valeur in extra.items():
        setattr(enregistrement, cle, valeur)
    return enregistrement


def test_un_jeton_porteur_est_masque_dans_le_texte() -> None:
    texte = masquer_texte("Authorization: Bearer abc.def-123:XYZ suite")
    assert "abc.def-123" not in texte
    assert MASQUE in texte
    assert masquer_texte("jeton reçu : Bearer abc.def-123") == "jeton reçu : Bearer ***"


def test_un_couple_cle_secret_est_masque_dans_le_texte() -> None:
    texte = masquer_texte('{"identifiant": "y.bamba", "mot_de_passe": "Secret-42"}')
    assert "Secret-42" not in texte
    assert "y.bamba" in texte


def test_les_cles_sensibles_sont_masquees_recursivement() -> None:
    donnees = {"identifiant": "a", "jeton": "j", "imbrique": [{"pin": "123456", "nom": "x"}]}
    masque = masquer_valeur(donnees)
    assert masque["jeton"] == MASQUE
    assert masque["imbrique"][0]["pin"] == MASQUE
    assert masque["imbrique"][0]["nom"] == "x"


def test_le_filtre_masque_les_arguments_et_les_extra() -> None:
    enregistrement = _enregistrement(
        "tentative %s", {"mot_de_passe": "Secret-42"}, jeton_session="abc"
    )
    FiltreMasquage().filter(enregistrement)
    assert "Secret-42" not in enregistrement.getMessage()
    assert enregistrement.jeton_session == MASQUE  # type: ignore[attr-defined]


def test_le_formateur_produit_une_ligne_json_avec_la_correlation() -> None:
    jeton = contexte.id_correlation.set("0b7c1f0e-0000-4000-8000-000000000001")
    try:
        enregistrement = _enregistrement("requête traitée", statut=200, route="/api/x", inconnu="?")
        ligne = json.loads(FormateurJson().format(enregistrement))
    finally:
        contexte.id_correlation.reset(jeton)
    assert ligne["id_correlation"] == "0b7c1f0e-0000-4000-8000-000000000001"
    assert ligne["statut"] == 200
    assert ligne["route"] == "/api/x"
    # Liste blanche : un champ non prévu ne sort jamais.
    assert "inconnu" not in ligne


def test_la_trace_d_une_erreur_est_jointe_et_masquee() -> None:
    try:
        raise ValueError("échec avec Bearer jeton-tres-secret")
    except ValueError:
        enregistrement = logging.LogRecord(
            "chantiersync.test", logging.ERROR, __file__, 1, "erreur", None, sys.exc_info()
        )
    ligne = json.loads(FormateurJson().format(enregistrement))
    assert "ValueError" in ligne["trace"]
    assert "jeton-tres-secret" not in ligne["trace"]
