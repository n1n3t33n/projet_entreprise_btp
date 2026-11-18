"""Import CSV des référentiels (EF-ADM-02) : lecture du fichier, validation
ligne par ligne, écriture des lignes valides, journal d'audit."""

from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient

from domaines.identite.models import JournalAudit
from domaines.organisation.models import Chantier, Magasin
from domaines.referentiels.models import Article, CategorieArticle, UniteMesure

pytestmark = pytest.mark.django_db

Client = Callable[..., APIClient]


@pytest.fixture
def catalogue(db: Any) -> None:
    UniteMesure.objects.create(code_unite="SAC", libelle="sac", type_unite="MASSE")
    CategorieArticle.objects.create(code_categorie="GO-CIM", libelle="Ciment")


def _analyse(client: APIClient, cible: str, contenu: str) -> Any:
    return client.post("/api/import/analyse", {"cible": cible, "contenu": contenu}, format="json")


def _confirmation(client: APIClient, cible: str, contenu: str) -> Any:
    return client.post(
        "/api/import/confirmation", {"cible": cible, "contenu": contenu}, format="json"
    )


# --- Lecture du fichier ------------------------------------------------------------
def test_l_analyse_ne_ecrit_rien_et_rend_le_rapport(
    client_authentifie: Client, catalogue: None
) -> None:
    contenu = "code;designation;unite\nA1;Ciment;SAC\nA2;Inconnu;BIDON\n"
    corps = _analyse(client_authentifie(), "articles", contenu).json()
    assert corps["colonnes"] == ["code", "designation", "unite", "origine", "famille", "code_barre"]
    assert corps["lignes"][0] == {
        "numero": 1,
        "valeurs": ["A1", "Ciment", "SAC", "", "", ""],
        "erreur": None,
    }
    assert corps["lignes"][1]["erreur"] == "l'unité « BIDON » n'existe pas"
    assert (corps["nombre_valides"], corps["nombre_erreurs"]) == (1, 1)
    assert not Article.objects.exists()


def test_les_colonnes_se_lisent_par_leur_nom_avec_virgules_et_guillemets(
    client_authentifie: Client, catalogue: None
) -> None:
    contenu = 'unite,Designation,code\nSAC,"Ciment, sac 50 kg",A1\n'
    ligne = _analyse(client_authentifie(), "articles", contenu).json()["lignes"][0]
    assert ligne["valeurs"][:3] == ["A1", "Ciment, sac 50 kg", "SAC"]
    assert ligne["erreur"] is None


def test_une_colonne_inconnue_ou_manquante_refuse_le_fichier(
    client_authentifie: Client, catalogue: None
) -> None:
    client = client_authentifie()
    inconnue = _analyse(client, "articles", "code;designation;unite;seuil_minimal\n")
    assert inconnue.status_code == 400
    assert "seuil_minimal" in inconnue.json()["details"]["contenu"][0]
    manquante = _analyse(client, "articles", "code;designation\nA1;Ciment\n")
    assert manquante.status_code == 400
    assert "unite" in manquante.json()["details"]["contenu"][0]


def test_lignes_incompletes_vides_et_doublons_sont_signales(
    client_authentifie: Client, catalogue: None
) -> None:
    contenu = "code;designation;unite\nA1;Ciment;SAC\nA1;Autre;SAC\nA2;;SAC\nA3;Seul\n"
    lignes = _analyse(client_authentifie(), "articles", contenu).json()["lignes"]
    assert [ligne["erreur"] for ligne in lignes] == [
        None,
        "« A1 » apparaît deux fois dans le fichier",
        "« designation » est obligatoire",
        "2 colonne(s) au lieu de 3 dans l'en-tête",
    ]


def test_une_cible_inconnue_est_refusee(client_authentifie: Client) -> None:
    reponse = _analyse(client_authentifie(), "fournisseurs", "code\nX\n")
    assert reponse.status_code == 400
    assert "cible" in reponse.json()["details"]


def test_un_fichier_vide_est_refuse(client_authentifie: Client) -> None:
    reponse = _analyse(client_authentifie(), "articles", "\n\n")
    assert reponse.status_code == 400


# --- Confirmation ------------------------------------------------------------------
def test_la_confirmation_ecrit_les_lignes_valides_et_journalise(
    client_authentifie: Client, catalogue: None
) -> None:
    client = client_authentifie()
    contenu = (
        "code;designation;unite;origine;famille;code_barre\n"
        "A1;Ciment;SAC;production_interne;GO-CIM;600\n"
        "A2;Erreur;BIDON;;;\n"
    )
    reponse = _confirmation(client, "articles", contenu)
    assert reponse.json() == {"cible": "articles", "nombre_importees": 1}
    article = Article.objects.get(code="A1")
    assert (article.origine, article.categorie_article_id, article.code_barre) == (
        "PRODUCTION_INTERNE",
        "GO-CIM",
        "600",
    )
    entree = JournalAudit.objects.get(action="IMPORT_CSV")
    assert (entree.type_objet, entree.id_objet) == ("referentiel", "articles")
    assert entree.utilisateur_id == client.utilisateur.pk  # type: ignore[attr-defined]


def test_reimporter_met_a_jour_au_lieu_de_dupliquer(
    client_authentifie: Client, catalogue: None
) -> None:
    client = client_authentifie()
    _confirmation(client, "articles", "code;designation;unite\nA1;Ciment;SAC\n")
    _confirmation(client, "articles", "code;designation;unite\nA1;Ciment CPJ;SAC\n")
    assert list(Article.objects.values_list("code", "designation")) == [("A1", "Ciment CPJ")]


def test_un_code_barre_deja_porte_par_un_autre_article_est_refuse(
    client_authentifie: Client, catalogue: None
) -> None:
    Article.objects.create(
        code="A9", designation="Existant", origine="ACHAT", unite_mesure_id="SAC", code_barre="600"
    )
    contenu = "code;designation;unite;code_barre\nA1;Ciment;SAC;600\n"
    ligne = _analyse(client_authentifie(), "articles", contenu).json()["lignes"][0]
    assert ligne["erreur"] == "le code-barres est déjà porté par l'article « A9 »"


def test_sans_ligne_valide_rien_n_est_importe(client_authentifie: Client, catalogue: None) -> None:
    reponse = _confirmation(client_authentifie(), "articles", "code;designation;unite\nA1;X;NON\n")
    assert reponse.status_code == 409
    assert reponse.json()["motif"] == "RIEN_A_IMPORTER"
    assert not JournalAudit.objects.filter(action="IMPORT_CSV").exists()


def test_chantiers_puis_magasins(client_authentifie: Client) -> None:
    client = client_authentifie()
    chantiers = "code;nom;date_debut\nCH-1;Chantier 1;01/09/2026\nCH-2;Chantier 2;demain\n"
    assert _confirmation(client, "chantiers", chantiers).json()["nombre_importees"] == 1
    chantier = Chantier.objects.get(code="CH-1")
    assert (str(chantier.date_debut), chantier.statut) == ("2026-09-01", "ACTIF")
    magasins = "code;nom;chantier\nM-1;Magasin 1;CH-1\nM-2;Magasin 2;CH-X\n"
    rapport = _analyse(client, "magasins", magasins).json()
    assert rapport["lignes"][1]["erreur"] == "le chantier « CH-X » n'existe pas"
    assert _confirmation(client, "magasins", magasins).json()["nombre_importees"] == 1
    assert Magasin.objects.get(code="M-1").chantier_id == chantier.pk


def test_l_import_demande_son_droit(client_authentifie: Client) -> None:
    reponse = _analyse(client_authentifie("TECHNICIEN"), "articles", "code\n")
    assert reponse.status_code == 403
