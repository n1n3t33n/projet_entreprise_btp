"""Décision, annulation et relance des mouvements (EF-STK-09, EF-STK-11,
ET-2, RG-S6, RG-S8, RG-D8)."""

import uuid
from collections.abc import Callable, Iterator
from datetime import timedelta
from typing import Any

import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.utils import timezone
from rest_framework.test import APIClient

from domaines.organisation.models import ParametreChantier
from domaines.stock.models import Alerte, EvenementValidation, MouvementStock
from domaines.stock.services import relance, validation
from domaines.stock.tests.outils import corps_mouvement, corps_sortie, stock_de
from socle.models import ExecutionTraitement

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def saisie(client_authentifie: Client, chantier_stock: dict[str, Any]) -> dict[str, Any]:
    """Un magasinier (administrateur ici, pour les droits) réceptionne 500 puis
    sort 150 : la sortie dépasse la règle de validation (100)."""
    auteur = client_authentifie()
    auteur.post(
        "/api/mouvements", corps_mouvement(chantier_stock, "ENT_RECEPTION", "500"), format="json"
    )
    sortie = auteur.post(
        "/api/mouvements", corps_sortie(chantier_stock, "150"), format="json"
    ).json()
    return {"auteur": auteur, "sortie": sortie, **chantier_stock}


def _decider(client: APIClient, uuid_mouvement: str, decision: str, **champs: Any) -> Any:
    return client.post(
        f"/api/mouvements/{uuid_mouvement}/validation",
        {"decision": decision, **champs},
        format="json",
    )


# --- Décision (EF-STK-09, RG-D8) --------------------------------------------------------
def test_un_autre_valideur_accepte_la_sortie(
    client_authentifie: Client, saisie: dict[str, Any]
) -> None:
    valideur = client_authentifie()
    a_valider = valideur.get("/api/mouvements/a-valider").json()
    assert [m["uuid"] for m in a_valider] == [saisie["sortie"]["uuid"]]
    reponse = _decider(valideur, saisie["sortie"]["uuid"], "ACCEPTE")
    assert reponse.status_code == 200
    assert reponse.json()["statut_validation"] == "VALIDE"
    evenement = EvenementValidation.objects.get()
    assert evenement.regle_validation is not None
    assert valideur.get("/api/mouvements/a-valider").json() == []


def test_l_auteur_ne_valide_pas_sa_propre_sortie(saisie: dict[str, Any]) -> None:
    reponse = _decider(saisie["auteur"], saisie["sortie"]["uuid"], "ACCEPTE")
    assert reponse.status_code == 403
    assert reponse.json()["motif"] == "SEPARATION_DES_TACHES"


def test_un_refus_exige_un_motif_et_ne_touche_pas_au_stock(
    client_authentifie: Client, saisie: dict[str, Any]
) -> None:
    valideur = client_authentifie()
    assert _decider(valideur, saisie["sortie"]["uuid"], "REFUSE").status_code == 400
    refus = _decider(valideur, saisie["sortie"]["uuid"], "REFUSE", motif="quantité excessive")
    assert refus.json()["statut_validation"] == "REJETE"
    assert stock_de(saisie).quantite == 350


def test_on_ne_decide_pas_deux_fois(client_authentifie: Client, saisie: dict[str, Any]) -> None:
    valideur = client_authentifie()
    _decider(valideur, saisie["sortie"]["uuid"], "ACCEPTE")
    seconde = _decider(valideur, saisie["sortie"]["uuid"], "REFUSE", motif="x")
    assert seconde.status_code == 409
    assert seconde.json()["motif"] == "DECISION_IMPOSSIBLE"


def test_une_decision_rejouee_n_est_inscrite_qu_une_fois(
    client_authentifie: Client, saisie: dict[str, Any]
) -> None:
    valideur = client_authentifie()
    cle = str(uuid.uuid4())
    assert _decider(valideur, saisie["sortie"]["uuid"], "ACCEPTE", uuid=cle).status_code == 200
    assert _decider(valideur, saisie["sortie"]["uuid"], "ACCEPTE", uuid=cle).status_code == 200
    assert EvenementValidation.objects.count() == 1


@pytest.fixture
def role_applicatif() -> Iterator[None]:
    with connection.cursor() as curseur:
        curseur.execute(f'SET ROLE "{settings.BD_ROLE_APPLICATION}"')
    try:
        yield
    finally:
        with connection.cursor() as curseur:
            curseur.execute("RESET ROLE")


def test_la_decision_fonctionne_sous_le_role_applicatif(
    fabrique_utilisateur: Any, saisie: dict[str, Any], role_applicatif: None
) -> None:
    """Le verrou est consultatif : un SELECT … FOR UPDATE échouerait, le rôle
    applicatif n'ayant pas le droit UPDATE sur le journal des mouvements."""
    valideur = fabrique_utilisateur()
    mouvement = validation.decider(valideur, saisie["sortie"]["uuid"], "ACCEPTE", None)
    assert mouvement.derniere_decision == "ACCEPTE"  # type: ignore[attr-defined]


# --- Annulation par contre-mouvement (RG-S8, EF-STK-11) ----------------------------------
def test_annuler_une_sortie_remet_le_stock_et_la_marque_annulee(
    client_authentifie: Client, saisie: dict[str, Any]
) -> None:
    gestionnaire = client_authentifie()
    url = f"/api/mouvements/{saisie['sortie']['uuid']}/annulation"
    assert gestionnaire.post(url, {}, format="json").status_code == 400  # motif obligatoire
    contre = gestionnaire.post(url, {"motif": "saisie en double"}, format="json")
    assert contre.status_code == 201
    corps = contre.json()
    assert corps["type_mouvement_code_type_mouvement"] == "ANN_PLUS"
    assert corps["mouvement_annule_uuid"] == saisie["sortie"]["uuid"]
    assert stock_de(saisie).quantite == 500
    origine = gestionnaire.get("/api/mouvements", {"article": str(saisie["ciment"].pk)}).json()
    statuts = {m["uuid"]: m["statut_validation"] for m in origine}
    assert statuts[saisie["sortie"]["uuid"]] == "ANNULE"
    assert gestionnaire.post(url, {"motif": "encore"}, format="json").status_code == 409
    contre_url = f"/api/mouvements/{corps['uuid']}/annulation"
    assert gestionnaire.post(contre_url, {"motif": "x"}, format="json").status_code == 409


# --- Relance (ET-2, Q-F) ------------------------------------------------------------------
@pytest.fixture
def sortie_ancienne(client_authentifie: Client, chantier_stock: dict[str, Any]) -> str:
    """Sortie à valider saisie il y a 30 h ; délai de relance du chantier : 24 h."""
    ParametreChantier.objects.create(
        cle="delai_relance_validation_h",
        valeur="24",
        type_valeur="ENTIER",
        chantier=chantier_stock["magasin"].chantier,
    )
    il_y_a_30_h = (timezone.now() - timedelta(hours=30)).isoformat()
    corps = client_authentifie().post(
        "/api/mouvements",
        corps_sortie(chantier_stock, "150", date_operation=il_y_a_30_h),
        format="json",
    )
    return str(corps.json()["uuid"])


def test_une_sortie_sans_decision_passe_en_alerte_et_est_relancee(
    client_authentifie: Client, sortie_ancienne: str
) -> None:
    valideur = client_authentifie()
    a_valider = valideur.get("/api/mouvements/a-valider").json()
    assert a_valider[0]["statut_validation"] == "EN_ALERTE"
    assert relance.relancer().startswith("1 mouvement(s) en retard")
    relance.relancer()  # rejouable : pas de seconde alerte
    ouvertes = Alerte.objects.filter(type_alerte="VALIDATION_EN_RETARD", statut="OUVERTE")
    assert ouvertes.count() == 1
    _decider(valideur, sortie_ancienne, "ACCEPTE")
    assert not ouvertes.exists()


def test_la_relance_est_un_traitement_planifie(sortie_ancienne: str) -> None:
    call_command("lancer_traitement", "relancer_validations")
    execution = ExecutionTraitement.objects.get(nom_traitement="relancer_validations")
    assert execution.statut == "REUSSI"


def test_sans_delai_defini_pas_de_relance_mais_une_alerte_technique(
    client_authentifie: Client,
    chantier_stock: dict[str, Any],
    settings: Any,
    mailoutbox: list[Any],
) -> None:
    settings.ALERTES_DESTINATAIRES = ["exploitation@example.test"]
    il_y_a_30_h = (timezone.now() - timedelta(hours=30)).isoformat()
    client_authentifie().post(
        "/api/mouvements",
        corps_sortie(chantier_stock, "150", date_operation=il_y_a_30_h),
        format="json",
    )
    assert relance.relancer().startswith("0 mouvement(s)")
    assert any("Paramètre de chantier manquant" in mail.subject for mail in mailoutbox)
    assert MouvementStock.objects.filter(statut_validation="A_VALIDER").count() == 1
