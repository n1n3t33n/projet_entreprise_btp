"""Lecture des équipes (EF-REF-06) : qui encadre qui."""

from typing import Any

from django.db.models import Q
from django.utils import timezone

from domaines.identite.models import MembreEquipe


def chefs_de(utilisateur: Any) -> set[Any]:
    """Identifiants des chefs des équipes actives dont l'utilisateur est
    membre aujourd'hui (RG-A3, RG-A9 : le chef d'équipe peut déclarer pour
    ses équipiers)."""
    aujourd_hui = timezone.localdate()
    actives = Q(date_debut__lte=aujourd_hui) & (
        Q(date_fin__isnull=True) | Q(date_fin__gte=aujourd_hui)
    )
    equipes = MembreEquipe.objects.filter(actives, utilisateur=utilisateur).values("equipe_id")
    return set(
        MembreEquipe.objects.filter(actives, equipe_id__in=equipes, est_chef_equipe=True)
        .exclude(utilisateur=utilisateur)
        .values_list("utilisateur_id", flat=True)
    )
