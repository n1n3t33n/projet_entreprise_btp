"""Jetons signés liés à l'appareil et authentification DRF (arbitrage Q2).

Mécanisme retenu (rapport B0 § 6.3) :
  * le jeton est signé par ``django.core.signing`` avec la clé secrète du
    serveur : aucune table, aucune dépendance ; il contient l'utilisateur,
    l'appareil (mobile) et sa date d'émission ;
  * À CHAQUE REQUÊTE, le serveur revérifie que le compte est actif et, pour
    le mobile, que l'appareil est actif : une révocation ou une désactivation
    coupe donc l'accès immédiatement (RG-D5, SQ-5 étape 12), sans liste noire ;
  * durée : 14 jours pour le mobile (verrou ET-4), 8 h pour le web, sans
    appareil ; le mobile reçoit un jeton neuf (en-tête X-Jeton-Renouvele)
    quand le sien a plus de JETON_RENOUVELLEMENT_HEURES heures.

Limite acceptée (arbitrage Q2) : la déconnexion web n'invalide pas le jeton
côté serveur avant ses 8 h ; le navigateur l'oublie, mais une copie volée
resterait valable jusque-là.

Chaque refus porte un MOTIF distinct, parce que le mobile doit savoir s'il
efface ses données (SQ-5 étapes 14-15 : APPAREIL_REVOQUE, COMPTE_DESACTIVE)
ou s'il redemande simplement le mot de passe (JETON_EXPIRE, JETON_INVALIDE).
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core import signing
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from domaines.identite.constantes import STATUT_APPAREIL_REVOQUE
from socle.journalisation import contexte

SEL = "chantiersync.identite.jeton"
TYPE_MOBILE = "MOBILE"
TYPE_WEB = "WEB"


@dataclass(frozen=True)
class InfoJeton:
    """Contenu vérifié d'un jeton."""

    id_utilisateur: str
    id_appareil: str | None
    type: str
    emis_le: int  # secondes depuis l'époque Unix

    @property
    def age(self) -> timedelta:
        return timedelta(seconds=int(timezone.now().timestamp()) - self.emis_le)


def emettre_jeton(utilisateur: Any, appareil: Any = None) -> str:
    """Signe un jeton pour l'utilisateur ; lié à l'appareil s'il y en a un."""
    contenu = {
        "u": str(utilisateur.pk),
        "a": str(appareil.pk) if appareil is not None else None,
        "t": TYPE_MOBILE if appareil is not None else TYPE_WEB,
        "e": int(timezone.now().timestamp()),
    }
    return signing.dumps(contenu, salt=SEL)


def duree_validite(type_jeton: str) -> timedelta:
    if type_jeton == TYPE_MOBILE:
        return timedelta(days=settings.JETON_DUREE_MOBILE_JOURS)
    return timedelta(hours=settings.JETON_DUREE_WEB_HEURES)


def _refus(motif: str, message: str) -> exceptions.AuthenticationFailed:
    return exceptions.AuthenticationFailed(detail=message, code=motif)


def lire_jeton(jeton: str) -> InfoJeton:
    """Vérifie la signature et l'âge d'un jeton, sans toucher à la base."""
    try:
        contenu = signing.loads(jeton, salt=SEL)
        info = InfoJeton(
            id_utilisateur=str(contenu["u"]),
            id_appareil=contenu.get("a"),
            type=str(contenu["t"]),
            emis_le=int(contenu["e"]),
        )
    except (signing.BadSignature, KeyError, TypeError, ValueError) as erreur:
        raise _refus(
            "JETON_INVALIDE", "Votre session n'est plus valide. Connectez-vous à nouveau."
        ) from erreur
    if info.age > duree_validite(info.type):
        raise _refus("JETON_EXPIRE", "Votre session a expiré. Connectez-vous à nouveau.")
    return info


class AuthentificationParJeton(BaseAuthentication):
    """Authentification DRF par « Authorization: Bearer <jeton> »."""

    mot_cle = "Bearer"

    def authenticate(self, request: Request) -> tuple[Any, InfoJeton] | None:
        en_tete = request.headers.get("Authorization", "")
        if not en_tete.startswith(f"{self.mot_cle} "):
            return None  # requête anonyme : les permissions décideront
        info = lire_jeton(en_tete[len(self.mot_cle) + 1 :].strip())

        from domaines.identite.models import Appareil, Utilisateur

        utilisateur = Utilisateur.objects.filter(pk=info.id_utilisateur).first()
        if utilisateur is None:
            raise _refus(
                "JETON_INVALIDE", "Votre session n'est plus valide. Connectez-vous à nouveau."
            )
        if not utilisateur.is_active:
            raise _refus("COMPTE_DESACTIVE", "Ce compte a été désactivé.")

        brut = request._request
        if info.type == TYPE_MOBILE:
            if info.id_appareil is None:
                raise _refus(
                    "JETON_INVALIDE", "Votre session n'est plus valide. Connectez-vous à nouveau."
                )
            appareil = Appareil.objects.filter(pk=info.id_appareil, utilisateur=utilisateur).first()
            if appareil is None or appareil.statut == STATUT_APPAREIL_REVOQUE:
                raise _refus("APPAREIL_REVOQUE", "Cet appareil n'a plus accès à ChantierSync.")
            if not appareil.est_actif:
                raise _refus("APPAREIL_INACTIF", "Cet appareil est désactivé.")
            # Traçabilité (Q-BD) : l'appareil et sa version suivent la requête.
            contexte.appareil.set((str(appareil.pk), appareil.version_application))
            if info.age > timedelta(hours=settings.JETON_RENOUVELLEMENT_HEURES):
                brut.jeton_renouvele = emettre_jeton(utilisateur, appareil)  # type: ignore[attr-defined]
        brut.id_appareil_journal = info.id_appareil  # type: ignore[attr-defined]
        brut.jeton_authentifie = True  # type: ignore[attr-defined]
        return utilisateur, info

    def authenticate_header(self, request: Request) -> str:
        """Fait répondre 401 (et non 403) quand l'authentification manque."""
        return f'{self.mot_cle} realm="api"'
