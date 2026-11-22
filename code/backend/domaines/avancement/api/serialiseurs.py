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
from domaines.avancement.models import EtapeTravaux, EvenementExecution, FicheRoute
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
