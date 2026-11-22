"""Alertes techniques par courriel (exigence 6.7).

Une alerte prévient l'exploitant qu'il faut intervenir : base injoignable,
rafale d'erreurs serveur, traitement planifié en échec, paramètre de chantier
manquant (Q-F, utilisé à partir de B3). Ce n'est pas une notification métier :
celles-là passeront par ``type_notification`` (B6).

Règles :
  * au plus UNE alerte par type et par intervalle (``ALERTES_INTERVALLE_
    MINUTES``, 15 par défaut), pour ne pas noyer la boîte de réception pendant
    une panne ;
  * destinataires, serveur SMTP et seuils viennent de l'environnement ; sans
    destinataire, l'alerte est seulement journalisée ;
  * une alerte ne fait jamais échouer la requête ou le traitement qui la
    déclenche : un échec d'envoi est journalisé, puis oublié ;
  * le message ne contient aucun secret (il passe par le masquage des
    journaux) ni de donnée personnelle.

DETTE (v0.2) : l'anti-répétition s'appuie sur le cache local, donc vaut par
processus. Avec plusieurs processus, chacun peut envoyer sa propre alerte.
"""

import logging

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

from socle.journalisation.masquage import masquer_texte

journal = logging.getLogger("chantiersync.alertes")

# Types d'alerte connus du socle ; un domaine peut en employer d'autres.
BASE_INJOIGNABLE = "BASE_INJOIGNABLE"
ERREURS_SERVEUR = "ERREURS_SERVEUR"
TRAITEMENT_EN_ECHEC = "TRAITEMENT_EN_ECHEC"
PARAMETRE_MANQUANT = "PARAMETRE_MANQUANT"

PREFIXE_SUJET = "[ChantierSync] "


def parametre_manquant(id_chantier: object, cle: str, repli: str) -> bool:
    """Alerte PARAMETRE_MANQUANT commune aux domaines (Q-F, Q-R, Q-Z) :
    ``repli`` dit ce que le serveur fait en attendant."""
    return alerter(
        PARAMETRE_MANQUANT,
        "Paramètre de chantier manquant",
        f"Le paramètre « {cle} » n'est pas défini pour le chantier {id_chantier}. "
        f"{repli} Renseignez-le dans l'écran Paramétrage.",
    )


def alerter(type_alerte: str, sujet: str, message: str) -> bool:
    """Envoie l'alerte si aucune du même type n'est partie dans l'intervalle.
    Rend vrai si l'alerte a été émise (journalisée, et envoyée s'il y a des
    destinataires)."""
    intervalle = settings.ALERTES_INTERVALLE_MINUTES * 60
    # « add » n'écrit que si la clé est absente : c'est le verrou anti-rafale.
    if not cache.add(f"alerte:{type_alerte}", True, timeout=intervalle):
        return False
    message = masquer_texte(message)
    journal.error("alerte technique", extra={"type_alerte": type_alerte, "detail": sujet})
    destinataires = settings.ALERTES_DESTINATAIRES
    if not destinataires:
        return True
    try:
        send_mail(
            PREFIXE_SUJET + sujet,
            message,
            settings.ALERTES_EXPEDITEUR,
            destinataires,
            fail_silently=False,
        )
    except Exception:  # noqa: BLE001 — l'alerte ne doit jamais casser l'appelant
        journal.exception("envoi de l'alerte impossible", extra={"type_alerte": type_alerte})
    return True
