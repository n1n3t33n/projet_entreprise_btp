"""Lectures du domaine « avancement ».

Les étapes sont annotées, en une requête, de l'auteur de leur dernière
déclaration (colonne « déclarée par » du web). Le retard (RG-A8) se calcule
à la lecture : date prévue dépassée et étape ni déclarée ni validée.
"""

from datetime import date
from typing import Any
from uuid import UUID

from django.db.models import CharField, Count, OuterRef, Q, QuerySet, Subquery, Value
from django.db.models.functions import Concat

from domaines.avancement.constantes import (
    BLOQUEE,
    STATUTS_TERMINES,
    TERMINEE_DECLAREE,
    VALIDEE,
)
from domaines.avancement.models import (
    AvancementAgrege,
    EtapeTravaux,
    EvenementExecution,
    FicheRoute,
)
from socle.indicateurs import bornes


def _derniere_declaration() -> QuerySet[EvenementExecution]:
    return EvenementExecution.objects.filter(
        etape_travaux=OuterRef("pk"), statut_apres=TERMINEE_DECLAREE
    ).order_by("-horodatage_serveur")


def etapes(chantiers: set[UUID] | None = None) -> QuerySet[EtapeTravaux]:
    """Étapes annotées ; ``chantiers`` : couverture de l'utilisateur."""
    requete = EtapeTravaux.objects.select_related(
        "logement__zone", "logement__type_logement", "etape_modele__corps_etat"
    ).annotate(
        id_auteur_declaration=Subquery(_derniere_declaration().values("utilisateur_id")[:1]),
        nom_auteur_declaration=Subquery(
            _derniere_declaration()
            .annotate(
                nom=Concat(
                    "utilisateur__prenom",
                    Value(" "),
                    "utilisateur__nom",
                    output_field=CharField(),
                )
            )
            .values("nom")[:1]
        ),
    )
    if chantiers is not None:
        requete = requete.filter(logement__zone__chantier_id__in=chantiers)
    return requete.order_by("logement__numero", "etape_modele__ordre")


def etapes_du_logement(id_logement: Any) -> QuerySet[EtapeTravaux]:
    return etapes().filter(logement_id=id_logement)


def en_retard(etape: EtapeTravaux, aujourd_hui: date) -> bool:
    """RG-A8 : date prévue dépassée et étape pas encore terminée."""
    return (
        etape.date_prevue is not None
        and etape.date_prevue < aujourd_hui
        and etape.statut not in STATUTS_TERMINES
    )


def evenements_de_l_etape(id_etape: Any) -> QuerySet[EvenementExecution]:
    """Historique complet d'une étape (EF-AVA-10), du plus ancien au plus récent."""
    return (
        EvenementExecution.objects.filter(etape_travaux_id=id_etape)
        .select_related("utilisateur", "pour_le_compte_de")
        .order_by("horodatage_serveur")
    )


def fiches(id_technicien: Any = None) -> QuerySet[FicheRoute]:
    requete = FicheRoute.objects.select_related("utilisateur")
    if id_technicien is not None:
        requete = requete.filter(utilisateur_id=id_technicien)
    return requete.order_by("-date_debut")


# --- Pilotage de l'avancement (RG-A6, RG-A8, EF-DSH) ---------------------------------
def filtre_retard(aujourd_hui: date) -> Q:
    """RG-A8 exprimé en requête : date prévue dépassée, étape pas terminée."""
    return Q(date_prevue__lt=aujourd_hui) & ~Q(statut__in=STATUTS_TERMINES)


def comptes_par(
    cle: str, etapes_qs: QuerySet[EtapeTravaux], aujourd_hui: date
) -> dict[Any, dict[str, int]]:
    """Nombres d'étapes, validées, bloquées et en retard, groupés par ``cle``
    (ex. ``logement_id``), en une requête."""
    lignes = (
        etapes_qs.order_by()
        .values(cle)
        .annotate(
            nombre_etapes=Count("pk"),
            nombre_validees=Count("pk", filter=Q(statut=VALIDEE)),
            nombre_bloquees=Count("pk", filter=Q(statut=BLOQUEE)),
            nombre_en_retard=Count("pk", filter=filtre_retard(aujourd_hui)),
        )
    )
    return {ligne.pop(cle): ligne for ligne in lignes}


def agregats(portee: str) -> dict[str, AvancementAgrege]:
    """Agrégats d'une portée, par cible."""
    return {a.id_cible: a for a in AvancementAgrege.objects.filter(portee=portee)}


def _dernier_blocage() -> QuerySet[EvenementExecution]:
    return EvenementExecution.objects.filter(
        etape_travaux=OuterRef("pk"), statut_apres=BLOQUEE
    ).order_by("-horodatage_serveur")


def alertes(chantiers: set[UUID] | None, aujourd_hui: date) -> QuerySet[EtapeTravaux]:
    """Étapes en retard ou bloquées (RG-A8, EF-AVA-09), avec le motif et le
    commentaire de leur dernier blocage."""
    return (
        etapes(chantiers)
        .filter(Q(statut=BLOQUEE) | filtre_retard(aujourd_hui))
        .annotate(
            code_motif_blocage=Subquery(_dernier_blocage().values("motif_blocage_id")[:1]),
            libelle_motif_blocage=Subquery(_dernier_blocage().values("motif_blocage__libelle")[:1]),
            commentaire_blocage=Subquery(_dernier_blocage().values("commentaire")[:1]),
        )
        .order_by("date_prevue", "logement__numero")
    )


# --- Journal d'exécution (EF-DSH-03, RG-A5 : qui, quoi, quand) -----------------------
def journal(chantiers: set[UUID] | None, **filtres: Any) -> QuerySet[EvenementExecution]:
    """Événements des chantiers couverts, les plus récents d'abord. Filtres :
    ``auteur``, ``zone``, ``statut`` (statut après), ``depuis`` et ``jusqua``
    (jours, sur l'horodatage serveur, qui fait foi)."""
    requete = EvenementExecution.objects.select_related(
        "utilisateur",
        "motif_blocage",
        "etape_travaux__logement__zone",
        "etape_travaux__etape_modele__corps_etat",
    )
    if chantiers is not None:
        requete = requete.filter(etape_travaux__logement__zone__chantier_id__in=chantiers)
    if filtres.get("auteur"):
        requete = requete.filter(utilisateur_id=filtres["auteur"])
    if filtres.get("zone"):
        requete = requete.filter(etape_travaux__logement__zone_id=filtres["zone"])
    if filtres.get("statut"):
        requete = requete.filter(statut_apres=filtres["statut"])
    if filtres.get("depuis"):
        requete = requete.filter(
            horodatage_serveur__gte=bornes(filtres["depuis"], filtres["depuis"])[0]
        )
    if filtres.get("jusqua"):
        requete = requete.filter(
            horodatage_serveur__lt=bornes(filtres["jusqua"], filtres["jusqua"])[1]
        )
    return requete.order_by("-horodatage_serveur")


def intervenants(chantiers: set[UUID] | None) -> list[dict[str, Any]]:
    """Auteurs d'au moins un événement, triés par nom (filtre du journal)."""
    auteurs = (
        journal(chantiers)
        .order_by()
        .values("utilisateur_id")
        .annotate(
            nom=Concat(
                "utilisateur__prenom", Value(" "), "utilisateur__nom", output_field=CharField()
            )
        )
        .distinct()
    )
    return sorted(
        ({"id_utilisateur": a["utilisateur_id"], "nom": a["nom"]} for a in auteurs),
        key=lambda a: str(a["nom"]).lower(),
    )
