"""Points d'entrée du domaine « avancement » (UC-2 ; EF-AVA-01 à 10).

Chaque vue déclare son droit (``ADroit``, EF-AUT-07) ; ``services.acces``
vérifie en plus que le chantier de l'étape est couvert par ce droit. Les
permissions sont des données (migration ``avancement 0003``).
"""

from typing import Any

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domaines.avancement import selecteurs
from domaines.avancement.api import serialiseurs as s
from domaines.avancement.constantes import (
    BLOQUEE,
    FICHE_OUVERTE,
    PORTEE_CHANTIER,
    PORTEE_CORPS_ETAT,
    PORTEE_LOGEMENT,
    PORTEE_ZONE,
    TERMINEE_DECLAREE,
)
from domaines.avancement.services import acces, agregats, declarations, fiches
from domaines.identite.permissions import ADroit
from domaines.organisation import selecteurs as selecteurs_organisation

LIMITE_FICHES = 100


def droit(ressource: str, action: str) -> list[Any]:
    return [IsAuthenticated(), ADroit("api", ressource, action)()]


def _valider(classe: Any, donnees: Any) -> dict[str, Any]:
    entree = classe(data=donnees)
    entree.is_valid(raise_exception=True)
    return dict(entree.validated_data)


def _encadre(utilisateur: Any) -> bool:
    """Vrai si l'utilisateur affecte des étapes (encadrement) : il voit les
    fiches de tous ; sinon chacun ne voit que les siennes (RG-A3)."""
    return acces.chantiers_couverts(utilisateur, "fiches-route", "CREER") != set()


# --- Étapes d'un logement (EF-AVA-01, EF-AVA-03) ----------------------------------
class VueEtapesLogement(APIView):
    """GET /api/logements/{id}/etapes — étapes du logement, dans l'ordre."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.LigneEtapeSerializer(many=True))
    def get(self, request: Request, id_logement: str) -> Response:
        logement = acces.logement_autorise(request.user, id_logement, "avancement", "LIRE")
        etapes = selecteurs.etapes_du_logement(logement.pk)
        return Response(s.LigneEtapeSerializer(etapes, many=True).data)


# --- Fiches de route (RG-A7, EF-AVA-02, 03, 08) ---------------------------------------
class VueFiches(APIView):
    """GET /api/fiches-route?technicien=&statut= — un technicien ne voit que
    ses fiches ; l'encadrement voit celles de tous."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "LIRE")

    @extend_schema(
        parameters=[OpenApiParameter("technicien", str), OpenApiParameter("statut", str)],
        responses=s.FicheRouteSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        technicien = request.query_params.get("technicien")
        if not _encadre(request.user):
            technicien = str(request.user.pk)
        requete = selecteurs.fiches(technicien)
        if request.query_params.get("statut"):
            requete = requete.filter(statut=request.query_params["statut"])
        return Response(s.FicheRouteSerializer(requete[:LIMITE_FICHES], many=True).data)


class VueFicheCourante(APIView):
    """GET /api/fiches-route/courante — fiches ouvertes de l'utilisateur
    (écran « Mes fiches » du mobile, EF-AVA-03)."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "LIRE")

    @extend_schema(responses=s.FicheRouteSerializer(many=True))
    def get(self, request: Request) -> Response:
        ouvertes = selecteurs.fiches(request.user.pk).filter(statut=FICHE_OUVERTE)
        return Response(s.FicheRouteSerializer(ouvertes, many=True).data)


class VueFiche(APIView):
    """GET /api/fiches-route/{id}."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "LIRE")

    @extend_schema(responses=s.FicheRouteSerializer)
    def get(self, request: Request, id_fiche: str) -> Response:
        fiche = fiches.fiche_autorisee(request.user, id_fiche, "CREER")
        return Response(s.FicheRouteSerializer(fiche).data)


class VueAffectations(APIView):
    """POST /api/fiches-route/affectations — affecter un lot d'étapes à un
    technicien, avec date prévue ; la réaffectation est tracée (RG-A3)."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "CREER")

    @extend_schema(
        request=s.AffectationEntreeSerializer, responses=s.LigneEtapeSerializer(many=True)
    )
    def post(self, request: Request) -> Response:
        donnees = _valider(s.AffectationEntreeSerializer, request.data)
        affectees = fiches.affecter(
            request.user,
            donnees["etapes"],
            donnees["technicien_id_utilisateur"],
            donnees.get("date_prevue"),
        )
        relues = selecteurs.etapes().filter(pk__in=[etape.pk for etape in affectees])
        return Response(s.LigneEtapeSerializer(relues, many=True).data)


class VueCloture(APIView):
    """POST /api/fiches-route/{id}/cloture — fin de cycle, report motivé des
    étapes non faites (EF-AVA-08). Le technicien clôture sa propre fiche."""

    def get_permissions(self) -> list[Any]:
        return droit("fiches-route", "LIRE")

    @extend_schema(request=s.ClotureEntreeSerializer, responses=s.FicheRouteSerializer)
    def post(self, request: Request, id_fiche: str) -> Response:
        donnees = _valider(s.ClotureEntreeSerializer, request.data)
        fiche = fiches.fiche_autorisee(request.user, id_fiche, "MODIFIER")
        motifs = {str(r["id_etape"]): r["motif"] for r in donnees.get("reports", [])}
        fiches.verifier_motifs(fiche, motifs)
        return Response(s.FicheRouteSerializer(fiches.cloturer(fiche, motifs)).data)


# --- Déclarations et contrôle (EF-AVA-04 à 07, EF-AVA-10) -------------------------------
def _statut(cree: bool) -> int:
    """201 au premier envoi, 200 pour un rejeu déjà reçu (idempotence)."""
    return status.HTTP_201_CREATED if cree else status.HTTP_200_OK


class VueDeclaration(APIView):
    """POST /api/etapes/{id}/declaration — étape terminée (EF-AVA-04), en
    délégation si l'auteur n'est pas le technicien affecté (EF-AVA-07). Rend
    un ou deux événements (validation implicite sans contrôle, Q-X)."""

    def get_permissions(self) -> list[Any]:
        return droit("etapes", "MODIFIER")

    @extend_schema(
        request=s.DeclarationEntreeSerializer, responses={201: s.EvenementSerializer(many=True)}
    )
    def post(self, request: Request, id_etape: str) -> Response:
        donnees = _valider(s.DeclarationEntreeSerializer, request.data)
        evenements, cree = declarations.declarer_terminee(
            request.user,
            id_etape,
            uuid=donnees.get("uuid"),
            horodatage_appareil=donnees.get("horodatage_appareil"),
            commentaire=donnees.get("commentaire"),
        )
        return Response(s.EvenementSerializer(evenements, many=True).data, status=_statut(cree))


class VueBlocage(APIView):
    """POST /api/etapes/{id}/blocage — blocage motivé (EF-AVA-05, RG-A10)."""

    def get_permissions(self) -> list[Any]:
        return droit("etapes", "MODIFIER")

    @extend_schema(request=s.BlocageEntreeSerializer, responses={201: s.EvenementSerializer})
    def post(self, request: Request, id_etape: str) -> Response:
        donnees = _valider(s.BlocageEntreeSerializer, request.data)
        evenement, cree = declarations.bloquer(
            request.user,
            id_etape,
            donnees["code_motif"],
            commentaire=donnees.get("commentaire"),
            id_article=donnees.get("article_id_article"),
            uuid=donnees.get("uuid"),
            horodatage_appareil=donnees.get("horodatage_appareil"),
        )
        return Response(s.EvenementSerializer(evenement).data, status=_statut(cree))


class VueLeveeBlocage(APIView):
    """POST /api/etapes/{id}/levee-blocage — reprise après blocage (ET-1)."""

    def get_permissions(self) -> list[Any]:
        return droit("etapes", "MODIFIER")

    @extend_schema(request=s.LeveeEntreeSerializer, responses={201: s.EvenementSerializer})
    def post(self, request: Request, id_etape: str) -> Response:
        donnees = _valider(s.LeveeEntreeSerializer, request.data)
        evenement, cree = declarations.lever_blocage(
            request.user, id_etape, commentaire=donnees.get("commentaire"), uuid=donnees.get("uuid")
        )
        return Response(s.EvenementSerializer(evenement).data, status=_statut(cree))


class VueValidationEtape(APIView):
    """POST /api/etapes/{id}/validation — contrôle d'une étape (EF-AVA-06) ;
    le déclarant ne contrôle pas sa propre étape (RG-D11)."""

    def get_permissions(self) -> list[Any]:
        return droit("etapes", "VALIDER")

    @extend_schema(request=s.DecisionEtapeEntreeSerializer, responses={201: s.EvenementSerializer})
    def post(self, request: Request, id_etape: str) -> Response:
        donnees = _valider(s.DecisionEtapeEntreeSerializer, request.data)
        evenement, cree = declarations.decider(
            request.user, id_etape, donnees["decision"], donnees.get("motif"), donnees.get("uuid")
        )
        return Response(s.EvenementSerializer(evenement).data, status=_statut(cree))


class VueEvenementsEtape(APIView):
    """GET /api/etapes/{id}/evenements — historique complet (EF-AVA-10)."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.EvenementSerializer(many=True))
    def get(self, request: Request, id_etape: str) -> Response:
        etape = acces.etape_autorisee(request.user, id_etape, "avancement", "LIRE")
        evenements = selecteurs.evenements_de_l_etape(etape.pk)
        return Response(s.EvenementSerializer(evenements, many=True).data)


class VueEtapesAValider(APIView):
    """GET /api/avancement/etapes-a-valider — étapes à contrôle déclarées,
    en attente du chef de chantier ou du responsable technique (RG-A4)."""

    def get_permissions(self) -> list[Any]:
        return droit("etapes", "VALIDER")

    @extend_schema(responses=s.LigneEtapeSerializer(many=True))
    def get(self, request: Request) -> Response:
        couverts = acces.chantiers_couverts(request.user, "etapes", "VALIDER")
        etapes = selecteurs.etapes(couverts).filter(
            statut=TERMINEE_DECLAREE, etape_modele__controle_requis=True
        )
        return Response(s.LigneEtapeSerializer(etapes, many=True).data)


# --- Lectures d'avancement (écran Avancement du web) ------------------------------------
def _couverts(request: Request) -> set[Any] | None:
    return acces.chantiers_couverts(request.user, "avancement", "LIRE")


def _etapes_couvertes(request: Request) -> Any:
    return selecteurs.etapes(_couverts(request))


class VueZonesAvancement(APIView):
    """GET /api/avancement/zones."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.ZoneAvancementSerializer(many=True))
    def get(self, request: Request) -> Response:
        zones = selecteurs_organisation.zones().order_by("code")
        couverts = _couverts(request)
        if couverts is not None:
            zones = zones.filter(chantier_id__in=couverts)
        return Response(s.ZoneAvancementSerializer(zones, many=True).data)


class VueSynthese(APIView):
    """GET /api/avancement/synthese — avancement déclaré et validé (RG-A6) et
    nombres à surveiller, sur les chantiers couverts."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.SyntheseSerializer)
    def get(self, request: Request) -> Response:
        etapes = _etapes_couvertes(request)
        declare, valide, _nombre = agregats.mesurer(etapes)
        corps = {
            "pourcentage_declare": declare,
            "pourcentage_valide": valide,
            "nombre_logements": etapes.values("logement_id").distinct().count(),
            "nombre_etapes_a_valider": etapes.filter(
                statut=TERMINEE_DECLAREE, etape_modele__controle_requis=True
            ).count(),
            "nombre_etapes_bloquees": etapes.filter(statut=BLOQUEE).count(),
            "nombre_etapes_en_retard": etapes.filter(
                selecteurs.filtre_retard(timezone.localdate())
            ).count(),
        }
        return Response(s.SyntheseSerializer(corps).data)


def _lignes_logements(request: Request) -> list[dict[str, Any]]:
    couverts = _couverts(request)
    etapes = selecteurs.etapes(couverts)
    comptes = selecteurs.comptes_par("logement_id", etapes, timezone.localdate())
    lus = selecteurs.agregats(PORTEE_LOGEMENT)
    logements = selecteurs_organisation.logements().select_related("zone", "type_logement")
    if couverts is not None:
        logements = logements.filter(zone__chantier_id__in=couverts)
    lignes = []
    for logement in logements.order_by("numero"):
        agregat = lus.get(str(logement.pk))
        lignes.append(
            {
                "logement": logement,
                "agregat": agregat,
                "comptes": comptes.get(logement.pk, {}),
            }
        )
    return lignes


class VueLogementsAvancement(APIView):
    """GET /api/avancement/logements — un logement par ligne (H11)."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.LigneLogementSerializer(many=True))
    def get(self, request: Request) -> Response:
        corps = [
            {
                "id_logement": ligne["logement"].pk,
                "numero": ligne["logement"].numero,
                "libelle_zone": ligne["logement"].zone.nom,
                "libelle_type": ligne["logement"].type_logement.libelle,
                "statut": ligne["logement"].statut,
                "pourcentage_declare": _pct(ligne["agregat"], "pourcentage_declare"),
                "pourcentage_valide": _pct(ligne["agregat"], "pourcentage_valide"),
                **_comptes(ligne["comptes"]),
            }
            for ligne in _lignes_logements(request)
        ]
        return Response(s.LigneLogementSerializer(corps, many=True).data)


def _pct(agregat: Any, champ: str) -> Any:
    return getattr(agregat, champ) if agregat is not None else 0


def _comptes(comptes: dict[str, int]) -> dict[str, int]:
    return {
        cle: comptes.get(cle, 0)
        for cle in ("nombre_etapes", "nombre_validees", "nombre_bloquees", "nombre_en_retard")
    }


# --- Pilotage (AvancementAgregeDto, AlerteEtapeDto) ---------------------------------------
def _agregat_dto(
    portee: str,
    id_cible: str,
    libelle: str,
    agregat: Any,
    comptes: dict[str, int],
    libelle_secondaire: str | None = None,
    couleur: str | None = None,
) -> dict[str, Any]:
    return {
        "portee": portee,
        "id_cible": id_cible,
        "libelle_cible": libelle,
        "libelle_secondaire": libelle_secondaire,
        "couleur": couleur,
        "pourcentage_declare": _pct(agregat, "pourcentage_declare"),
        "pourcentage_valide": _pct(agregat, "pourcentage_valide"),
        **_comptes(comptes),
        "date_calcul": agregat.date_calcul if agregat is not None else timezone.now(),
    }


class VuePilotageChantier(APIView):
    """GET /api/pilotage/avancement/chantier — le chantier (le premier couvert
    ; un seul au pilote)."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.AvancementAgregeSerializer)
    def get(self, request: Request) -> Response:
        couverts = _couverts(request)
        chantiers = selecteurs_organisation.chantiers()
        if couverts is not None:
            chantiers = chantiers.filter(id_chantier__in=couverts)
        chantier = chantiers.first()
        if chantier is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        etapes = selecteurs.etapes({chantier.pk})
        comptes = selecteurs.comptes_par(
            "logement__zone__chantier_id", etapes, timezone.localdate()
        )
        dto = _agregat_dto(
            PORTEE_CHANTIER,
            str(chantier.pk),
            chantier.nom,
            selecteurs.agregats(PORTEE_CHANTIER).get(str(chantier.pk)),
            comptes.get(chantier.pk, {}),
        )
        return Response(s.AvancementAgregeSerializer(dto).data)


class VuePilotageZones(APIView):
    """GET /api/pilotage/avancement/zones."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.AvancementAgregeSerializer(many=True))
    def get(self, request: Request) -> Response:
        couverts = _couverts(request)
        comptes = selecteurs.comptes_par(
            "logement__zone_id", selecteurs.etapes(couverts), timezone.localdate()
        )
        lus = selecteurs.agregats(PORTEE_ZONE)
        zones = selecteurs_organisation.zones().select_related("chantier").order_by("code")
        if couverts is not None:
            zones = zones.filter(chantier_id__in=couverts)
        corps = [
            _agregat_dto(
                PORTEE_ZONE,
                str(z.pk),
                z.nom,
                lus.get(str(z.pk)),
                comptes.get(z.pk, {}),
                z.chantier.nom,
            )
            for z in zones
        ]
        return Response(s.AvancementAgregeSerializer(corps, many=True).data)


class VuePilotageLogements(APIView):
    """GET /api/pilotage/avancement/logements."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.AvancementAgregeSerializer(many=True))
    def get(self, request: Request) -> Response:
        corps = [
            _agregat_dto(
                PORTEE_LOGEMENT,
                str(ligne["logement"].pk),
                ligne["logement"].numero,
                ligne["agregat"],
                ligne["comptes"],
                ligne["logement"].zone.nom,
            )
            for ligne in _lignes_logements(request)
        ]
        return Response(s.AvancementAgregeSerializer(corps, many=True).data)


class VuePilotageCorpsEtat(APIView):
    """GET /api/pilotage/avancement/corps-etat — par corps d'état et par
    chantier (RG-A6)."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.AvancementAgregeSerializer(many=True))
    def get(self, request: Request) -> Response:
        etapes = selecteurs.etapes(_couverts(request))
        lus = selecteurs.agregats(PORTEE_CORPS_ETAT)
        groupes = (
            etapes.order_by()
            .values(
                "logement__zone__chantier_id",
                "etape_modele__corps_etat_id",
                "etape_modele__corps_etat__libelle",
                "etape_modele__corps_etat__couleur",
                "etape_modele__corps_etat__ordre",
            )
            .distinct()
        )
        corps = []
        for groupe in sorted(groupes, key=lambda g: g["etape_modele__corps_etat__ordre"]):
            cible = agregats.cible_corps_etat(
                groupe["logement__zone__chantier_id"], groupe["etape_modele__corps_etat_id"]
            )
            corps.append(
                _agregat_dto(
                    PORTEE_CORPS_ETAT,
                    cible,
                    groupe["etape_modele__corps_etat__libelle"],
                    lus.get(cible),
                    # Compté chantier par chantier : un corps d'état n'est pas
                    # agrégé d'un chantier à l'autre.
                    selecteurs.comptes_par(
                        "etape_modele__corps_etat_id",
                        etapes.filter(
                            logement__zone__chantier_id=groupe["logement__zone__chantier_id"]
                        ),
                        timezone.localdate(),
                    ).get(groupe["etape_modele__corps_etat_id"], {}),
                    couleur=groupe["etape_modele__corps_etat__couleur"],
                )
            )
        return Response(s.AvancementAgregeSerializer(corps, many=True).data)


class VueAlertesEtapes(APIView):
    """GET /api/pilotage/alertes-etapes — étapes en retard ou bloquées (RG-A8,
    EF-AVA-09) ; la remontée par notification relève de B6."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.AlerteEtapeSerializer(many=True))
    def get(self, request: Request) -> Response:
        lignes = selecteurs.alertes(_couverts(request), timezone.localdate())
        return Response(s.AlerteEtapeSerializer(lignes, many=True).data)


# --- Journal d'exécution (EF-DSH-03) ------------------------------------------------
class VueJournal(APIView):
    """GET /api/pilotage/journal — journal d'exécution filtré (auteur, zone,
    statut, depuis, jusqua), les plus récents d'abord."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(
        parameters=[s.FiltreJournalSerializer],
        responses=s.EvenementJournalSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        filtres = s.FiltreJournalSerializer(data=request.query_params)
        filtres.is_valid(raise_exception=True)
        donnees = dict(filtres.validated_data)
        limite = donnees.pop("limite")
        lignes = selecteurs.journal(_couverts(request), **donnees)[:limite]
        return Response(s.EvenementJournalSerializer(lignes, many=True).data)


class VueIntervenants(APIView):
    """GET /api/pilotage/journal/intervenants — auteurs d'au moins un
    événement, pour le filtre du journal (RG-A5 « qui »)."""

    def get_permissions(self) -> list[Any]:
        return droit("avancement", "LIRE")

    @extend_schema(responses=s.IntervenantSerializer(many=True))
    def get(self, request: Request) -> Response:
        return Response(
            s.IntervenantSerializer(selecteurs.intervenants(_couverts(request)), many=True).data
        )
