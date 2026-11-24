"""Déclarations et contrôle des étapes (ET-1, RG-A2 à RG-A5, RG-A9, RG-A10,
RG-D11 ; EF-AVA-04 à 07, SQ-3, AC-4).

Transitions (ET-1) :
  EN_COURS          → TERMINEE_DECLAREE  déclarer terminée (EF-AVA-04)
  TERMINEE_DECLAREE → VALIDEE            implicite si l'étape n'est pas à
                                         contrôle (Q-X) ; sinon décision
  TERMINEE_DECLAREE → EN_COURS           rejet motivé (RG-A2)
  A_FAIRE, EN_COURS → BLOQUEE            blocage motivé (EF-AVA-05)
  BLOQUEE           → EN_COURS / A_FAIRE levée du blocage

Qui déclare (RG-A3) : le technicien affecté, son chef d'équipe, ou
l'encadrement du chantier (droit ``api.etapes.valider``). Quand l'auteur n'est
pas le technicien affecté, la déclaration est une délégation : le technicien
est inscrit dans ``pour_le_compte_de`` (RG-A9, Q-W), figé à l'écriture.

Contrôle (RG-A4, RG-D11) : une étape à contrôle est validée par une autre
personne que celle qui l'a déclarée et que celle pour qui elle l'a été.

Idempotence (téléphone hors ligne, 6.4) : un ``uuid`` d'événement déjà reçu
rend l'événement existant sans rien écrire.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from domaines.avancement.constantes import (
    A_FAIRE,
    BLOQUEE,
    COMMENTAIRE_VALIDATION_IMPLICITE,
    EN_COURS,
    TERMINEE_DECLAREE,
    VALIDEE,
)
from domaines.avancement.models import EtapeTravaux, EvenementExecution
from domaines.avancement.services import acces, fiches, journal, publications
from domaines.identite.selecteurs import equipes
from domaines.referentiels import selecteurs as selecteurs_referentiels
from socle.api_outils import conflit, donnee_invalide
from socle.erreurs import ErreurApi

DECISION_ACCEPTE = "ACCEPTE"
DECISION_REFUSE = "REFUSE"
DECISIONS: tuple[str, ...] = (DECISION_ACCEPTE, DECISION_REFUSE)


def _deja_recu(uuid: UUID | None) -> list[EvenementExecution] | None:
    if uuid is None:
        return None
    existant = EvenementExecution.objects.filter(uuid=uuid).first()
    return [existant] if existant else None


def _transition_impossible(etape: EtapeTravaux, action: str) -> ErreurApi:
    return conflit(
        "TRANSITION_IMPOSSIBLE",
        f"Impossible de {action} une étape au statut « {etape.statut} ».",
    )


def _encadre(utilisateur: Any, etape: EtapeTravaux) -> bool:
    couverts = acces.chantiers_couverts(utilisateur, "etapes", "VALIDER")
    return couverts is None or etape.logement.zone.chantier_id in couverts


def pour_le_compte_de(auteur: Any, etape: EtapeTravaux) -> Any:
    """RG-A3 : rend le technicien pour qui l'auteur déclare (``None`` s'il
    déclare pour lui-même), ou refuse."""
    technicien = fiches.technicien_actuel(etape)
    if technicien is not None and technicien.pk == auteur.pk:
        return None
    if technicien is not None and auteur.pk in equipes.chefs_de(technicien):
        return technicien
    if _encadre(auteur, etape):
        return technicien
    raise ErreurApi(
        statut=403,
        motif="DECLARATION_INTERDITE",
        message="Seuls le technicien affecté, son chef d'équipe ou le chef de chantier "
        "peuvent déclarer cette étape.",
    )


@transaction.atomic
def declarer_terminee(
    auteur: Any,
    id_etape: Any,
    *,
    uuid: UUID | None = None,
    horodatage_appareil: datetime | None = None,
    commentaire: str | None = None,
) -> tuple[list[EvenementExecution], bool]:
    """EF-AVA-04. Rend (événements, créés ?)."""
    deja = _deja_recu(uuid)
    if deja:
        return deja, False
    etape = acces.etape_autorisee(auteur, id_etape, "etapes", "MODIFIER", verrouiller=True)
    if etape.statut != EN_COURS:
        raise _transition_impossible(etape, "déclarer terminée")
    pour = pour_le_compte_de(auteur, etape)
    instant = horodatage_appareil or timezone.now()
    evenements = [
        journal.ecrire(
            etape,
            auteur,
            TERMINEE_DECLAREE,
            uuid=uuid,
            horodatage_appareil=instant,
            pour_le_compte_de=pour,
            commentaire=commentaire,
        )
    ]
    etape.date_fin_declaree = timezone.localtime(instant).date()
    etape.save(update_fields=["date_fin_declaree"])
    if not etape.etape_modele.controle_requis:
        evenements.append(
            journal.ecrire(
                etape,
                auteur,
                VALIDEE,
                horodatage_appareil=instant,
                pour_le_compte_de=pour,
                commentaire=COMMENTAIRE_VALIDATION_IMPLICITE,
            )
        )
        etape.date_validation = timezone.now()
        etape.save(update_fields=["date_validation"])
    else:
        publications.a_controler(etape, auteur)
    return evenements, True


@transaction.atomic
def bloquer(
    auteur: Any,
    id_etape: Any,
    code_motif: str,
    *,
    commentaire: str | None = None,
    id_article: Any = None,
    uuid: UUID | None = None,
    horodatage_appareil: datetime | None = None,
) -> tuple[EvenementExecution, bool]:
    """EF-AVA-05, RG-A10 : un motif « manque de matériel » référence l'article."""
    deja = _deja_recu(uuid)
    if deja:
        return deja[0], False
    etape = acces.etape_autorisee(auteur, id_etape, "etapes", "MODIFIER", verrouiller=True)
    if etape.statut not in (A_FAIRE, EN_COURS):
        raise _transition_impossible(etape, "bloquer")
    motif = (
        selecteurs_referentiels.motifs_blocage().filter(code_motif=code_motif, actif=True).first()
    )
    if motif is None:
        raise donnee_invalide("code_motif", "Ce motif de blocage n'existe pas.")
    article = None
    if id_article:
        article = selecteurs_referentiels.articles().filter(id_article=id_article).first()
        if article is None:
            raise donnee_invalide("article_id_article", "Cet article n'existe pas.")
    if motif.requiert_article and article is None:
        raise donnee_invalide("article_id_article", "Indiquez l'article qui manque.")
    pour = pour_le_compte_de(auteur, etape)
    evenement = journal.ecrire(
        etape,
        auteur,
        BLOQUEE,
        uuid=uuid,
        horodatage_appareil=horodatage_appareil,
        pour_le_compte_de=pour,
        motif_blocage=motif,
        article=article,
        commentaire=commentaire,
    )
    publications.bloquee(etape, auteur, motif.libelle, article)
    return evenement, True


@transaction.atomic
def lever_blocage(
    auteur: Any, id_etape: Any, *, commentaire: str | None = None, uuid: UUID | None = None
) -> tuple[EvenementExecution, bool]:
    """ET-1 « blocage levé » : l'étape reprend (en cours si elle est affectée)."""
    deja = _deja_recu(uuid)
    if deja:
        return deja[0], False
    etape = acces.etape_autorisee(auteur, id_etape, "etapes", "MODIFIER", verrouiller=True)
    if etape.statut != BLOQUEE:
        raise _transition_impossible(etape, "débloquer")
    pour = pour_le_compte_de(auteur, etape)
    reprise = EN_COURS if fiches.technicien_actuel(etape) is not None else A_FAIRE
    evenement = journal.ecrire(
        etape, auteur, reprise, uuid=uuid, pour_le_compte_de=pour, commentaire=commentaire
    )
    return evenement, True


def _declaration(etape: EtapeTravaux) -> EvenementExecution | None:
    return (
        EvenementExecution.objects.filter(etape_travaux=etape, statut_apres=TERMINEE_DECLAREE)
        .order_by("-horodatage_serveur")
        .first()
    )


@transaction.atomic
def decider(
    valideur: Any,
    id_etape: Any,
    decision: str,
    motif: str | None,
    uuid: UUID | None = None,
) -> tuple[EvenementExecution, bool]:
    """EF-AVA-06, RG-A4 : valider ou rejeter (avec motif) une étape à contrôle."""
    deja = _deja_recu(uuid)
    if deja:
        return deja[0], False
    etape = acces.etape_autorisee(valideur, id_etape, "etapes", "VALIDER", verrouiller=True)
    if etape.statut != TERMINEE_DECLAREE or not etape.etape_modele.controle_requis:
        raise conflit("DECISION_IMPOSSIBLE", "Cette étape n'attend pas de contrôle.")
    declaration = _declaration(etape)
    concernes = (
        {declaration.utilisateur_id, declaration.pour_le_compte_de_id} if declaration else set()
    )
    if valideur.pk in concernes:
        raise ErreurApi(
            statut=403,
            motif="SEPARATION_DES_TACHES",
            message="Vous avez déclaré cette étape : une autre personne doit la contrôler.",
        )
    if decision == DECISION_REFUSE:
        if not motif:
            raise donnee_invalide("motif", "Indiquez le motif du rejet.")
        rejet = journal.ecrire(etape, valideur, EN_COURS, uuid=uuid, commentaire=motif)
        declarant = declaration.utilisateur if declaration else None
        publications.rejetee(etape, valideur, declarant, motif)
        return rejet, True
    evenement = journal.ecrire(etape, valideur, VALIDEE, uuid=uuid, commentaire=motif)
    etape.date_validation = timezone.now()
    etape.save(update_fields=["date_validation"])
    return evenement, True
