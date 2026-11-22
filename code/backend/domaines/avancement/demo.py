"""Données de démonstration du domaine « avancement », reprises de la
simulation du web (``lib/mocks/avancement-grand-bassam.ts``) : douze logements
sur trois îlots, gamme de dix étapes, (rang × 7) modulo 11 étapes validées
par logement, des étapes en retard, en attente de contrôle et bloquées.

Logements de rang pair : le technicien Kouassi Adama déclare lui-même.
Logements de rang impair : le maçon Adama Koné n'a pas de compte (H7) ; son
chef d'équipe Koffi N'Guessan déclare pour lui (délégation, RG-A9). Le chef de
chantier contrôle les étapes à contrôle (RG-A4).

Tout passe par les services du domaine ; identifiants d'événement stables :
le chargement est rejouable sans doublon. Logements, comptes, motifs et
articles sont LUS par les sélecteurs de leurs domaines (rang 40, après le
stock).
"""

from datetime import datetime, time, timedelta
from typing import Any

from django.utils import timezone

from domaines.avancement.constantes import (
    EN_COURS,
    STATUTS_TERMINES,
    TERMINEE_DECLAREE,
    VALIDEE,
)
from domaines.avancement.models import EtapeTravaux, EvenementExecution
from domaines.avancement.services import agregats, declarations, fiches, instanciation
from domaines.identite.selecteurs import comptes
from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.referentiels import selecteurs as selecteurs_referentiels
from socle.demo import uid

ECART_JOURS = 4  # une étape tous les quatre jours, comme le web


def _rang(numero: str) -> int:
    """A01 → 0, B01 → 1, C01 → 2, A02 → 3… (ordre de la démo organisation)."""
    return (int(numero[1:]) - 1) * 3 + "ABC".index(numero[0])


def _compte(identifiant: str) -> Any:
    compte = comptes.par_identifiant(identifiant)
    if compte is None:
        raise LookupError(f"Le compte de démonstration « {identifiant} » doit être chargé d'abord.")
    return compte


def _instant(jour: Any) -> datetime:
    return timezone.make_aware(datetime.combine(jour, time(16, 0)))


def _derouler(logement: Any, rang: int, acteurs: dict[str, Any], article: Any) -> None:
    etapes = list(
        EtapeTravaux.objects.filter(logement=logement)
        .select_related("etape_modele")
        .order_by("etape_modele__ordre")
    )
    validees = (rang * 7) % 11
    aujourd_hui = timezone.localdate()
    technicien = acteurs["technicien"] if rang % 2 == 0 else acteurs["equipier"]
    declarant = acteurs["technicien"] if rang % 2 == 0 else acteurs["chef_equipe"]
    # Deux logements en retard (RG-A8) : leur étape suivante n'est ni à
    # contrôle ni bloquée, elle reste donc « en cours » au-delà de sa date.
    retard = 3 if rang in (1, 7) else 0
    courantes = etapes[: validees + 1]
    for etape in courantes:
        if etape.statut in STATUTS_TERMINES:  # rejeu : déjà faite, rien à affecter
            continue
        decalage = (etape.etape_modele.ordre - validees - 1 - retard) * ECART_JOURS
        fiches.affecter(
            acteurs["responsable"], [etape.pk], technicien, aujourd_hui + timedelta(days=decalage)
        )
    for etape in courantes[:validees]:
        etape.refresh_from_db()
        if etape.statut == EN_COURS:
            declarations.declarer_terminee(
                declarant,
                etape.pk,
                uuid=uid("evenement", f"{logement.numero}-{etape.etape_modele.ordre}-declaration"),
                horodatage_appareil=_instant(etape.date_prevue),
            )
        etape.refresh_from_db()
        if etape.statut == TERMINEE_DECLAREE:
            declarations.decider(
                acteurs["chef"],
                etape.pk,
                declarations.DECISION_ACCEPTE,
                None,
                uid("evenement", f"{logement.numero}-{etape.etape_modele.ordre}-controle"),
            )
    if validees >= len(etapes):
        return
    suivante = etapes[validees]
    suivante.refresh_from_db()
    if suivante.statut != EN_COURS:
        return
    # L'étape suivante, si elle est à contrôle, attend le chef (RG-A4).
    if suivante.etape_modele.controle_requis:
        declarations.declarer_terminee(
            declarant,
            suivante.pk,
            uuid=uid("evenement", f"{logement.numero}-{suivante.etape_modele.ordre}-declaration"),
        )
    elif rang % 6 in (3, 5):
        declarations.bloquer(
            declarant,
            suivante.pk,
            "MANQUE_MATERIEL",
            id_article=article.pk,
            commentaire="Rupture au magasin",
            uuid=uid("evenement", f"{logement.numero}-{suivante.etape_modele.ordre}-blocage"),
        )


def charger(mot_de_passe: str) -> dict[str, int]:
    acteurs = {
        "technicien": _compte("technicien"),
        "equipier": _compte("a.kone"),
        "chef_equipe": _compte("k.n-guessan"),
        "chef": _compte("chef"),
        "responsable": _compte("responsable"),
    }
    article = selecteurs_referentiels.articles().first()
    logements = list(selecteurs_organisation.logements().select_related("zone"))
    for logement in logements:
        instanciation.generer(logement)
    for logement in sorted(logements, key=lambda lo: _rang(lo.numero)):
        _derouler(logement, _rang(logement.numero), acteurs, article)
    agregats.consolider()
    return {
        "étapes": EtapeTravaux.objects.count(),
        "validées": EtapeTravaux.objects.filter(statut=VALIDEE).count(),
        "événements": EvenementExecution.objects.count(),
    }
