"""Fiches de route et affectation des étapes (RG-A3, RG-A7, EF-AVA-02,
EF-AVA-08, AC-3).

Une fiche regroupe les étapes affectées à un technicien pour un cycle de
travail ; le type de cycle est un paramètre du chantier (Q-Z). Affecter une
étape l'inscrit sur la fiche OUVERTE du technicien pour le cycle en cours
(créée au besoin) et la fait passer « en cours » (ET-1 « affectée à un
technicien ») ; réaffecter la retire de l'ancienne fiche et l'écrit au
journal (RG-A3 : « l'affectation et la réaffectation sont tracées »).

En fin de cycle, la fiche est clôturée ; les étapes non faites sont
reportées avec un motif et reprises sur la fiche du cycle suivant (RG-A7).
Le traitement planifié ``cycler_fiches_route`` clôture chaque jour les fiches
échues avec le motif par défaut.
"""

from datetime import date, timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from domaines.avancement.constantes import (
    A_FAIRE,
    CYCLE_JOUR,
    CYCLE_LOGEMENT,
    CYCLE_QUINZAINE,
    CYCLE_SEMAINE,
    EN_COURS,
    FICHE_CLOTUREE,
    FICHE_OUVERTE,
    MOTIF_REPORT_FIN_DE_CYCLE,
    STATUTS_TERMINES,
)
from domaines.avancement.models import EtapeTravaux, FicheRoute, LigneFicheRoute
from domaines.avancement.services import acces, journal, parametres
from socle.api_outils import conflit, donnee_invalide
from socle.erreurs import ErreurApi


def bornes_du_cycle(type_cycle: str, jour: date) -> tuple[date, date | None]:
    """Premier et dernier jour du cycle qui contient ``jour``. Semaine du lundi
    au dimanche ; quinzaine du 1er au 15 ou du 16 à la fin du mois ; un cycle
    « logement » n'a pas de date de fin."""
    if type_cycle == CYCLE_JOUR:
        return jour, jour
    if type_cycle == CYCLE_SEMAINE:
        lundi = jour - timedelta(days=jour.weekday())
        return lundi, lundi + timedelta(days=6)
    if type_cycle == CYCLE_QUINZAINE:
        if jour.day <= 15:
            return jour.replace(day=1), jour.replace(day=15)
        mois_suivant = (jour.replace(day=28) + timedelta(days=4)).replace(day=1)
        return jour.replace(day=16), mois_suivant - timedelta(days=1)
    if type_cycle == CYCLE_LOGEMENT:
        return jour, None
    raise ValueError(f"Type de cycle inconnu : {type_cycle}")


def fiche_du_cycle(technicien: Any, id_chantier: Any, jour: date) -> FicheRoute:
    """Fiche OUVERTE du technicien qui couvre ``jour`` (créée au besoin)."""
    type_cycle = parametres.type_cycle(id_chantier)
    debut, fin = bornes_du_cycle(type_cycle, jour)
    fiche = (
        FicheRoute.objects.select_for_update()
        .filter(utilisateur=technicien, statut=FICHE_OUVERTE, type_cycle=type_cycle)
        .filter(date_debut__lte=jour)
        .exclude(date_fin__lt=jour)
        .order_by("date_debut")
        .first()
    )
    if fiche is None:
        fiche = FicheRoute.objects.create(
            utilisateur=technicien, type_cycle=type_cycle, date_debut=debut, date_fin=fin
        )
    return fiche


def technicien_actuel(etape: EtapeTravaux) -> Any:
    """Technicien de la fiche ouverte qui porte l'étape, ou ``None``."""
    ligne = (
        LigneFicheRoute.objects.select_related("fiche_route__utilisateur")
        .filter(etape_travaux=etape, fiche_route__statut=FICHE_OUVERTE)
        .first()
    )
    return ligne.fiche_route.utilisateur if ligne else None


def _inscrire(fiche: FicheRoute, etape: EtapeTravaux) -> None:
    LigneFicheRoute.objects.get_or_create(
        fiche_route=fiche, etape_travaux=etape, defaults={"ordre": etape.etape_modele.ordre}
    )


@transaction.atomic
def affecter(
    auteur: Any, ids_etapes: list[Any], technicien: Any, date_prevue: date | None
) -> list[EtapeTravaux]:
    """EF-AVA-02 : affecte un lot d'étapes à un technicien, avec date prévue."""
    affectees = []
    for id_etape in ids_etapes:
        etape = acces.etape_autorisee(auteur, id_etape, "fiches-route", "CREER", verrouiller=True)
        if etape.statut in STATUTS_TERMINES:
            raise conflit("ETAPE_TERMINEE", "Une étape terminée ne s'affecte plus.")
        precedent = technicien_actuel(etape)
        if date_prevue is not None:
            etape.date_prevue = date_prevue
            etape.save(update_fields=["date_prevue"])
        if precedent is not None and precedent.pk == technicien.pk:
            affectees.append(etape)
            continue
        LigneFicheRoute.objects.filter(
            etape_travaux=etape, fiche_route__statut=FICHE_OUVERTE
        ).delete()
        jour = timezone.localdate()
        _inscrire(fiche_du_cycle(technicien, etape.logement.zone.chantier_id, jour), etape)
        nom = technicien.nom_complet
        if precedent is None:
            commentaire = f"Affectée à {nom}"
        else:
            commentaire = f"Réaffectée de {precedent.nom_complet} à {nom}"
        statut = EN_COURS if etape.statut == A_FAIRE else etape.statut
        journal.ecrire(etape, auteur, statut, commentaire=commentaire)
        affectees.append(etape)
    return affectees


def fiche_autorisee(utilisateur: Any, id_fiche: Any, action: str) -> FicheRoute:
    """La fiche, si elle appartient à l'utilisateur ou s'il a le droit
    d'encadrement (``api.fiches-route.<action>``)."""
    fiche = FicheRoute.objects.select_related("utilisateur").filter(id_fiche=id_fiche).first()
    if fiche is None:
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Cette fiche est introuvable.")
    if (
        fiche.utilisateur_id != utilisateur.pk
        and acces.chantiers_couverts(utilisateur, "fiches-route", action) == set()
    ):
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Cette fiche est introuvable.")
    return fiche


@transaction.atomic
def cloturer(fiche: FicheRoute, motifs: dict[str, str] | None = None) -> FicheRoute:
    """Clôture la fiche ; les étapes non faites sont reportées avec leur motif
    sur la fiche du cycle suivant du même technicien (RG-A7, EF-AVA-08)."""
    fiche = FicheRoute.objects.select_for_update().get(pk=fiche.pk)
    if fiche.statut != FICHE_OUVERTE:
        raise conflit("FICHE_CLOTUREE", "Cette fiche de route est déjà clôturée.")
    motifs = motifs or {}
    lendemain = max(timezone.localdate(), (fiche.date_fin or fiche.date_debut) + timedelta(days=1))
    a_reporter = []
    for ligne in fiche.lignes.select_related(
        "etape_travaux__logement__zone", "etape_travaux__etape_modele"
    ):
        etape = ligne.etape_travaux
        if etape.statut in STATUTS_TERMINES:
            continue
        ligne.reportee = True
        ligne.motif_report = motifs.get(str(etape.pk)) or MOTIF_REPORT_FIN_DE_CYCLE
        ligne.save(update_fields=["reportee", "motif_report"])
        a_reporter.append(etape)
    fiche.statut, fiche.date_cloture = FICHE_CLOTUREE, timezone.now()
    fiche.save(update_fields=["statut", "date_cloture"])
    for etape in a_reporter:
        suivante = fiche_du_cycle(fiche.utilisateur, etape.logement.zone.chantier_id, lendemain)
        _inscrire(suivante, etape)
    return fiche


def verifier_motifs(fiche: FicheRoute, motifs: dict[str, str]) -> None:
    etapes = {str(i) for i in fiche.lignes.values_list("etape_travaux_id", flat=True)}
    inconnues = set(motifs) - etapes
    if inconnues:
        raise donnee_invalide("reports", "Une étape citée n'est pas sur cette fiche.")


def cycler() -> str:
    """Traitement planifié quotidien : clôture les fiches dont le cycle est
    terminé et reporte leurs étapes non faites. Rejouable."""
    echues = FicheRoute.objects.filter(statut=FICHE_OUVERTE, date_fin__lt=timezone.localdate())
    nombre = 0
    for fiche in echues:
        cloturer(fiche)
        nombre += 1
    return f"{nombre} fiche(s) de route clôturée(s) en fin de cycle."
