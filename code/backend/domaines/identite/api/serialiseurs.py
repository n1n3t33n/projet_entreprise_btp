"""Sérialiseurs du domaine identité : ils FIXENT LE CONTRAT d'API.

Chaque forme reprend exactement les DTO déjà consommés par le web
(``features/auth/api/dto.ts``, ``features/admin/api/*dto.ts``) et le mobile
(``dto_auth.dart``) : snake_case, énumérés en UPPER_SNAKE, horodatages ISO
8601 (rapport B0 § 3). Les champs nouveaux sont des AJOUTS (compatibles).

Rappel (arbitrage Q14) : ces sérialiseurs définissent le CONTRAT ; le schéma
de DONNÉES, lui, vient du MPD. On ne déduit jamais l'un de l'autre.
"""

from typing import Any

from rest_framework import serializers

from domaines.identite.constantes import STATUTS_UTILISATEUR
from domaines.identite.services import audit as service_audit
from domaines.identite.services.comptes import affectation_principale


# --- Erreur (format unique, socle/erreurs.py) -------------------------------
class ErreurSerializer(serializers.Serializer):  # type: ignore[type-arg]
    motif = serializers.CharField(help_text="Code stable, UPPER_SNAKE, destiné au programme.")
    message = serializers.CharField(help_text="Phrase en français destinée à l'utilisateur.")
    details = serializers.DictField(required=False)
    secondes_restantes = serializers.IntegerField(required=False)
    id_correlation = serializers.CharField(required=False)


# --- Utilisateur ------------------------------------------------------------
class UtilisateurSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``UtilisateurDto`` (web et mobile). ``role_code_role`` et
    ``perimetre_id_perimetre`` décrivent l'affectation principale."""

    id_utilisateur = serializers.UUIDField()
    identifiant = serializers.CharField()
    nom = serializers.CharField()
    prenom = serializers.CharField()
    fonction = serializers.CharField()
    statut = serializers.CharField()
    date_creation = serializers.DateTimeField()
    role_code_role = serializers.SerializerMethodField()
    perimetre_id_perimetre = serializers.SerializerMethodField()
    libelle_perimetre = serializers.SerializerMethodField()
    # Ajout compatible (fidelite-wireframes : chantier affiché à l'écran 1).
    libelle_chantier = serializers.SerializerMethodField()

    def _principale(self, obj: Any) -> Any:
        cache = self.context.setdefault("_principales", {})
        if obj.pk not in cache:
            cache[obj.pk] = affectation_principale(obj)
        return cache[obj.pk]

    def get_role_code_role(self, obj: Any) -> str | None:
        affectation = self._principale(obj)
        return affectation.role_id if affectation else None

    def get_perimetre_id_perimetre(self, obj: Any) -> str | None:
        affectation = self._principale(obj)
        return str(affectation.perimetre_id) if affectation else None

    def get_libelle_perimetre(self, obj: Any) -> str | None:
        affectation = self._principale(obj)
        return affectation.perimetre.libelle if affectation else None

    def get_libelle_chantier(self, obj: Any) -> str | None:
        affectation = self._principale(obj)
        if affectation is None:
            return None
        perimetre = affectation.perimetre
        if perimetre.chantier is not None:
            return str(perimetre.chantier.nom)
        if perimetre.magasin is not None:
            return str(perimetre.magasin.chantier.nom)
        return None


class AppareilSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``AppareilDto`` (web, Administration › Appareils)."""

    id_appareil = serializers.UUIDField()
    empreinte_materiel = serializers.CharField()
    plateforme = serializers.CharField()
    version_application = serializers.CharField()
    derniere_synchronisation = serializers.DateTimeField(allow_null=True)
    statut = serializers.CharField()
    utilisateur_id_utilisateur = serializers.UUIDField(source="utilisateur_id")
    identifiant_utilisateur = serializers.CharField(source="utilisateur.identifiant")
    nom_utilisateur = serializers.CharField(source="utilisateur.nom_complet")


class DroitEffectifSerializer(serializers.Serializer):  # type: ignore[type-arg]
    code_permission = serializers.CharField()
    module = serializers.CharField()
    ressource = serializers.CharField()
    action = serializers.CharField()
    portee = serializers.CharField()
    id_perimetre = serializers.UUIDField()
    libelle_perimetre = serializers.CharField()


# --- Connexion --------------------------------------------------------------
class AppareilConnexionSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Bloc facultatif envoyé par le mobile (SQ-5 étape 3)."""

    empreinte_materiel = serializers.CharField(max_length=120)
    plateforme = serializers.CharField(max_length=120)
    version_application = serializers.CharField(max_length=120)


class ConnexionEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    identifiant = serializers.CharField(max_length=120)
    mot_de_passe = serializers.CharField(max_length=256, trim_whitespace=False)
    appareil = AppareilConnexionSerializer(required=False)


class SessionSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``SessionDto`` : ``jeton`` et ``utilisateur`` (contrat existant) ;
    ``connecte_le``, ``id_appareil`` et ``droits`` sont des ajouts."""

    jeton = serializers.CharField()
    utilisateur = UtilisateurSerializer()
    connecte_le = serializers.DateTimeField(
        help_text="Heure du serveur : à ranger dans derniere_connexion_en_ligne (verrou 14 j)."
    )
    id_appareil = serializers.UUIDField(allow_null=True)
    droits = DroitEffectifSerializer(many=True)


# --- Profil courant (/auth/moi) ---------------------------------------------
class AffectationSerializer(serializers.Serializer):  # type: ignore[type-arg]
    role_code_role = serializers.CharField(source="role_id")
    libelle_role = serializers.CharField(source="role.libelle")
    perimetre_id_perimetre = serializers.UUIDField(source="perimetre_id")
    libelle_perimetre = serializers.CharField(source="perimetre.libelle")
    chantier_id_chantier = serializers.UUIDField(source="perimetre.chantier_id", allow_null=True)
    magasin_id_magasin = serializers.UUIDField(source="perimetre.magasin_id", allow_null=True)
    date_debut = serializers.DateField()
    date_fin = serializers.DateField(allow_null=True)


class ProfilSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Profil, affectations et droits effectifs : le mobile en tire ses
    onglets (permissions du module « mobile ») au lieu de les coder en dur
    (lève I-06 côté serveur). Bâtiment et libellé court d'appareil : absents
    du MPD (I-20), donc non servis."""

    utilisateur = UtilisateurSerializer()
    affectations = AffectationSerializer(many=True)
    droits = DroitEffectifSerializer(many=True)
    appareil = AppareilSerializer(allow_null=True)
    horodatage_serveur = serializers.DateTimeField()


# --- Comptes ----------------------------------------------------------------
class PerimetreSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_perimetre = serializers.UUIDField()
    libelle = serializers.CharField()


class CompteEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Corps de POST/PUT /auth/comptes. ``mot_de_passe`` est un ajout
    (arbitrage Q12) : obligatoire à la création, facultatif ensuite."""

    identifiant = serializers.CharField(max_length=120)
    nom = serializers.CharField(max_length=120)
    prenom = serializers.CharField(max_length=120)
    fonction = serializers.CharField(max_length=120, allow_blank=True, required=False, default="")
    statut = serializers.ChoiceField(choices=list(STATUTS_UTILISATEUR))
    role_code_role = serializers.CharField(max_length=32)
    perimetre_id_perimetre = serializers.UUIDField()
    mot_de_passe = serializers.CharField(
        max_length=256, required=False, allow_null=True, write_only=True, trim_whitespace=False
    )


# --- Droits -----------------------------------------------------------------
class RoleSerializer(serializers.Serializer):  # type: ignore[type-arg]
    code_role = serializers.CharField()
    libelle = serializers.CharField()
    systeme = serializers.BooleanField()
    actif = serializers.BooleanField()


class PermissionSerializer(serializers.Serializer):  # type: ignore[type-arg]
    code_permission = serializers.CharField()
    module = serializers.CharField()
    ressource = serializers.CharField()
    action = serializers.CharField()
    libelle = serializers.CharField()


class DroitAccordeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    role_code_role = serializers.CharField(source="role_id", max_length=32)
    permission_code_permission = serializers.CharField(source="permission_id", max_length=32)
    portee = serializers.CharField(max_length=32)


class MatriceEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    droits = DroitAccordeSerializer(many=True)
    # Ajout facultatif : modules à remplacer (voir services/matrice.py).
    modules = serializers.ListField(child=serializers.CharField(), required=False)


# --- Audit ------------------------------------------------------------------
class EntreeAuditSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``EntreeAuditDto``. ``id_objet`` reste null : colonne absente du MPD
    (incohérence I-27, non tranchée)."""

    id_entree = serializers.UUIDField()
    action = serializers.CharField()
    type_objet = serializers.CharField()
    id_objet = serializers.SerializerMethodField()
    resume = serializers.SerializerMethodField()
    horodatage = serializers.DateTimeField()
    adresse_ip = serializers.CharField(allow_null=True)
    utilisateur_id_utilisateur = serializers.UUIDField(source="utilisateur_id")
    identifiant_utilisateur = serializers.CharField(source="utilisateur.identifiant")
    nom_utilisateur = serializers.CharField(source="utilisateur.nom_complet")

    def get_id_objet(self, obj: Any) -> str | None:
        return None

    def get_resume(self, obj: Any) -> str:
        return service_audit.resume(obj)


class FiltreAuditSerializer(serializers.Serializer):  # type: ignore[type-arg]
    action = serializers.CharField(required=False, max_length=120)
    auteur = serializers.UUIDField(required=False)
    limite = serializers.IntegerField(required=False, min_value=1, max_value=1000, default=200)
