"""MPD-5 en base : journal d'exécution immuable (RG-A5, RG-S8), partition
mensuelle sur l'heure du serveur (Q-U), contraintes de l'avancement."""

from collections.abc import Iterator
from typing import Any

import pytest
from django.conf import settings
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.utils import timezone

from domaines.avancement.models import AvancementAgrege, EtapeTravaux, EvenementExecution

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def evenement(chantier_avancement: dict[str, Any], logement: Any) -> EvenementExecution:
    etape = EtapeTravaux.objects.create(
        logement=logement, etape_modele=chantier_avancement["modeles"][0]
    )
    agregat = AvancementAgrege.objects.create(portee="LOGEMENT", id_cible=str(logement.pk))
    return EvenementExecution.objects.create(
        statut_avant="A_FAIRE",
        statut_apres="EN_COURS",
        etape_travaux=etape,
        utilisateur=chantier_avancement["technicien"],
        avancement_agrege=agregat,
    )


@pytest.fixture
def role_applicatif() -> Iterator[None]:
    with connection.cursor() as curseur:
        curseur.execute(f'SET ROLE "{settings.BD_ROLE_APPLICATION}"')
    try:
        yield
    finally:
        with connection.cursor() as curseur:
            curseur.execute("RESET ROLE")


def _doit_echouer(sql: str) -> None:
    with pytest.raises(DatabaseError), transaction.atomic(), connection.cursor() as curseur:
        curseur.execute(sql)


def _partition() -> str:
    return "evenement_execution_" + timezone.now().strftime("%Y_%m")


@pytest.mark.parametrize("table", ["evenement_execution", "partition"])
def test_le_role_applicatif_ne_peut_ni_modifier_ni_supprimer_ni_vider(
    evenement: EvenementExecution, role_applicatif: None, table: str
) -> None:
    nom = _partition() if table == "partition" else table
    _doit_echouer(f"UPDATE {nom} SET commentaire = 'x'")
    _doit_echouer(f"DELETE FROM {nom}")
    _doit_echouer(f"TRUNCATE {nom}")


def test_meme_le_proprietaire_est_arrete_par_les_declencheurs(
    evenement: EvenementExecution,
) -> None:
    _doit_echouer("UPDATE evenement_execution SET commentaire = 'x'")
    _doit_echouer("DELETE FROM evenement_execution")


def test_un_evenement_tombe_dans_la_partition_du_mois_serveur(
    evenement: EvenementExecution,
) -> None:
    with connection.cursor() as curseur:
        curseur.execute(f"SELECT count(*) FROM {_partition()}")  # noqa: S608
        assert curseur.fetchone()[0] == 1


def test_un_statut_hors_liste_est_refuse(evenement: EvenementExecution) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        EvenementExecution.objects.create(
            statut_apres="LIVREE",
            etape_travaux=evenement.etape_travaux,
            utilisateur=evenement.utilisateur,
            avancement_agrege=evenement.avancement_agrege,
        )


def test_une_etape_modele_ne_s_instancie_qu_une_fois_par_logement(
    evenement: EvenementExecution,
) -> None:
    etape = evenement.etape_travaux
    with pytest.raises(IntegrityError), transaction.atomic():
        EtapeTravaux.objects.create(logement=etape.logement, etape_modele=etape.etape_modele)


def test_un_agregat_par_portee_et_par_cible(evenement: EvenementExecution) -> None:
    agregat = evenement.avancement_agrege
    with pytest.raises(IntegrityError), transaction.atomic():
        AvancementAgrege.objects.create(portee=agregat.portee, id_cible=agregat.id_cible)
