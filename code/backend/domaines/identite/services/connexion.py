"""Connexion en ligne et enrôlement (SQ-5 étapes 2 à 5, EF-AUT-03/04, ET-4).

Flux arrêté le 2026-11-10 : connexion EN LIGNE par identifiant et mot de
passe, puis code PIN LOCAL pour l'usage hors ligne. Le serveur ne connaît
jamais le PIN (il reste haché sur le téléphone, CL-6/MPD-6) : il fournit le
jeton, l'appareil enrôlé et l'heure de connexion (``connecte_le``), que le
mobile range dans ``derniere_connexion_en_ligne`` pour son verrou de 14 jours.

EF-AUT-04 (arbitrage Q11) : pas de verrouillage dur du compte après échecs ;
la limitation du taux par identifiant répond « 429 VERROUILLE ».
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from domaines.identite.authentification import emettre_jeton
from domaines.identite.constantes import (
    AUDIT_CONNEXION,
    AUDIT_ECHEC_CONNEXION,
    OBJET_APPAREIL,
    OBJET_UTILISATEUR,
)
from domaines.identite.models import Appareil, Utilisateur
from domaines.identite.models.utilisateur import normaliser_identifiant
from domaines.identite.services import audit
from domaines.identite.services.appareils import DonneesAppareil, enroler
from domaines.identite.services.droits import affectations_actives
from socle.erreurs import ErreurApi

MESSAGE_IDENTIFIANTS = "Identifiant ou mot de passe incorrect."


@dataclass(frozen=True)
class ResultatConnexion:
    jeton: str
    utilisateur: Utilisateur
    appareil: Appareil | None
    connecte_le: datetime


def _refuser_identifiants() -> ErreurApi:
    # Même message que le compte existe ou non : on ne révèle pas quels
    # identifiants sont valides.
    return ErreurApi(statut=401, motif="IDENTIFIANTS", message=MESSAGE_IDENTIFIANTS)


def connecter(
    identifiant: str,
    mot_de_passe: str,
    donnees_appareil: DonneesAppareil | None,
    adresse_ip: str | None,
) -> ResultatConnexion:
    """Vérifie le compte, enrôle l'appareil s'il y en a un, émet le jeton."""
    utilisateur = Utilisateur.objects.filter(
        identifiant=normaliser_identifiant(identifiant)
    ).first()
    if utilisateur is None:
        # Calcul d'empreinte « à vide » : le temps de réponse ne trahit pas
        # l'inexistence du compte.
        make_password(mot_de_passe)
        raise _refuser_identifiants()
    if not utilisateur.check_password(mot_de_passe):
        audit.consigner(utilisateur, AUDIT_ECHEC_CONNEXION, OBJET_UTILISATEUR, adresse_ip)
        raise _refuser_identifiants()
    if not utilisateur.is_active:
        audit.consigner(utilisateur, AUDIT_ECHEC_CONNEXION, OBJET_UTILISATEUR, adresse_ip)
        raise ErreurApi(
            statut=403,
            motif="COMPTE_INACTIF",
            message="Ce compte est désactivé. Adressez-vous à l'administrateur du chantier.",
        )
    if not affectations_actives(utilisateur).exists():
        raise ErreurApi(
            statut=403,
            motif="AUCUNE_AFFECTATION",
            message="Aucun rôle n'est attribué à ce compte. Adressez-vous à l'administrateur.",
        )

    appareil: Any = None
    if donnees_appareil is not None:
        appareil = enroler(utilisateur, donnees_appareil, adresse_ip)
    audit.consigner(
        utilisateur,
        AUDIT_CONNEXION,
        OBJET_APPAREIL if appareil is not None else OBJET_UTILISATEUR,
        adresse_ip,
    )
    return ResultatConnexion(
        jeton=emettre_jeton(utilisateur, appareil),
        utilisateur=utilisateur,
        appareil=appareil,
        connecte_le=timezone.now(),
    )
