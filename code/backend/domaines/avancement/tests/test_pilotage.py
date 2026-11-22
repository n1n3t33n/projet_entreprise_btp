"""Avancement agrégé (RG-A6, Q-V, Q-AB), retards et blocages (RG-A8,
EF-AVA-09), lectures de l'écran Avancement et du pilotage."""

from collections.abc import Callable
from datetime import timedelta
from decimal import Decimal
from typing import Any

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.avancement.models import AvancementAgrege, EtapeTravaux
from domaines.avancement.services import agregats, declarations, fiches
from domaines.organisation.models import Logement
from socle.models import ExecutionTraitement

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def chantier_en_cours(
    chantier_avancement: dict[str, Any], logement: Logement, fabrique_utilisateur: Any
) -> dict[str, Any]:
    """Étapes : Fondations (50, à contrôle), Murs (30), Peinture (20), affectées
    au technicien par un encadrant qui pourra contrôler."""
    encadrant = fabrique_utilisateur()
    etapes = list(EtapeTravaux.objects.filter(logement=logement).order_by("etape_modele__ordre"))
    fiches.affecter(encadrant, [e.pk for e in etapes], chantier_avancement["technicien"], None)
    return {
        **chantier_avancement,
        "logement": logement,
        "encadrant": encadrant,
        "fondations": etapes[0],
        "murs": etapes[1],
        "peinture": etapes[2],
    }


def _agregat(portee: str, id_cible: Any) -> tuple[Decimal, Decimal]:
    agregat = AvancementAgrege.objects.get(portee=portee, id_cible=str(id_cible))
    return agregat.pourcentage_declare, agregat.pourcentage_valide


# --- RG-A6 : déclaré et validé, à chaque portée -----------------------------------------
def test_l_avancement_suit_les_declarations_et_les_controles(
    chantier_en_cours: dict[str, Any], fabrique_utilisateur: Any
) -> None:
    c = chantier_en_cours
    declarations.declarer_terminee(c["encadrant"], c["murs"].pk)  # 30, validée implicitement
    assert _agregat("LOGEMENT", c["logement"].pk) == (Decimal("30.000"), Decimal("30.000"))
    declarations.declarer_terminee(c["encadrant"], c["fondations"].pk)  # 50, à contrôle
    assert _agregat("LOGEMENT", c["logement"].pk) == (Decimal("80.000"), Decimal("30.000"))
    declarations.decider(fabrique_utilisateur(), c["fondations"].pk, "ACCEPTE", None)
    assert _agregat("LOGEMENT", c["logement"].pk) == (Decimal("80.000"), Decimal("80.000"))
    assert _agregat("ZONE", c["zone"].pk) == (Decimal("80.000"), Decimal("80.000"))
    assert _agregat("CHANTIER", c["chantier"].pk) == (Decimal("80.000"), Decimal("80.000"))
    gros_oeuvre = agregats.cible_corps_etat(c["chantier"].pk, "GO")
    assert _agregat("CORPS_ETAT", gros_oeuvre) == (Decimal("100.000"), Decimal("100.000"))
    assert _agregat("CORPS_ETAT", agregats.cible_corps_etat(c["chantier"].pk, "FIN")) == (
        Decimal("0.000"),
        Decimal("0.000"),
    )


def test_la_consolidation_corrige_une_derive(chantier_en_cours: dict[str, Any]) -> None:
    declarations.declarer_terminee(chantier_en_cours["encadrant"], chantier_en_cours["murs"].pk)
    AvancementAgrege.objects.update(pourcentage_declare=Decimal("99"))
    call_command("lancer_traitement", "consolider_avancement")
    execution = ExecutionTraitement.objects.get(nom_traitement="consolider_avancement")
    assert execution.statut == "REUSSI"
    assert _agregat("LOGEMENT", chantier_en_cours["logement"].pk)[0] == Decimal("30.000")


# --- Lectures de l'écran Avancement ---------------------------------------------------------
def test_la_synthese_et_les_logements(
    client_authentifie: Client, chantier_en_cours: dict[str, Any]
) -> None:
    c = chantier_en_cours
    declarations.declarer_terminee(c["encadrant"], c["fondations"].pk)
    declarations.bloquer(c["encadrant"], c["peinture"].pk, "INTEMPERIES")
    client = client_authentifie()
    synthese = client.get("/api/avancement/synthese").json()
    assert synthese == {
        "pourcentage_declare": "50.000",
        "pourcentage_valide": "0.000",
        "nombre_logements": 1,
        "nombre_etapes_a_valider": 1,
        "nombre_etapes_bloquees": 1,
        "nombre_etapes_en_retard": 0,
    }
    ligne = client.get("/api/avancement/logements").json()[0]
    assert (ligne["numero"], ligne["nombre_etapes"], ligne["nombre_bloquees"]) == ("A01", 3, 1)
    assert ligne["pourcentage_declare"] == "50.000"
    zones = client.get("/api/avancement/zones").json()
    assert zones == [
        {
            "id_zone": str(c["zone"].pk),
            "code": "A",
            "nom": "Îlot A",
            "id_chantier": str(c["chantier"].pk),
        }
    ]


# --- Pilotage -------------------------------------------------------------------------------------
def test_le_pilotage_sert_les_quatre_portees(
    client_authentifie: Client, chantier_en_cours: dict[str, Any]
) -> None:
    declarations.declarer_terminee(chantier_en_cours["encadrant"], chantier_en_cours["murs"].pk)
    client = client_authentifie()
    chantier = client.get("/api/pilotage/avancement/chantier").json()
    assert (chantier["portee"], chantier["pourcentage_valide"], chantier["nombre_validees"]) == (
        "CHANTIER",
        "30.000",
        1,
    )
    zones = client.get("/api/pilotage/avancement/zones").json()
    assert zones[0]["libelle_secondaire"] == chantier_en_cours["chantier"].nom
    logements = client.get("/api/pilotage/avancement/logements").json()
    assert logements[0]["libelle_cible"] == "A01"
    corps = client.get("/api/pilotage/avancement/corps-etat").json()
    assert [(x["libelle_cible"], x["pourcentage_valide"]) for x in corps] == [
        ("Gros œuvre", "37.500"),
        ("Finitions", "0.000"),
    ]


def test_les_alertes_listent_retards_et_blocages(
    client_authentifie: Client, chantier_en_cours: dict[str, Any]
) -> None:
    c = chantier_en_cours
    EtapeTravaux.objects.filter(pk=c["murs"].pk).update(
        date_prevue=timezone.localdate() - timedelta(days=3)
    )
    declarations.bloquer(c["encadrant"], c["peinture"].pk, "INTEMPERIES", commentaire="orage")
    alertes = client_authentifie().get("/api/pilotage/alertes-etapes").json()
    par_etape = {a["libelle_etape"]: a for a in alertes}
    assert par_etape["Murs"]["jours_de_retard"] == 3
    assert (
        par_etape["Peinture"]["statut"],
        par_etape["Peinture"]["code_motif_blocage"],
        par_etape["Peinture"]["commentaire"],
    ) == ("BLOQUEE", "INTEMPERIES", "orage")
    assert par_etape["Peinture"]["jours_de_retard"] == 0
