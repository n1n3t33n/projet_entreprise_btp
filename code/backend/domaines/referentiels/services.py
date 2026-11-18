"""Écritures du domaine « référentiels et catalogue » (EF-REF-03 à 06,
EF-REF-08, EF-REF-09 ; UC-3).

Le cœur métier est le cycle des versions de gamme (EF-REF-09 « publier une
version de gamme de travaux ») :
  * on ne modifie jamais une gamme publiée : on en crée une nouvelle version,
    en brouillon, copie de la précédente ;
  * seules les étapes d'un BROUILLON se modifient ;
  * publier un brouillon le rend ACTIVE et archive la version active du même
    type de logement : un type n'a jamais deux gammes actives ;
  * une gamme active peut être archivée sans remplaçante.
Les codes d'étape sont uniques sur tout le catalogue (``uq_etape_modele_code``,
MPD-3) : chaque version préfixe donc les codes de ses étapes (I-36).
"""

from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone

from domaines.identite.services import audit
from domaines.referentiels import selecteurs
from domaines.referentiels.constantes import (
    STATUT_GAMME_ACTIVE,
    STATUT_GAMME_ARCHIVEE,
    STATUT_GAMME_BROUILLON,
)
from domaines.referentiels.models import EtapeModele, Gamme
from socle import importation
from socle.api_outils import conflit, donnee_invalide
from socle.api_outils import enregistrer as enregistrer  # utilisé par les vues
from socle.erreurs import ErreurApi

SEPARATEUR_CODE = "~"

# Journal d'audit de l'import CSV (EF-AUT-08) : mêmes valeurs que la
# simulation du web.
AUDIT_IMPORT_CSV = "IMPORT_CSV"
OBJET_REFERENTIEL = "referentiel"


def code_de_version(code: str, version: int) -> str:
    """Code d'étape propre à une version : « EM-01 » devient « EM-01~V2 »
    (32 caractères au plus, comme au MPD)."""
    base = code.split(SEPARATEUR_CODE)[0]
    suffixe = f"{SEPARATEUR_CODE}V{version}"
    return base[: 32 - len(suffixe)] + suffixe


def _gamme(id_gamme: str) -> Gamme:
    gamme = Gamme.objects.select_for_update().filter(id_gamme=id_gamme).first()
    if gamme is None:
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Cette gamme est introuvable.")
    return gamme


@transaction.atomic
def nouvelle_version(id_gamme_source: str) -> Gamme:
    """Crée le brouillon de la version suivante, copie des étapes de la
    gamme source. Un seul brouillon à la fois par type de logement."""
    source = _gamme(id_gamme_source)
    if Gamme.objects.filter(
        type_logement_id=source.type_logement_id, statut=STATUT_GAMME_BROUILLON
    ).exists():
        raise conflit(
            "BROUILLON_EXISTANT",
            "Une nouvelle version est déjà en préparation pour ce type de logement.",
        )
    derniere = Gamme.objects.filter(type_logement_id=source.type_logement_id).aggregate(
        Max("version")
    )["version__max"]
    version = (derniere or 0) + 1
    brouillon = Gamme.objects.create(
        version=version,
        libelle=source.libelle,
        statut=STATUT_GAMME_BROUILLON,
        type_logement_id=source.type_logement_id,
    )
    EtapeModele.objects.bulk_create(
        EtapeModele(
            code=code_de_version(etape.code, version),
            libelle=etape.libelle,
            ordre=etape.ordre,
            poids=etape.poids,
            controle_requis=etape.controle_requis,
            gamme=brouillon,
            corps_etat_id=etape.corps_etat_id,
        )
        for etape in selecteurs.etapes_de_gamme(str(source.pk))
    )
    return brouillon


@transaction.atomic
def remplacer_etapes(id_gamme: str, etapes: list[dict[str, Any]]) -> list[EtapeModele]:
    """Remplace toutes les étapes d'un brouillon (l'écran envoie la liste
    complète, dans l'ordre)."""
    gamme = _gamme(id_gamme)
    if gamme.statut != STATUT_GAMME_BROUILLON:
        raise conflit(
            "GAMME_PUBLIEE",
            "Une gamme publiée ne se modifie plus : créez-en une nouvelle version.",
        )
    codes = [etape["code"] for etape in etapes]
    if len(codes) != len(set(codes)):
        raise donnee_invalide("etapes", "Deux étapes portent le même code.")
    EtapeModele.objects.filter(gamme=gamme).delete()
    try:
        crees = EtapeModele.objects.bulk_create(
            EtapeModele(
                code=etape["code"],
                libelle=etape["libelle"],
                ordre=etape["ordre"],
                poids=etape["poids"],
                controle_requis=etape["controle_requis"],
                gamme=gamme,
                corps_etat_id=etape["corps_etat_code_corps_etat"],
            )
            for etape in etapes
        )
    except IntegrityError as erreur:
        raise donnee_invalide(
            "etapes", "Un code d'étape est déjà utilisé par une autre gamme."
        ) from erreur
    return crees


@transaction.atomic
def publier(id_gamme: str) -> Gamme:
    """BROUILLON → ACTIVE ; l'ancienne version active du type passe ARCHIVEE."""
    gamme = _gamme(id_gamme)
    if gamme.statut != STATUT_GAMME_BROUILLON:
        raise conflit("GAMME_NON_BROUILLON", "Seul un brouillon peut être publié.")
    if not EtapeModele.objects.filter(gamme=gamme).exists():
        raise conflit("GAMME_VIDE", "Ajoutez au moins une étape avant de publier.")
    Gamme.objects.filter(
        type_logement_id=gamme.type_logement_id, statut=STATUT_GAMME_ACTIVE
    ).update(statut=STATUT_GAMME_ARCHIVEE)
    gamme.statut = STATUT_GAMME_ACTIVE
    gamme.date_activation = timezone.now()
    gamme.save(update_fields=["statut", "date_activation"])
    return gamme


@transaction.atomic
def archiver(id_gamme: str) -> Gamme:
    """ACTIVE → ARCHIVEE."""
    gamme = _gamme(id_gamme)
    if gamme.statut != STATUT_GAMME_ACTIVE:
        raise conflit("GAMME_NON_ACTIVE", "Seule une gamme active peut être archivée.")
    gamme.statut = STATUT_GAMME_ARCHIVEE
    gamme.save(update_fields=["statut"])
    return gamme


@transaction.atomic
def importer_csv(utilisateur: Any, cible: str, contenu: str, adresse_ip: str | None) -> int:
    """Second temps de l'import CSV (EF-ADM-02) : écrit les lignes valides et
    journalise l'opération dans la même transaction (EF-AUT-08). L'audit est
    écrit par le service du domaine identité (règle de modularité)."""
    nombre = importation.importer(cible, contenu)
    audit.consigner(utilisateur, AUDIT_IMPORT_CSV, OBJET_REFERENTIEL, adresse_ip, cible)
    return nombre
