"""Lecture des périmètres (EF-AUT-02) : ce qu'un périmètre couvre."""

from collections.abc import Iterable
from uuid import UUID

from domaines.identite.models import Perimetre


def portees(ids_perimetres: Iterable[UUID]) -> list[tuple[UUID | None, UUID | None]]:
    """(chantier, magasin) couverts par chaque périmètre. Un périmètre de
    chantier couvre tous les magasins de ce chantier ; un périmètre de
    magasin, ce seul magasin (MPD-1 ``perimetre``)."""
    return list(
        Perimetre.objects.filter(id_perimetre__in=list(ids_perimetres)).values_list(
            "chantier_id", "magasin_id"
        )
    )
