"""Sérialiseurs du domaine « avancement » : ils fixent le CONTRAT d'API.

Formes reprises de ``features/avancement/api/dto.ts`` et
``features/pilotage/api/dto.ts`` (web) : ``LigneEtapeDto``,
``EvenementExecutionDto``, ``LigneLogementDto``, ``ZoneDto``,
``SyntheseAvancementDto``, ``AvancementAgregeDto``, ``AlerteEtapeDto``.
Pourcentages et poids en chaîne (numeric(14,3)). Les fiches de route, la
déclaration et la levée de blocage n'ont pas d'écran web : leur forme est
définie ici, proche du mobile (contrat d'abord, F-13).
"""

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from domaines.avancement import selecteurs
from domaines.avancement.constantes import LONGUEUR_COMMENTAIRE, STATUTS_ETAPE
from domaines.avancement.models import EtapeTravaux, EvenementExecution, FicheRoute
from domaines.avancement.services.declarations import DECISIONS
from domaines.identite.selecteurs import comptes


def _quantite(**options: Any) -> serializers.DecimalField:
    return serializers.DecimalField(max_digits=14, decimal_places=3, **options)


class LigneEtapeSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``LigneEtapeDto`` : une étape avec son logement, son corps d'état, son
    retard (RG-A8) et l'auteur de sa dernière déclaration."""

    id_logement = serializers.UUIDField(source="logement_id")
    numero_logement = serializers.CharField(source="logement.numero")
    libelle_etape = serializers.CharField(source="etape_modele.libelle")
    code_corps_etat = serializers.CharField(source="etape_modele.corps_etat_id")
    libelle_corps_etat = serializers.CharField(source="etape_modele.corps_etat.libelle")
    couleur_corps_etat = serializers.CharField(source="etape_modele.corps_etat.couleur")
    ordre = serializers.IntegerField(source="etape_modele.ordre")
    controle_requis = serializers.BooleanField(source="etape_modele.controle_requis")
    en_retard = serializers.SerializerMethodField()
    id_auteur_declaration = serializers.UUIDField(allow_null=True, read_only=True, default=None)
    nom_auteur_declaration = serializers.CharField(allow_null=True, read_only=True, default=None)

    class Meta:
        model = EtapeTravaux
        fields = [
            "id_etape",
            "id_logement",
            "numero_logement",
            "libelle_etape",
            "code_corps_etat",
            "libelle_corps_etat",
            "couleur_corps_etat",
            "ordre",
            "statut",
            "date_prevue",
            "date_fin_declaree",
            "date_validation",
            "poids_effectif",
            "controle_requis",
            "en_retard",
            "id_auteur_declaration",
            "nom_auteur_declaration",
        ]

    def get_en_retard(self, obj: EtapeTravaux) -> bool:
        return selecteurs.en_retard(obj, timezone.localdate())


class EvenementSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``EvenementExecutionDto``. ``est_delegation`` : déclaré pour le compte
    d'un autre (RG-A9, Q-W) ; ``pour_le_compte_de`` est un ajout compatible."""

    etape_travaux_id_etape = serializers.UUIDField(source="etape_travaux_id")
    utilisateur_id_utilisateur = serializers.UUIDField(source="utilisateur_id")
    nom_auteur = serializers.CharField(source="utilisateur.nom_complet")
    est_delegation = serializers.SerializerMethodField()
    pour_le_compte_de_id_utilisateur = serializers.UUIDField(
        source="pour_le_compte_de_id", allow_null=True
    )
    nom_pour_le_compte_de = serializers.SerializerMethodField()
    motif_blocage_code_motif = serializers.CharField(source="motif_blocage_id", allow_null=True)
    article_id_article = serializers.UUIDField(source="article_id", allow_null=True)

    class Meta:
        model = EvenementExecution
        fields = [
            "uuid",
            "etape_travaux_id_etape",
            "statut_avant",
            "statut_apres",
            "horodatage_appareil",
            "horodatage_serveur",
            "commentaire",
            "utilisateur_id_utilisateur",
            "nom_auteur",
            "est_delegation",
            "pour_le_compte_de_id_utilisateur",
            "nom_pour_le_compte_de",
            "motif_blocage_code_motif",
            "article_id_article",
        ]

    def get_est_delegation(self, obj: EvenementExecution) -> bool:
        return (
            obj.pour_le_compte_de_id is not None and obj.pour_le_compte_de_id != obj.utilisateur_id
        )

    def get_nom_pour_le_compte_de(self, obj: EvenementExecution) -> str | None:
        return obj.pour_le_compte_de.nom_complet if obj.pour_le_compte_de else None


# --- Fiches de route (RG-A7, EF-AVA-02, 03, 08) --------------------------------------
class LigneFicheSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_ligne = serializers.UUIDField()
    ordre = serializers.IntegerField()
    reportee = serializers.BooleanField()
    motif_report = serializers.CharField(allow_null=True)
    etape = LigneEtapeSerializer(source="etape_travaux")


class FicheRouteSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    utilisateur_id_utilisateur = serializers.UUIDField(source="utilisateur_id")
    nom_technicien = serializers.CharField(source="utilisateur.nom_complet")
    lignes = serializers.SerializerMethodField()

    class Meta:
        model = FicheRoute
        fields = [
            "id_fiche",
            "type_cycle",
            "date_debut",
            "date_fin",
            "statut",
            "date_cloture",
            "utilisateur_id_utilisateur",
            "nom_technicien",
            "lignes",
        ]

    def get_lignes(self, obj: FicheRoute) -> list[dict[str, Any]]:
        lignes = obj.lignes.select_related(
            "etape_travaux__logement", "etape_travaux__etape_modele__corps_etat"
        ).order_by("ordre", "etape_travaux__logement__numero")
        return list(LigneFicheSerializer(lignes, many=True).data)


class AffectationEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Affecter un lot d'étapes à un technicien, avec date prévue (EF-AVA-02)."""

    etapes = serializers.ListField(child=serializers.UUIDField(), min_length=1)
    technicien_id_utilisateur = serializers.PrimaryKeyRelatedField(queryset=comptes.lister())
    date_prevue = serializers.DateField(required=False, allow_null=True)


class ReportSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_etape = serializers.UUIDField()
    motif = serializers.CharField()


class ClotureEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Clôture d'une fiche (EF-AVA-08) : motif de report par étape non faite ;
    sans motif, « non faite en fin de cycle »."""

    reports = ReportSerializer(many=True, required=False)


# --- Déclarations (EF-AVA-04 à 07) ------------------------------------------------------
# ``uuid`` : identifiant de l'événement généré par le téléphone (rejeu sans
# doublon) ; ``horodatage_appareil`` : heure de la saisie hors ligne (RG-A5).
def _commentaire() -> serializers.CharField:
    return serializers.CharField(
        max_length=LONGUEUR_COMMENTAIRE, required=False, allow_null=True, allow_blank=True
    )


class DeclarationEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    uuid = serializers.UUIDField(required=False)
    horodatage_appareil = serializers.DateTimeField(required=False)
    commentaire = _commentaire()


class BlocageEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Corps du web (``code_motif``, ``commentaire``) ; ``article_id_article``
    pour un manque de matériel (RG-A10)."""

    code_motif = serializers.CharField(max_length=32)
    commentaire = _commentaire()
    article_id_article = serializers.UUIDField(required=False, allow_null=True)
    uuid = serializers.UUIDField(required=False)
    horodatage_appareil = serializers.DateTimeField(required=False)


class LeveeEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    commentaire = _commentaire()
    uuid = serializers.UUIDField(required=False)


class DecisionEtapeEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """ACCEPTE ou REFUSE (motif obligatoire au rejet). Le web envoie encore
    « valider » / « rejeter » (I-30) : il s'alignera (F-13)."""

    decision = serializers.ChoiceField(choices=list(DECISIONS))
    motif = _commentaire()
    uuid = serializers.UUIDField(required=False)


# --- Lectures d'avancement et de pilotage (RG-A6, RG-A8) ----------------------------------
class ZoneAvancementSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``ZoneDto`` du module Avancement (troisième forme de la zone, I-30)."""

    id_zone = serializers.UUIDField()
    code = serializers.CharField()
    nom = serializers.CharField()
    id_chantier = serializers.UUIDField(source="chantier_id")


class SyntheseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    pourcentage_declare = _quantite()
    pourcentage_valide = _quantite()
    nombre_logements = serializers.IntegerField()
    nombre_etapes_a_valider = serializers.IntegerField()
    nombre_etapes_bloquees = serializers.IntegerField()
    nombre_etapes_en_retard = serializers.IntegerField()


class LigneLogementSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_logement = serializers.UUIDField()
    numero = serializers.CharField()
    libelle_zone = serializers.CharField()
    libelle_type = serializers.CharField()
    statut = serializers.CharField()
    pourcentage_declare = _quantite()
    pourcentage_valide = _quantite()
    nombre_etapes = serializers.IntegerField()
    nombre_validees = serializers.IntegerField()
    nombre_bloquees = serializers.IntegerField()
    nombre_en_retard = serializers.IntegerField()


class AvancementAgregeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``AvancementAgregeDto`` du pilotage."""

    portee = serializers.CharField()
    id_cible = serializers.CharField()
    libelle_cible = serializers.CharField()
    libelle_secondaire = serializers.CharField(allow_null=True)
    couleur = serializers.CharField(allow_null=True)
    pourcentage_declare = _quantite()
    pourcentage_valide = _quantite()
    nombre_etapes = serializers.IntegerField()
    nombre_validees = serializers.IntegerField()
    nombre_bloquees = serializers.IntegerField()
    nombre_en_retard = serializers.IntegerField()
    date_calcul = serializers.DateTimeField()


class AlerteEtapeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``AlerteEtapeDto`` : étape en retard ou bloquée (RG-A8)."""

    id_etape = serializers.UUIDField()
    id_logement = serializers.UUIDField(source="logement_id")
    numero_logement = serializers.CharField(source="logement.numero")
    libelle_zone = serializers.CharField(source="logement.zone.nom")
    libelle_etape = serializers.CharField(source="etape_modele.libelle")
    libelle_corps_etat = serializers.CharField(source="etape_modele.corps_etat.libelle")
    couleur_corps_etat = serializers.CharField(source="etape_modele.corps_etat.couleur")
    statut = serializers.CharField()
    date_prevue = serializers.DateField(allow_null=True)
    jours_de_retard = serializers.SerializerMethodField()
    code_motif_blocage = serializers.CharField(allow_null=True, default=None)
    libelle_motif_blocage = serializers.CharField(allow_null=True, default=None)
    commentaire = serializers.CharField(source="commentaire_blocage", allow_null=True, default=None)

    def get_jours_de_retard(self, obj: EtapeTravaux) -> int:
        if not selecteurs.en_retard(obj, timezone.localdate()):
            return 0
        return (timezone.localdate() - obj.date_prevue).days  # type: ignore[operator]


# --- Journal d'exécution (EF-DSH-03) : formes de features/pilotage/api/dto.ts --------
class EvenementJournalSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``EvenementJournalDto`` : l'événement et son contexte (étape, logement,
    zone, corps d'état), lisible sans autre appel. RG-A5 : deux horodatages."""

    id_etape = serializers.UUIDField(source="etape_travaux_id")
    libelle_etape = serializers.CharField(source="etape_travaux.etape_modele.libelle")
    id_logement = serializers.UUIDField(source="etape_travaux.logement_id")
    numero_logement = serializers.CharField(source="etape_travaux.logement.numero")
    libelle_zone = serializers.CharField(source="etape_travaux.logement.zone.nom")
    code_corps_etat = serializers.CharField(source="etape_travaux.etape_modele.corps_etat_id")
    libelle_corps_etat = serializers.CharField(
        source="etape_travaux.etape_modele.corps_etat.libelle"
    )
    id_auteur = serializers.UUIDField(source="utilisateur_id")
    nom_auteur = serializers.CharField(source="utilisateur.nom_complet")
    est_delegation = serializers.SerializerMethodField()
    code_motif_blocage = serializers.CharField(source="motif_blocage_id", allow_null=True)
    libelle_motif_blocage = serializers.SerializerMethodField()

    class Meta:
        model = EvenementExecution
        fields = [
            "uuid",
            "id_etape",
            "libelle_etape",
            "id_logement",
            "numero_logement",
            "libelle_zone",
            "code_corps_etat",
            "libelle_corps_etat",
            "statut_avant",
            "statut_apres",
            "horodatage_appareil",
            "horodatage_serveur",
            "id_auteur",
            "nom_auteur",
            "est_delegation",
            "code_motif_blocage",
            "libelle_motif_blocage",
            "commentaire",
        ]

    def get_est_delegation(self, obj: EvenementExecution) -> bool:
        return (
            obj.pour_le_compte_de_id is not None and obj.pour_le_compte_de_id != obj.utilisateur_id
        )

    def get_libelle_motif_blocage(self, obj: EvenementExecution) -> str | None:
        return obj.motif_blocage.libelle if obj.motif_blocage else None


class FiltreJournalSerializer(serializers.Serializer):  # type: ignore[type-arg]
    auteur = serializers.UUIDField(required=False)
    zone = serializers.UUIDField(required=False)
    statut = serializers.ChoiceField(choices=list(STATUTS_ETAPE), required=False)
    depuis = serializers.DateField(required=False)
    jusqua = serializers.DateField(required=False)
    limite = serializers.IntegerField(required=False, default=500, min_value=1, max_value=1000)

    def to_internal_value(self, data: Any) -> Any:
        # Le statut s'accepte quelle que soit la casse (le web le transmet tel quel).
        donnees = dict(data.items()) if hasattr(data, "items") else data
        if isinstance(donnees.get("statut"), str):
            donnees["statut"] = donnees["statut"].upper()
        return super().to_internal_value(donnees)


class IntervenantSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_utilisateur = serializers.UUIDField()
    nom = serializers.CharField()
