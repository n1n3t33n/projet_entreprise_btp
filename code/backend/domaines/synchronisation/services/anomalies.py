"""Anomalies de synchronisation (EF-SYN-05, CL-6 ``AnomalieSynchronisation``).

Une anomalie est signalée par un appareil (« signale », (1,1)) et peut être
motivée par le résultat d'un événement (« motive », (0,1)) : rejet d'une
règle, conflit avec l'état du serveur, stock devenu négatif. La dérive
d'horloge (RG-S11) concerne le lot entier et ne cite aucun résultat.
"""

from datetime import datetime, timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from domaines.identite.models import Appareil
from domaines.synchronisation.constantes import (
    ANOMALIE_TRAITEE,
    CONFLIT_VERSION,
    DERIVE_HORLOGE,
    DERIVE_HORLOGE_MAX_MIN,
    MOTIFS_CONFLIT,
    REJET_REGLE,
)
from domaines.synchronisation.models import AnomalieSynchronisation, ResultatEvenement
from socle.api_outils import obtenir_ou_404
from socle.evenements import EvenementMetier, publier

ANOMALIE_SYNCHRONISATION = "ANOMALIE_SYNCHRONISATION"


def signaler(
    appareil: Appareil,
    type_anomalie: str,
    description: str,
    resultat: ResultatEvenement | None = None,
) -> AnomalieSynchronisation:
    anomalie = AnomalieSynchronisation.objects.create(
        appareil=appareil,
        type_anomalie=type_anomalie,
        description=description,
        resultat_evenement=resultat,
    )
    # Sans lieu : un appareil n'appartient à aucun chantier au MPD.
    publier(
        EvenementMetier(
            code=ANOMALIE_SYNCHRONISATION,
            id_objet=anomalie.pk,
            contexte={"description": description},
        )
    )
    return anomalie


def signaler_rejet(appareil: Appareil, resultat: ResultatEvenement) -> AnomalieSynchronisation:
    """Un rejet dû à un état changé sur le serveur (décision déjà prise,
    étape déjà terminée…) est un conflit ; les autres sont des rejets de
    règle."""
    type_anomalie = CONFLIT_VERSION if resultat.code_rejet in MOTIFS_CONFLIT else REJET_REGLE
    return signaler(appareil, type_anomalie, resultat.motif_rejet or "", resultat)


def traiter(id_anomalie: Any) -> tuple[AnomalieSynchronisation, bool]:
    """Marque une anomalie traitée (EF-SYN-05). Rend (anomalie, changée ?) :
    traiter deux fois ne change rien (rejeu d'un événement mobile)."""
    with transaction.atomic():
        anomalie = obtenir_ou_404(
            AnomalieSynchronisation.objects.select_for_update(),
            "Cette anomalie est introuvable.",
            pk=id_anomalie,
        )
        if anomalie.statut == ANOMALIE_TRAITEE:
            return anomalie, False
        anomalie.statut = ANOMALIE_TRAITEE
        anomalie.save(update_fields=["statut"])
    return anomalie, True


def verifier_horloge(appareil: Appareil, horodatage_envoi: datetime | None) -> None:
    """RG-S11 : l'heure d'envoi déclarée par l'appareil ne doit pas s'écarter
    de celle du serveur de plus de ``DERIVE_HORLOGE_MAX_MIN`` minutes."""
    if horodatage_envoi is None:
        return
    ecart = abs(timezone.now() - horodatage_envoi)
    if ecart > timedelta(minutes=DERIVE_HORLOGE_MAX_MIN):
        minutes = int(ecart.total_seconds() // 60)
        signaler(
            appareil,
            DERIVE_HORLOGE,
            f"L'horloge de l'appareil est décalée d'environ {minutes} minutes "
            "par rapport au serveur.",
        )
