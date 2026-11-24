"""Déclaration du domaine « pilotage »."""

from django.apps import AppConfig


class ConfigurationPilotage(AppConfig):
    """Pilotage transverse : rapport hebdomadaire et indicateurs d'usage
    (EF-DSH-06, EF-DSH-07). Aucune table : il assemble les rubriques que les
    domaines déclarent (socle/indicateurs.py) et n'importe aucun domaine."""

    name = "domaines.pilotage"
    label = "pilotage"
    verbose_name = "Pilotage"

    def ready(self) -> None:
        from domaines.pilotage.services import rapports
        from socle.traitements import declarer_traitement

        # Le lundi : annonce du rapport de la semaine écoulée (MOT, I-29, Q-AT).
        declarer_traitement("preparer_rapport_hebdomadaire", rapports.annoncer)
