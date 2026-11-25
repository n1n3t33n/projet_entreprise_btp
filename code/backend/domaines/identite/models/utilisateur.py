"""Modèle utilisateur personnalisé, branché sur la table ``utilisateur`` (MPD-1).

CL-1 ``Utilisateur { idUtilisateur, identifiant, nom, prenom, fonction,
statut, dateCreation }``. Deux écarts au MPD, validés (arbitrage Q7) et à
remonter en v0.2 de la modélisation :
  * Q7-1 : colonne ``mot_de_passe varchar(128)`` — SQ-5 étape 2 et EF-AUT-04
    exigent une connexion par mot de passe, que le MPD ne stockait pas (I-14).
    Le mot de passe n'est jamais stocké en clair : Django y range une
    empreinte (algorithme, sel, itérations).
  * Q7-2 : ``UNIQUE uq_utilisateur_identifiant`` — l'identifiant sert à se
    connecter, il doit désigner un seul compte.

Le framework de permissions de Django n'est pas utilisé : ``is_staff`` et
``has_perm`` sont CALCULÉS à partir de la matrice des droits (droit_accorde),
jamais stockés (arbitrage Q5).
"""

import uuid
from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import Q
from django.utils import timezone

from domaines.identite.constantes import (
    ACTION_LIRE,
    ACTION_MODIFIER,
    MODULE_TECHNIQUE,
    STATUT_UTILISATEUR_ACTIF,
    STATUTS_UTILISATEUR,
)
from domaines.organisation.models import Acquereur


def normaliser_identifiant(identifiant: str) -> str:
    """Identifiant sans espaces superflus et en minuscules : « Y.Bamba » et
    « y.bamba » désignent le même compte."""
    return identifiant.strip().lower()


class GestionnaireUtilisateurs(BaseUserManager["Utilisateur"]):
    """Création des comptes avec un mot de passe toujours haché."""

    use_in_migrations = True

    def create_user(
        self, identifiant: str, password: str | None = None, **champs: Any
    ) -> "Utilisateur":
        utilisateur = self.model(identifiant=normaliser_identifiant(identifiant), **champs)
        if password:
            utilisateur.set_password(password)
        else:
            # Compte sans mot de passe utilisable (membre d'équipe sans accès).
            utilisateur.set_unusable_password()
        utilisateur.save(using=self._db)
        return utilisateur


class Utilisateur(AbstractBaseUser):
    """Compte nominatif (EF-AUT-01), unique porteur d'identité du système."""

    id_utilisateur = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identifiant = models.CharField(max_length=120)
    nom = models.CharField(max_length=120)
    prenom = models.CharField(max_length=120)
    fonction = models.CharField(max_length=120, blank=True, default="")
    statut = models.CharField(max_length=32, default=STATUT_UTILISATEUR_ACTIF)
    date_creation = models.DateTimeField(default=timezone.now)
    # Écart Q-AY (I-20, dette v0.2) : le MPD ne relie aucun compte à un
    # acquéreur. Le lien porte la portée de l'espace acquéreur (RG-D10 :
    # « l'acquéreur n'accède qu'à son logement »). Il est posé côté compte
    # pour que l'identité continue de dépendre de l'organisation, jamais
    # l'inverse.
    acquereur = models.ForeignKey(
        Acquereur,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="acquereur_id_acquereur",
        db_index=False,
        related_name="comptes",
    )

    # Écart Q7-1 : colonne « mot_de_passe » (nom français, comme le MPD), qui
    # remplace la colonne « password » d'AbstractBaseUser.
    password = models.CharField("mot de passe", max_length=128, db_column="mot_de_passe")
    # Aucune colonne « last_login » : absente du MPD, et la traçabilité des
    # connexions est assurée par journal_audit (RG-D9).
    last_login = None  # type: ignore[assignment]

    objects = GestionnaireUtilisateurs()

    USERNAME_FIELD = "identifiant"
    REQUIRED_FIELDS = ["nom", "prenom"]
    # Aucun « super-utilisateur » : tout droit passe par la matrice.
    is_superuser = False

    class Meta:
        db_table = "utilisateur"
        verbose_name = "utilisateur"
        constraints = [
            # Écart Q7-2.
            models.UniqueConstraint(fields=["identifiant"], name="uq_utilisateur_identifiant"),
            # Écart Q-AY : un acquéreur a au plus un compte.
            models.UniqueConstraint(
                fields=["acquereur"], name="uq_utilisateur_acquereur_id_acquereur"
            ),
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_UTILISATEUR), name="ck_utilisateur_statut"
            ),
        ]

    def __str__(self) -> str:
        return self.nom_complet

    @property
    def nom_complet(self) -> str:
        """« Prénom Nom », tel que l'affichent les maquettes (Écran 1, A1-A5)."""
        return f"{self.prenom} {self.nom}".strip()

    # AbstractBaseUser déclare « is_active = True » comme simple attribut ; on
    # le remplace volontairement par un calcul depuis le statut du MPD.
    @property
    def is_active(self) -> bool:  # type: ignore[override]
        """Un compte INACTIF est refusé partout, immédiatement (RG-D5)."""
        return self.statut == STATUT_UTILISATEUR_ACTIF

    @property
    def is_staff(self) -> bool:
        """Accès à l'administration Django : droit « technique / admin / LIRE »
        de la matrice (arbitrage Q5), jamais un booléen stocké."""
        from domaines.identite.services.droits import a_le_droit

        return self.is_active and a_le_droit(self, MODULE_TECHNIQUE, "admin", ACTION_LIRE)

    def has_perm(self, perm: str, obj: object = None) -> bool:
        """Traduit une permission de l'admin Django vers la matrice : consulter
        demande « admin / LIRE », ajouter, modifier ou supprimer demande
        « admin / MODIFIER ». Les ModelAdmin en lecture seule refusent de
        toute façon les écritures."""
        from domaines.identite.services.droits import a_le_droit

        if not self.is_active:
            return False
        nom_action = perm.split(".", 1)[-1].split("_", 1)[0]
        action = ACTION_LIRE if nom_action == "view" else ACTION_MODIFIER
        return a_le_droit(self, MODULE_TECHNIQUE, "admin", action)

    def has_perms(self, perm_list: Any, obj: object = None) -> bool:
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label: str) -> bool:
        return self.is_staff
