"""Fixtures du domaine avancement : un logement de type villa, une gamme
ACTIVE de trois étapes (dont une « à contrôle »), un technicien."""

from decimal import Decimal
from typing import Any

import pytest

from domaines.organisation.models import Logement, TypeLogement, Zone
from domaines.referentiels.models import CorpsEtat, EtapeModele, Gamme, MotifBlocage


@pytest.fixture
def chantier_avancement(chantier: Any, fabrique_utilisateur: Any) -> dict[str, Any]:
    villa = TypeLogement.objects.create(code_type="VILLA3", libelle="Villa 3 pièces")
    zone = Zone.objects.create(code="A", nom="Îlot A", type_zone="TRANCHE", chantier=chantier)
    gros_oeuvre = CorpsEtat.objects.create(code_corps_etat="GO", libelle="Gros œuvre", ordre=1)
    finitions = CorpsEtat.objects.create(code_corps_etat="FIN", libelle="Finitions", ordre=2)
    gamme = Gamme.objects.create(
        version=1, libelle="Villa standard", statut="ACTIVE", type_logement=villa
    )
    modeles = [
        EtapeModele.objects.create(
            code=code,
            libelle=libelle,
            ordre=ordre,
            poids=Decimal(poids),
            controle_requis=controle,
            gamme=gamme,
            corps_etat=corps,
        )
        for ordre, (code, libelle, poids, controle, corps) in enumerate(
            [
                ("T-01", "Fondations", 50, True, gros_oeuvre),
                ("T-02", "Murs", 30, False, gros_oeuvre),
                ("T-03", "Peinture", 20, False, finitions),
            ],
            start=1,
        )
    ]
    MotifBlocage.objects.create(
        code_motif="MANQUE_MATERIEL", libelle="Manque de matériel", requiert_article=True
    )
    MotifBlocage.objects.create(code_motif="INTEMPERIES", libelle="Intempéries")
    return {
        "chantier": chantier,
        "zone": zone,
        "villa": villa,
        "gamme": gamme,
        "modeles": modeles,
        "technicien": fabrique_utilisateur(role="TECHNICIEN"),
    }


@pytest.fixture
def logement(chantier_avancement: dict[str, Any]) -> Logement:
    return Logement.objects.create(
        numero="A01", zone=chantier_avancement["zone"], type_logement=chantier_avancement["villa"]
    )
