"""Lectures du domaine « référentiels et catalogue »."""

from decimal import Decimal

from django.db.models import Count, DecimalField, QuerySet, Sum, Value
from django.db.models.functions import Coalesce

from domaines.referentiels.models import (
    Article,
    CategorieArticle,
    CorpsEtat,
    EtapeModele,
    Gamme,
    MotifBlocage,
    RegleValidation,
    TypeMouvement,
    UniteMesure,
)


def categories() -> QuerySet[CategorieArticle]:
    return CategorieArticle.objects.order_by("code_categorie")


def unites() -> QuerySet[UniteMesure]:
    return UniteMesure.objects.order_by("code_unite")


def articles() -> QuerySet[Article]:
    return Article.objects.select_related("unite_mesure", "categorie_article").order_by("code")


def corps_etat() -> QuerySet[CorpsEtat]:
    return CorpsEtat.objects.order_by("ordre", "code_corps_etat")


def gammes() -> QuerySet[Gamme]:
    """Gammes avec leur nombre d'étapes et leur poids total, calculés par la
    base en une seule requête (le web les affiche dans la liste)."""
    return (
        Gamme.objects.select_related("type_logement")
        .annotate(
            nombre_etapes=Count("etapes"),
            poids_total=Coalesce(
                Sum("etapes__poids"),
                Value(Decimal("0")),
                output_field=DecimalField(max_digits=14, decimal_places=3),
            ),
        )
        .order_by("type_logement_id", "-version")
    )


def etapes_de_gamme(id_gamme: str) -> QuerySet[EtapeModele]:
    return (
        EtapeModele.objects.select_related("corps_etat").filter(gamme_id=id_gamme).order_by("ordre")
    )


def types_mouvement() -> QuerySet[TypeMouvement]:
    return TypeMouvement.objects.order_by("code_type_mouvement")


def motifs_blocage() -> QuerySet[MotifBlocage]:
    return MotifBlocage.objects.order_by("code_motif")


def regles() -> QuerySet[RegleValidation]:
    return RegleValidation.objects.order_by("type_evenement", "champ_teste")
