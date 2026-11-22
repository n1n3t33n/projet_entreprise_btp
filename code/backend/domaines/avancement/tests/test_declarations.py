"""Déclarations, blocages et contrôle des étapes (ET-1, RG-A2 à RG-A5,
RG-A9, RG-A10, RG-D11 ; EF-AVA-04 à 07, EF-AVA-10)."""

import uuid
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from django.conf import settings
from django.db import connection
from rest_framework.test import APIClient

from domaines.avancement.models import EtapeTravaux, EvenementExecution
from domaines.avancement.services import declarations, fiches
from domaines.identite.models import DroitAccorde, Equipe, MembreEquipe
from domaines.organisation.models import Logement
from domaines.referentiels.models import Article, UniteMesure

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def chantier_affecte(
    chantier_avancement: dict[str, Any], logement: Logement, fabrique_utilisateur: Any
) -> dict[str, Any]:
    """Les trois étapes du logement affectées au technicien ; le technicien a
    le droit de déclarer (api.etapes.modifier)."""
    DroitAccorde.objects.create(
        role_id="TECHNICIEN", permission_id="api.etapes.modifier", portee="GLOBALE"
    )
    etapes = list(EtapeTravaux.objects.filter(logement=logement).order_by("etape_modele__ordre"))
    fiches.affecter(
        fabrique_utilisateur(), [e.pk for e in etapes], chantier_avancement["technicien"], None
    )
    return {
        **chantier_avancement,
        "fondations": etapes[0],
        "murs": etapes[1],
        "peinture": etapes[2],
    }


def _declarer(client: APIClient, etape: EtapeTravaux, **champs: Any) -> Any:
    return client.post(f"/api/etapes/{etape.pk}/declaration", champs, format="json")


def _statut(etape: EtapeTravaux) -> str:
    etape.refresh_from_db()
    return etape.statut


# --- Déclaration (EF-AVA-04, Q-X) -----------------------------------------------------------
def test_une_etape_sans_controle_est_validee_implicitement(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    technicien = client_authentifie(utilisateur=chantier_affecte["technicien"])
    reponse = _declarer(technicien, chantier_affecte["murs"])
    assert reponse.status_code == 201
    assert [e["statut_apres"] for e in reponse.json()] == ["TERMINEE_DECLAREE", "VALIDEE"]
    assert reponse.json()[1]["commentaire"].startswith("Validation implicite")
    assert _statut(chantier_affecte["murs"]) == "VALIDEE"


def test_une_etape_a_controle_attend_le_chef(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    technicien = client_authentifie(utilisateur=chantier_affecte["technicien"])
    reponse = _declarer(technicien, chantier_affecte["fondations"])
    assert [e["statut_apres"] for e in reponse.json()] == ["TERMINEE_DECLAREE"]
    a_valider = client_authentifie().get("/api/avancement/etapes-a-valider").json()
    assert [e["id_etape"] for e in a_valider] == [str(chantier_affecte["fondations"].pk)]
    assert a_valider[0]["nom_auteur_declaration"] == chantier_affecte["technicien"].nom_complet


def test_une_declaration_rejouee_n_est_inscrite_qu_une_fois(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    technicien = client_authentifie(utilisateur=chantier_affecte["technicien"])
    cle = str(uuid.uuid4())
    assert _declarer(technicien, chantier_affecte["fondations"], uuid=cle).status_code == 201
    assert _declarer(technicien, chantier_affecte["fondations"], uuid=cle).status_code == 200
    assert EvenementExecution.objects.filter(statut_apres="TERMINEE_DECLAREE").count() == 1


def test_une_etape_non_commencee_ne_se_declare_pas(
    client_authentifie: Client, chantier_avancement: dict[str, Any], logement: Logement
) -> None:
    etape = EtapeTravaux.objects.filter(logement=logement).first()
    assert etape is not None
    reponse = _declarer(client_authentifie(), etape)
    assert reponse.status_code == 409
    assert reponse.json()["motif"] == "TRANSITION_IMPOSSIBLE"


# --- Qui déclare (RG-A3, RG-A9, EF-AVA-07) ----------------------------------------------------
def test_le_chef_d_equipe_declare_pour_son_equipier(
    client_authentifie: Client, chantier_affecte: dict[str, Any], fabrique_utilisateur: Any
) -> None:
    chef = fabrique_utilisateur(role="TECHNICIEN")
    equipe = Equipe.objects.create(code="GO-A", libelle="Gros œuvre A")
    MembreEquipe.objects.create(utilisateur=chef, equipe=equipe, est_chef_equipe=True)
    MembreEquipe.objects.create(utilisateur=chantier_affecte["technicien"], equipe=equipe)
    reponse = _declarer(client_authentifie(utilisateur=chef), chantier_affecte["murs"])
    declaration = reponse.json()[0]
    assert declaration["est_delegation"] is True
    assert declaration["nom_pour_le_compte_de"] == chantier_affecte["technicien"].nom_complet


def test_un_autre_technicien_ne_declare_pas(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    reponse = _declarer(client_authentifie("TECHNICIEN"), chantier_affecte["murs"])
    assert reponse.status_code == 403
    assert reponse.json()["motif"] == "DECLARATION_INTERDITE"


# --- Contrôle (EF-AVA-06, RG-A4, RG-D11) ----------------------------------------------------------
def _decider(client: APIClient, etape: EtapeTravaux, decision: str, **champs: Any) -> Any:
    return client.post(
        f"/api/etapes/{etape.pk}/validation", {"decision": decision, **champs}, format="json"
    )


def test_le_controle_valide_ou_rejette_avec_motif(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    technicien = client_authentifie(utilisateur=chantier_affecte["technicien"])
    chef = client_authentifie()
    _declarer(technicien, chantier_affecte["fondations"])
    assert _decider(chef, chantier_affecte["fondations"], "REFUSE").status_code == 400
    rejet = _decider(chef, chantier_affecte["fondations"], "REFUSE", motif="ferraillage incomplet")
    assert rejet.json()["statut_apres"] == "EN_COURS"
    assert rejet.json()["commentaire"] == "ferraillage incomplet"
    _declarer(technicien, chantier_affecte["fondations"])
    assert (
        _decider(chef, chantier_affecte["fondations"], "ACCEPTE").json()["statut_apres"]
        == "VALIDEE"
    )
    validee = EtapeTravaux.objects.get(pk=chantier_affecte["fondations"].pk)
    assert validee.date_validation is not None


def test_le_declarant_ne_controle_pas_sa_propre_etape(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    chef = client_authentifie()
    _declarer(chef, chantier_affecte["fondations"])  # déclaration par délégation
    reponse = _decider(chef, chantier_affecte["fondations"], "ACCEPTE")
    assert reponse.status_code == 403
    assert reponse.json()["motif"] == "SEPARATION_DES_TACHES"


def test_une_etape_sans_controle_n_attend_pas_de_decision(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    reponse = _decider(client_authentifie(), chantier_affecte["murs"], "ACCEPTE")
    assert reponse.status_code == 409


# --- Blocage (EF-AVA-05, RG-A10) ---------------------------------------------------------------------
def test_un_manque_de_materiel_reference_l_article_puis_se_leve(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    technicien = client_authentifie(utilisateur=chantier_affecte["technicien"])
    url = f"/api/etapes/{chantier_affecte['murs'].pk}/blocage"
    sans_article = technicien.post(url, {"code_motif": "MANQUE_MATERIEL"}, format="json")
    assert "article_id_article" in sans_article.json()["details"]
    unite = UniteMesure.objects.create(code_unite="SAC", libelle="sac", type_unite="MASSE")
    ciment = Article.objects.create(
        code="A1", designation="Ciment", origine="ACHAT", unite_mesure=unite
    )
    bloque = technicien.post(
        url,
        {
            "code_motif": "MANQUE_MATERIEL",
            "article_id_article": str(ciment.pk),
            "commentaire": "rupture",
        },
        format="json",
    )
    assert bloque.status_code == 201
    assert (bloque.json()["statut_apres"], bloque.json()["article_id_article"]) == (
        "BLOQUEE",
        str(ciment.pk),
    )
    levee = technicien.post(
        f"/api/etapes/{chantier_affecte['murs'].pk}/levee-blocage", {}, format="json"
    )
    assert levee.json()["statut_apres"] == "EN_COURS"


def test_l_historique_d_une_etape_est_complet(
    client_authentifie: Client, chantier_affecte: dict[str, Any]
) -> None:
    technicien = client_authentifie(utilisateur=chantier_affecte["technicien"])
    _declarer(technicien, chantier_affecte["murs"])
    historique = (
        client_authentifie().get(f"/api/etapes/{chantier_affecte['murs'].pk}/evenements").json()
    )
    assert [(e["statut_avant"], e["statut_apres"]) for e in historique] == [
        ("A_FAIRE", "EN_COURS"),
        ("EN_COURS", "TERMINEE_DECLAREE"),
        ("TERMINEE_DECLAREE", "VALIDEE"),
    ]


@pytest.fixture
def role_applicatif() -> Iterator[None]:
    with connection.cursor() as curseur:
        curseur.execute(f'SET ROLE "{settings.BD_ROLE_APPLICATION}"')
    try:
        yield
    finally:
        with connection.cursor() as curseur:
            curseur.execute("RESET ROLE")


def test_declarer_et_controler_sous_le_role_applicatif(
    chantier_affecte: dict[str, Any], fabrique_utilisateur: Any, role_applicatif: None
) -> None:
    """Verrou de ligne sur etape_travaux (table modifiable) et insertion au
    journal immuable : tout passe sous le rôle applicatif."""
    declarations.declarer_terminee(
        chantier_affecte["technicien"], chantier_affecte["fondations"].pk
    )
    evenement, _ = declarations.decider(
        fabrique_utilisateur(), chantier_affecte["fondations"].pk, "ACCEPTE", None
    )
    assert evenement.statut_apres == "VALIDEE"
