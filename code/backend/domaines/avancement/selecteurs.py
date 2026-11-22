"""Lectures du domaine « avancement ».

Les étapes sont annotées, en une requête, de l'auteur de leur dernière
déclaration (colonne « déclarée par » du web). Le retard (RG-A8) se calcule
à la lecture : date prévue dépassée et étape ni déclarée ni validée.
"""

from datetime import date
from typing import Any
from uuid import UUID

from django.db.models import CharField, OuterRef, QuerySet, Subquery, Value
from django.db.models.functions import Concat

from domaines.avancement.constantes import STATUTS_TERMINES, TERMINEE_DECLAREE
from domaines.avancement.models import EtapeTravaux, EvenementExecution, FicheRoute


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
