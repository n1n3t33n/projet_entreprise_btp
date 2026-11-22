"""Lectures du domaine « référentiels et catalogue »."""

from decimal import Decimal
from typing import Any

from django.db.models import Count, DecimalField, QuerySet, Sum, Value
from django.db.models.functions import Coalesce

from domaines.referentiels.models import (
    Article,
    CategorieArticle,
    Conditionnement,
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


def type_mouvement(code: str) -> TypeMouvement | None:
    return TypeMouvement.objects.filter(code_type_mouvement=code).first()


def facteur_conversion(id_article: Any, code_unite: str) -> Decimal | None:
    """RG-S1 : facteur qui ramène une unité de conditionnement à l'unité de
    base de l'article (1 sac = 50 kg). ``None`` si l'unité n'est ni l'unité de
    base ni un conditionnement déclaré de l'article."""
    article = Article.objects.filter(id_article=id_article).first()
    if article is None:
        return None
    if article.unite_mesure_id == code_unite:
        return Decimal("1")
    conditionnement = Conditionnement.objects.filter(
        article_id=id_article, unite_mesure_id=code_unite
    ).first()
    return conditionnement.facteur_conversion if conditionnement else None


def regles_de(type_evenement: str) -> QuerySet[RegleValidation]:
    """Règles de validation d'un type d'événement (RG-S6, RG-S9)."""
    return RegleValidation.objects.filter(type_evenement=type_evenement).order_by("champ_teste")


def gamme_active(code_type_logement: str) -> Gamme | None:
    """La version ACTIVE de la gamme d'un type de logement (au plus une)."""
    return Gamme.objects.filter(type_logement_id=code_type_logement, statut="ACTIVE").first()


def etapes_modele_actives(code_type_logement: str) -> QuerySet[EtapeModele]:
    """Étapes de la gamme active d'un type de logement, dans leur ordre."""
    return EtapeModele.objects.filter(
        gamme__type_logement_id=code_type_logement, gamme__statut="ACTIVE"
    ).order_by("ordre")
