"""Lectures du domaine « organisation du chantier », pour les autres domaines
et pour les vues."""

from domaines.organisation.models import Chantier, Magasin


def chantier_par_code(code: str) -> Chantier | None:
    return Chantier.objects.filter(code=code).first()


def magasin_par_code(code: str) -> Magasin | None:
    return Magasin.objects.select_related("chantier").filter(code=code).first()
