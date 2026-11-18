"""Lectures du domaine « organisation du chantier », pour les vues et pour les
autres domaines (qui ne requêtent jamais ces tables directement)."""

from django.db.models import Prefetch, QuerySet

from domaines.organisation.models import (
    Chantier,
    Logement,
    Magasin,
    ParametreChantier,
    TypeLogement,
    Zone,
)


def chantiers() -> QuerySet[Chantier]:
    return Chantier.objects.order_by("nom")


def chantier_par_code(code: str) -> Chantier | None:
    return Chantier.objects.filter(code=code).first()


def chantier_unique() -> Chantier | None:
    """Le chantier du programme quand il n'y en a qu'un (pilote) : sert de
    valeur par défaut aux écrans qui ne précisent pas le chantier (I-35)."""
    premiers = list(Chantier.objects.order_by("code")[:2])
    return premiers[0] if len(premiers) == 1 else None


def arborescence(id_chantier: str) -> Chantier | None:
    """Chantier avec ses zones et leurs logements, en trois requêtes."""
    logements = Logement.objects.order_by("numero")
    zones = Zone.objects.order_by("code").prefetch_related(
        Prefetch("logements", queryset=logements)
    )
    return (
        Chantier.objects.prefetch_related(Prefetch("zones", queryset=zones))
        .filter(id_chantier=id_chantier)
        .first()
    )


def magasins() -> QuerySet[Magasin]:
    return Magasin.objects.select_related("chantier").order_by("code")


def magasin_par_code(code: str) -> Magasin | None:
    return Magasin.objects.select_related("chantier").filter(code=code).first()


def zones() -> QuerySet[Zone]:
    return Zone.objects.select_related("chantier").order_by("code")


def logements() -> QuerySet[Logement]:
    return Logement.objects.select_related("zone", "type_logement").order_by("numero")


def logements_du_chantier(id_chantier: str) -> QuerySet[Logement]:
    """Logements de destination d'une sortie de stock (écran Stock du web)."""
    return logements().filter(zone__chantier_id=id_chantier)


def types_logement() -> QuerySet[TypeLogement]:
    return TypeLogement.objects.order_by("code_type")


def parametres(id_chantier: str | None = None) -> QuerySet[ParametreChantier]:
    resultat = ParametreChantier.objects.select_related("chantier").order_by("cle")
    return resultat.filter(chantier_id=id_chantier) if id_chantier else resultat


def valeur_parametre(id_chantier: str, cle: str) -> ParametreChantier | None:
    """Paramètre d'un chantier par sa clé (ex. delai_relance_validation_h,
    lu par la relance d'ET-2 en B3)."""
    return ParametreChantier.objects.filter(chantier_id=id_chantier, cle=cle).first()
