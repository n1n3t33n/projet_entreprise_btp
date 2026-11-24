"""Indicateurs de l'avancement pour le pilotage (socle/indicateurs.py).

Rapport hebdomadaire (EF-DSH-06) : avancement déclaré et validé de chaque
chantier (RG-A6), étapes déclarées et validées dans la période, blocages et
retards en cours (RG-A8). Usage du pilote (EF-DSH-07) : déclarations reçues,
dont pour le compte d'un autre (RG-A9). Déclarés par ``avancement/apps.py``.
"""

from datetime import date

from django.db.models import F, QuerySet
from django.utils import timezone

from domaines.avancement import selecteurs
from domaines.avancement.constantes import BLOQUEE, TERMINEE_DECLAREE, VALIDEE
from domaines.avancement.models import EtapeTravaux, EvenementExecution
from domaines.organisation import selecteurs as selecteurs_organisation
from socle.indicateurs import RAPPORT, USAGE, Ligne, Rubrique, bornes

PORTEE_CHANTIER = "CHANTIER"


def _periode(debut: date, fin: date) -> QuerySet[EvenementExecution]:
    de, a = bornes(debut, fin)
    return EvenementExecution.objects.filter(horodatage_serveur__gte=de, horodatage_serveur__lt=a)


def rapport(debut: date, fin: date) -> list[Ligne]:
    lignes: list[Ligne] = []
    agregats = selecteurs.agregats(PORTEE_CHANTIER)
    for chantier in selecteurs_organisation.chantiers():
        agregat = agregats.get(str(chantier.pk))
        if agregat is None:
            continue
        lignes.append((f"Avancement déclaré — {chantier.code} (%)", agregat.pourcentage_declare))
        lignes.append((f"Avancement validé — {chantier.code} (%)", agregat.pourcentage_valide))
    evenements = _periode(debut, fin)
    etapes = EtapeTravaux.objects.all()
    lignes += [
        (
            "Étapes déclarées terminées dans la période",
            evenements.filter(statut_apres=TERMINEE_DECLAREE).count(),
        ),
        ("Étapes validées dans la période", evenements.filter(statut_apres=VALIDEE).count()),
        ("Étapes bloquées", etapes.filter(statut=BLOQUEE).count()),
        ("Étapes en retard", etapes.filter(selecteurs.filtre_retard(timezone.localdate())).count()),
    ]
    return lignes


def usage(debut: date, fin: date) -> list[Ligne]:
    evenements = _periode(debut, fin)
    delegations = evenements.filter(pour_le_compte_de__isnull=False).exclude(
        pour_le_compte_de=F("utilisateur")
    )
    return [
        ("Déclarations d'avancement reçues", evenements.count()),
        ("Dont déclarées pour le compte d'un autre", delegations.count()),
    ]


RUBRIQUES = (
    Rubrique(RAPPORT, 10, "Avancement", rapport),
    Rubrique(USAGE, 20, "Saisie de l'avancement", usage),
)
