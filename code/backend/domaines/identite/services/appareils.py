"""Enrôlement et révocation des appareils (ET-4, SQ-5, EF-AUT-06, RG-D5).

ET-4 : « appareil non enregistré » → enrôlé à la première connexion en ligne
→ révoqué (par l'administrateur, ou parce que le compte est désactivé). Un
appareil révoqué ne revient jamais : il faudrait un nouvel enrôlement par un
nouvel identifiant d'installation, décision de l'administrateur.
"""

from dataclasses import dataclass
from typing import Any

from django.db import transaction

from domaines.identite.constantes import (
    AUDIT_ENROLEMENT_APPAREIL,
    AUDIT_REVOCATION_APPAREIL,
    OBJET_APPAREIL,
    STATUT_APPAREIL_ACTIF,
    STATUT_APPAREIL_REVOQUE,
)
from domaines.identite.models import Appareil
from domaines.identite.services import audit
from socle.erreurs import ErreurApi


@dataclass(frozen=True)
class DonneesAppareil:
    """Bloc « appareil » facultatif de la connexion (SQ-5 étape 3)."""

    empreinte_materiel: str
    plateforme: str
    version_application: str


def enroler(utilisateur: Any, donnees: DonneesAppareil, adresse_ip: str | None) -> Appareil:
    """Rend l'appareil de l'utilisateur pour cette empreinte, en le créant à
    la première connexion (SQ-5 étape 4). Un appareil révoqué est refusé."""
    appareil = Appareil.objects.filter(
        utilisateur=utilisateur, empreinte_materiel=donnees.empreinte_materiel
    ).first()
    if appareil is not None and appareil.statut == STATUT_APPAREIL_REVOQUE:
        raise ErreurApi(
            statut=403,
            motif="APPAREIL_REVOQUE",
            message="Cet appareil n'a plus accès à ChantierSync. Adressez-vous à l'administrateur.",
        )
    if appareil is None:
        appareil = Appareil.objects.create(
            utilisateur=utilisateur,
            empreinte_materiel=donnees.empreinte_materiel,
            plateforme=donnees.plateforme,
            version_application=donnees.version_application,
            statut=STATUT_APPAREIL_ACTIF,
        )
        audit.consigner(utilisateur, AUDIT_ENROLEMENT_APPAREIL, OBJET_APPAREIL, adresse_ip)
        return appareil
    appareil.plateforme = donnees.plateforme
    appareil.version_application = donnees.version_application
    appareil.statut = STATUT_APPAREIL_ACTIF
    appareil.save(update_fields=["plateforme", "version_application", "statut"])
    return appareil


def revoquer(auteur: Any, id_appareil: str, adresse_ip: str | None) -> Appareil:
    """Révoque un appareil (EF-AUT-06, SQ-5 étape 12 : « blocage serveur
    immédiat et journalisation »). Idempotent : révoquer deux fois ne crée
    qu'une entrée d'audit."""
    with transaction.atomic():
        appareil = (
            Appareil.objects.select_for_update()
            .select_related("utilisateur")
            .filter(id_appareil=id_appareil)
            .first()
        )
        if appareil is None:
            raise ErreurApi(
                statut=404, motif="INTROUVABLE", message="Cet appareil est introuvable."
            )
        if appareil.statut == STATUT_APPAREIL_REVOQUE:
            return appareil
        appareil.statut = STATUT_APPAREIL_REVOQUE
        appareil.save(update_fields=["statut"])
        audit.consigner(auteur, AUDIT_REVOCATION_APPAREIL, OBJET_APPAREIL, adresse_ip)
    return appareil


def revoquer_tous(auteur: Any, utilisateur: Any, adresse_ip: str | None) -> int:
    """ET-4 : un compte désactivé rend ses appareils révoqués."""
    nombre = 0
    for appareil in Appareil.objects.filter(utilisateur=utilisateur).exclude(
        statut=STATUT_APPAREIL_REVOQUE
    ):
        revoquer(auteur, str(appareil.id_appareil), adresse_ip)
        nombre += 1
    return nombre
