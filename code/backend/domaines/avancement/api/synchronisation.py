"""Événements de l'avancement rejouables par lot (EF-SYN-02, SQ-2).

La charge utile porte ``id_etape`` et le corps de la route REST
correspondante (Q-AE) ; l'``uuid`` de l'événement devient celui de
l'événement d'exécution (idempotence, 6.4) :
  * ``DECLARATION_ETAPE`` — ``POST /etapes/{id}/declaration`` ;
  * ``BLOCAGE_ETAPE``     — ``POST /etapes/{id}/blocage`` ;
  * ``LEVEE_BLOCAGE``     — ``POST /etapes/{id}/levee-blocage`` ;
  * ``DECISION_ETAPE``    — ``POST /etapes/{id}/validation``.
Le type générique ``EVENEMENT_ETAPE`` du mobile est remplacé par ces quatre
types explicites (F-14). Déclarés par ``avancement/apps.py``.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from domaines.avancement.api import serialiseurs as s
from domaines.avancement.services import declarations
from socle.synchronisation import Traitement, TypeEvenement


def _valider(classe: Any, charge: dict[str, Any], uuid: UUID) -> dict[str, Any]:
    entree = classe(data={**charge, "uuid": str(uuid)})
    entree.is_valid(raise_exception=True)
    return dict(entree.validated_data)


def _horodatage(donnees: dict[str, Any], horodatage: datetime | None) -> datetime | None:
    return donnees.get("horodatage_appareil") or horodatage


def declaration(
    auteur: Any, uuid: UUID, horodatage: datetime | None, charge: dict[str, Any]
) -> Traitement:
    donnees = _valider(s.DeclarationEntreeSerializer, charge, uuid)
    _evenements, cree = declarations.declarer_terminee(
        auteur,
        charge.get("id_etape"),
        uuid=uuid,
        horodatage_appareil=_horodatage(donnees, horodatage),
        commentaire=donnees.get("commentaire"),
    )
    return Traitement(cree=cree)


def blocage(
    auteur: Any, uuid: UUID, horodatage: datetime | None, charge: dict[str, Any]
) -> Traitement:
    donnees = _valider(s.BlocageEntreeSerializer, charge, uuid)
    _evenement, cree = declarations.bloquer(
        auteur,
        charge.get("id_etape"),
        donnees["code_motif"],
        commentaire=donnees.get("commentaire"),
        id_article=donnees.get("article_id_article"),
        uuid=uuid,
        horodatage_appareil=_horodatage(donnees, horodatage),
    )
    return Traitement(cree=cree)


def levee(
    auteur: Any, uuid: UUID, horodatage: datetime | None, charge: dict[str, Any]
) -> Traitement:
    donnees = _valider(s.LeveeEntreeSerializer, charge, uuid)
    _evenement, cree = declarations.lever_blocage(
        auteur, charge.get("id_etape"), commentaire=donnees.get("commentaire"), uuid=uuid
    )
    return Traitement(cree=cree)


def decision(
    auteur: Any, uuid: UUID, horodatage: datetime | None, charge: dict[str, Any]
) -> Traitement:
    donnees = _valider(s.DecisionEtapeEntreeSerializer, charge, uuid)
    _evenement, cree = declarations.decider(
        auteur, charge.get("id_etape"), donnees["decision"], donnees.get("motif"), uuid
    )
    return Traitement(cree=cree)


TYPES = (
    TypeEvenement("DECLARATION_ETAPE", declaration, "etapes", "MODIFIER"),
    TypeEvenement("BLOCAGE_ETAPE", blocage, "etapes", "MODIFIER"),
    TypeEvenement("LEVEE_BLOCAGE", levee, "etapes", "MODIFIER"),
    TypeEvenement("DECISION_ETAPE", decision, "etapes", "VALIDER"),
)
