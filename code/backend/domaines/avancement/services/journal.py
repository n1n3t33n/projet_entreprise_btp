"""Écriture au journal d'exécution (RG-A5).

Point d'écriture unique : tout changement de statut d'une étape passe par
``ecrire``, qui inscrit l'événement immuable (qui, quand côté appareil et
serveur, pour le compte de qui, avant, après, motif) et met à jour le statut
courant de l'étape dans la même transaction. L'appelant a verrouillé l'étape.
On ne corrige jamais un événement : on en écrit un nouveau.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from django.utils import timezone

from domaines.avancement.constantes import LONGUEUR_COMMENTAIRE
from domaines.avancement.models import EtapeTravaux, EvenementExecution
from domaines.avancement.services import agregats


def ecrire(
    etape: EtapeTravaux,
    auteur: Any,
    statut_apres: str,
    *,
    commentaire: str | None = None,
    uuid: UUID | None = None,
    horodatage_appareil: datetime | None = None,
    pour_le_compte_de: Any = None,
    motif_blocage: Any = None,
    article: Any = None,
) -> EvenementExecution:
    valeurs: dict[str, Any] = {
        "statut_avant": etape.statut,
        "statut_apres": statut_apres,
        "horodatage_appareil": horodatage_appareil or timezone.now(),
        "commentaire": (commentaire or None) and commentaire[:LONGUEUR_COMMENTAIRE],
        "etape_travaux": etape,
        "utilisateur": auteur,
        "pour_le_compte_de": pour_le_compte_de,
        "motif_blocage": motif_blocage,
        "article": article,
        "avancement_agrege": agregats.agregat_du_logement(etape.logement),
    }
    if uuid is not None:
        valeurs["uuid"] = uuid
    evenement = EvenementExecution.objects.create(**valeurs)
    if etape.statut != statut_apres:
        etape.statut = statut_apres
        etape.save(update_fields=["statut"])
    return evenement
