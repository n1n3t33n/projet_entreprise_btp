"""Gestion des comptes nominatifs (EF-AUT-01, EF-AUT-02, EF-AUT-06 ; UC-4).

Le contrat du web (« Administration › Comptes ») gère UN rôle sur UN
périmètre par compte : l'« affectation principale ». Le modèle en permet
plusieurs (EF-AUT-02, incohérence I-28) ; ce service ne touche donc qu'à
l'affectation principale et laisse les autres intactes.

Mot de passe initial (arbitrage Q12) : saisi par l'administrateur à la
création, validé par les règles de robustesse (EF-AUT-04). Le changement au
premier accès est une exigence v0.2, hors B1.
"""

from dataclasses import dataclass
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from domaines.identite.constantes import (
    AUDIT_CREATION_COMPTE,
    AUDIT_DESACTIVATION_COMPTE,
    AUDIT_MODIFICATION_COMPTE,
    OBJET_UTILISATEUR,
    STATUT_UTILISATEUR_INACTIF,
)
from domaines.identite.models import AffectationRole, Perimetre, Role, Utilisateur
from domaines.identite.models.utilisateur import normaliser_identifiant
from domaines.identite.selecteurs.comptes import affectation_principale
from domaines.identite.services import audit
from domaines.identite.services.appareils import revoquer_tous
from socle.erreurs import ErreurApi


@dataclass(frozen=True)
class SaisieCompte:
    identifiant: str
    nom: str
    prenom: str
    fonction: str
    statut: str
    code_role: str
    id_perimetre: str
    mot_de_passe: str | None


def _invalide(champ: str, message: str) -> ErreurApi:
    return ErreurApi(
        statut=400,
        motif="DONNEES_INVALIDES",
        message="Certaines informations sont manquantes ou incorrectes.",
        details={champ: [message]},
    )


def _verifier_role_et_perimetre(saisie: SaisieCompte) -> tuple[Role, Perimetre]:
    role = Role.objects.filter(code_role=saisie.code_role, actif=True).first()
    if role is None:
        raise _invalide("role_code_role", "Ce rôle n'existe pas ou n'est plus actif.")
    perimetre = Perimetre.objects.filter(id_perimetre=saisie.id_perimetre).first()
    if perimetre is None:
        raise _invalide("perimetre_id_perimetre", "Ce périmètre n'existe pas.")
    return role, perimetre


def _appliquer_mot_de_passe(utilisateur: Utilisateur, mot_de_passe: str) -> None:
    try:
        validate_password(mot_de_passe, user=utilisateur)
    except ValidationError as erreur:
        raise ErreurApi(
            statut=400,
            motif="DONNEES_INVALIDES",
            message="Le mot de passe n'est pas assez robuste.",
            details={"mot_de_passe": list(erreur.messages)},
        ) from erreur
    utilisateur.set_password(mot_de_passe)


def creer(auteur: Any, saisie: SaisieCompte, adresse_ip: str | None) -> Utilisateur:
    """Crée un compte avec son affectation principale et son mot de passe."""
    if not saisie.mot_de_passe:
        raise _invalide("mot_de_passe", "Saisissez un mot de passe initial.")
    identifiant = normaliser_identifiant(saisie.identifiant)
    if Utilisateur.objects.filter(identifiant=identifiant).exists():
        raise _invalide("identifiant", "Cet identifiant est déjà utilisé.")
    role, perimetre = _verifier_role_et_perimetre(saisie)
    with transaction.atomic():
        utilisateur = Utilisateur(
            identifiant=identifiant,
            nom=saisie.nom,
            prenom=saisie.prenom,
            fonction=saisie.fonction,
            statut=saisie.statut,
        )
        _appliquer_mot_de_passe(utilisateur, saisie.mot_de_passe)
        utilisateur.save()
        AffectationRole.objects.create(role=role, perimetre=perimetre, utilisateur=utilisateur)
        audit.consigner(
            auteur, AUDIT_CREATION_COMPTE, OBJET_UTILISATEUR, adresse_ip, utilisateur.pk
        )
    return utilisateur


def _changer_affectation_principale(
    utilisateur: Utilisateur, role: Role, perimetre: Perimetre
) -> None:
    """Clôt l'affectation principale actuelle (fin = aujourd'hui, période
    demi-ouverte) et ouvre ou rouvre la nouvelle. La clé primaire
    (rôle, périmètre, utilisateur) ne connaît pas les dates : revenir à un
    couple déjà connu rouvre la ligne existante."""
    aujourd_hui = timezone.localdate()
    actuelle = affectation_principale(utilisateur)
    if actuelle is not None and (actuelle.role_id, actuelle.perimetre_id) == (
        role.code_role,
        perimetre.id_perimetre,
    ):
        return
    if actuelle is not None:
        AffectationRole.objects.filter(
            role_id=actuelle.role_id,
            perimetre_id=actuelle.perimetre_id,
            utilisateur=utilisateur,
        ).update(date_fin=aujourd_hui)
    AffectationRole.objects.update_or_create(
        role=role,
        perimetre=perimetre,
        utilisateur=utilisateur,
        defaults={"date_debut": aujourd_hui, "date_fin": None},
    )


def modifier(
    auteur: Any, id_utilisateur: str, saisie: SaisieCompte, adresse_ip: str | None
) -> Utilisateur:
    """Modifie un compte. Passer le statut à INACTIF désactive le compte :
    refus immédiat partout (RG-D5) et révocation de ses appareils (ET-4)."""
    utilisateur = Utilisateur.objects.filter(id_utilisateur=id_utilisateur).first()
    if utilisateur is None:
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Ce compte est introuvable.")
    identifiant = normaliser_identifiant(saisie.identifiant)
    if Utilisateur.objects.filter(identifiant=identifiant).exclude(pk=utilisateur.pk).exists():
        raise _invalide("identifiant", "Cet identifiant est déjà utilisé.")
    role, perimetre = _verifier_role_et_perimetre(saisie)
    desactivation = utilisateur.is_active and saisie.statut == STATUT_UTILISATEUR_INACTIF
    with transaction.atomic():
        utilisateur.identifiant = identifiant
        utilisateur.nom = saisie.nom
        utilisateur.prenom = saisie.prenom
        utilisateur.fonction = saisie.fonction
        utilisateur.statut = saisie.statut
        if saisie.mot_de_passe:
            _appliquer_mot_de_passe(utilisateur, saisie.mot_de_passe)
        utilisateur.save()
        _changer_affectation_principale(utilisateur, role, perimetre)
        audit.consigner(
            auteur,
            AUDIT_DESACTIVATION_COMPTE if desactivation else AUDIT_MODIFICATION_COMPTE,
            OBJET_UTILISATEUR,
            adresse_ip,
            utilisateur.pk,
        )
        if desactivation:
            revoquer_tous(auteur, utilisateur, adresse_ip)
    return utilisateur
