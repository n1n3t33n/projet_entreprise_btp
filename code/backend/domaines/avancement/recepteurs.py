"""Réactions du domaine avancement aux événements des autres domaines.

Branchées dans ``apps.ready()`` : l'avancement connaît l'organisation et les
référentiels, jamais l'inverse (règle de modularité).
  * un logement créé reçoit ses étapes si une gamme active existe (RG-A1) ;
  * une gamme publiée donne leurs étapes aux logements de son type qui n'en
    ont pas encore (Q-AA).
"""

from typing import Any

from domaines.avancement.services import instanciation


def logement_enregistre(sender: Any, instance: Any, created: bool, **options: Any) -> None:
    if created and not options.get("raw"):
        instanciation.generer(instance)


def gamme_publiee(sender: Any, gamme: Any, **options: Any) -> None:
    instanciation.generer_pour_le_type(gamme.type_logement_id)
