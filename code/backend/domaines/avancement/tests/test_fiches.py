"""Instanciation des étapes (RG-A1, EF-AVA-01, Q-AA), affectation tracée
(RG-A3, EF-AVA-02) et fiches de route par cycle (RG-A7, EF-AVA-03, 08)."""

from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.avancement.models import EtapeTravaux, EvenementExecution, FicheRoute
from domaines.avancement.services import fiches
from domaines.identite.models import DroitAccorde
from domaines.organisation.models import Logement, TypeLogement
from domaines.referentiels import services as services_referentiels
from domaines.referentiels.models import EtapeModele, Gamme
from socle.models import ExecutionTraitement

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


# --- Instanciation (RG-A1, Q-AA) ------------------------------------------------------
def test_un_logement_cree_recoit_les_etapes_de_la_gamme_active(logement: Logement) -> None:
    etapes = EtapeTravaux.objects.filter(logement=logement).order_by("etape_modele__ordre")
    assert [(e.statut, e.poids_effectif) for e in etapes] == [
        ("A_FAIRE", Decimal("50")),
        ("A_FAIRE", Decimal("30")),
        ("A_FAIRE", Decimal("20")),
    ]


def test_la_premiere_gamme_publiee_instancie_les_logements_en_attente(
    chantier_avancement: dict[str, Any],
) -> None:
    duplex = TypeLogement.objects.create(code_type="DUPLEX", libelle="Duplex")
    logement = Logement.objects.create(
        numero="D01", zone=chantier_avancement["zone"], type_logement=duplex
    )
    assert not EtapeTravaux.objects.filter(logement=logement).exists()
    brouillon = Gamme.objects.create(version=1, libelle="Duplex", type_logement=duplex)
    EtapeModele.objects.create(
        code="D-01",
        libelle="Dalle",
        ordre=1,
        poids=Decimal("100"),
        gamme=brouillon,
        corps_etat_id="GO",
    )
    services_referentiels.publier(str(brouillon.pk))
    assert EtapeTravaux.objects.filter(logement=logement).count() == 1


def test_une_nouvelle_version_ne_recree_pas_les_etapes(logement: Logement) -> None:
    gamme = logement.type_logement.gammes.get()
    brouillon = services_referentiels.nouvelle_version(str(gamme.pk))
    services_referentiels.publier(str(brouillon.pk))
    assert EtapeTravaux.objects.filter(logement=logement).count() == 3


# --- Cycles (RG-A7, H9) ------------------------------------------------------------------
@pytest.mark.parametrize(
    ("cycle", "jour", "attendu"),
    [
        ("JOUR", date(2026, 11, 18), (date(2026, 11, 18), date(2026, 11, 18))),
        ("SEMAINE", date(2026, 11, 18), (date(2026, 11, 16), date(2026, 11, 22))),
        ("QUINZAINE", date(2026, 11, 3), (date(2026, 11, 1), date(2026, 11, 15))),
        ("QUINZAINE", date(2026, 2, 20), (date(2026, 2, 16), date(2026, 2, 28))),
        ("LOGEMENT", date(2026, 11, 18), (date(2026, 11, 18), None)),
    ],
)
def test_les_bornes_du_cycle(cycle: str, jour: date, attendu: tuple[date, date | None]) -> None:
    assert fiches.bornes_du_cycle(cycle, jour) == attendu


# --- Affectation (RG-A3, EF-AVA-02) -------------------------------------------------------
def _affecter(client: APIClient, etapes: list[EtapeTravaux], technicien: Any, **champs: Any) -> Any:
    return client.post(
        "/api/fiches-route/affectations",
        {
            "etapes": [str(e.pk) for e in etapes],
            "technicien_id_utilisateur": str(technicien.pk),
            **champs,
        },
        format="json",
    )


def test_affecter_met_en_cours_inscrit_sur_la_fiche_et_trace(
    client_authentifie: Client, chantier_avancement: dict[str, Any], logement: Logement
) -> None:
    technicien = chantier_avancement["technicien"]
    etapes = list(EtapeTravaux.objects.filter(logement=logement))
    reponse = _affecter(client_authentifie(), etapes, technicien, date_prevue="2026-12-01")
    assert reponse.status_code == 200
    assert {e["statut"] for e in reponse.json()} == {"EN_COURS"}
    fiche = FicheRoute.objects.get(utilisateur=technicien)
    assert (fiche.type_cycle, fiche.lignes.count()) == ("SEMAINE", 3)
    commentaires = set(EvenementExecution.objects.values_list("commentaire", flat=True))
    assert commentaires == {f"Affectée à {technicien.nom_complet}"}


def test_reaffecter_deplace_l_etape_et_trace_le_changement(
    client_authentifie: Client,
    chantier_avancement: dict[str, Any],
    logement: Logement,
    fabrique_utilisateur: Any,
) -> None:
    client = client_authentifie()
    etape = EtapeTravaux.objects.filter(logement=logement).first()
    assert etape is not None
    premier, second = chantier_avancement["technicien"], fabrique_utilisateur(role="TECHNICIEN")
    _affecter(client, [etape], premier)
    _affecter(client, [etape], second)
    assert fiches.technicien_actuel(etape) == second
    dernier = EvenementExecution.objects.order_by("-horodatage_serveur").first()
    assert dernier is not None
    assert dernier.commentaire == f"Réaffectée de {premier.nom_complet} à {second.nom_complet}"
    assert (dernier.statut_avant, dernier.statut_apres) == ("EN_COURS", "EN_COURS")


def test_une_etape_terminee_ne_s_affecte_plus(
    client_authentifie: Client, chantier_avancement: dict[str, Any], logement: Logement
) -> None:
    etape = EtapeTravaux.objects.filter(logement=logement).first()
    assert etape is not None
    EtapeTravaux.objects.filter(pk=etape.pk).update(statut="VALIDEE")
    reponse = _affecter(client_authentifie(), [etape], chantier_avancement["technicien"])
    assert reponse.status_code == 409


# --- Fiches de route (EF-AVA-03, EF-AVA-08) -----------------------------------------------
def test_un_technicien_ne_voit_que_ses_fiches(
    client_authentifie: Client, chantier_avancement: dict[str, Any], logement: Logement
) -> None:
    etapes = list(EtapeTravaux.objects.filter(logement=logement))
    _affecter(client_authentifie(), etapes, chantier_avancement["technicien"])
    DroitAccorde.objects.create(
        role_id="TECHNICIEN", permission_id="api.fiches-route.lire", portee="GLOBALE"
    )
    proprietaire = client_authentifie(utilisateur=chantier_avancement["technicien"])
    autre = client_authentifie("TECHNICIEN")
    assert len(proprietaire.get("/api/fiches-route/courante").json()[0]["lignes"]) == 3
    assert autre.get("/api/fiches-route").json() == []


def test_cloturer_reporte_les_etapes_non_faites_sur_le_cycle_suivant(
    client_authentifie: Client, chantier_avancement: dict[str, Any], logement: Logement
) -> None:
    client = client_authentifie()
    etapes = list(EtapeTravaux.objects.filter(logement=logement).order_by("etape_modele__ordre"))
    _affecter(client, etapes, chantier_avancement["technicien"])
    EtapeTravaux.objects.filter(pk=etapes[0].pk).update(statut="VALIDEE")
    fiche = FicheRoute.objects.get()
    reponse = client.post(
        f"/api/fiches-route/{fiche.pk}/cloture",
        {"reports": [{"id_etape": str(etapes[1].pk), "motif": "pluie"}]},
        format="json",
    )
    assert reponse.json()["statut"] == "CLOTUREE"
    motifs = {
        ligne["etape"]["id_etape"]: ligne["motif_report"] for ligne in reponse.json()["lignes"]
    }
    assert motifs[str(etapes[1].pk)] == "pluie"
    assert motifs[str(etapes[2].pk)] == "Non faite en fin de cycle"
    suivante = FicheRoute.objects.get(statut="OUVERTE")
    assert suivante.date_debut > fiche.date_debut
    assert suivante.lignes.count() == 2
    deuxieme = client.post(f"/api/fiches-route/{fiche.pk}/cloture", {}, format="json")
    assert deuxieme.status_code == 409


def test_le_traitement_cloture_les_fiches_echues(
    client_authentifie: Client, chantier_avancement: dict[str, Any], logement: Logement
) -> None:
    _affecter(
        client_authentifie(),
        list(EtapeTravaux.objects.filter(logement=logement)),
        chantier_avancement["technicien"],
    )
    il_y_a_dix_jours = timezone.localdate() - timedelta(days=10)
    FicheRoute.objects.update(date_debut=il_y_a_dix_jours, date_fin=il_y_a_dix_jours)
    call_command("lancer_traitement", "cycler_fiches_route")
    assert ExecutionTraitement.objects.get(nom_traitement="cycler_fiches_route").statut == "REUSSI"
    assert FicheRoute.objects.filter(statut="CLOTUREE").count() == 1
    assert FicheRoute.objects.get(statut="OUVERTE").lignes.count() == 3


# --- Lecture des étapes d'un logement --------------------------------------------------------
def test_les_etapes_du_logement_ont_la_forme_de_l_ecran(
    client_authentifie: Client, logement: Logement
) -> None:
    etapes = client_authentifie().get(f"/api/logements/{logement.pk}/etapes").json()
    assert [e["libelle_etape"] for e in etapes] == ["Fondations", "Murs", "Peinture"]
    assert etapes[0]["controle_requis"] is True
    assert etapes[0]["en_retard"] is False
    assert etapes[0]["poids_effectif"] == "50.000"


def test_sans_le_droit_de_lecture_les_etapes_sont_refusees(
    client_authentifie: Client, logement: Logement
) -> None:
    reponse = client_authentifie("ACQUEREUR").get(f"/api/logements/{logement.pk}/etapes")
    assert reponse.status_code == 403
