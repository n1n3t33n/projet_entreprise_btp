"""Jeu de référence de l'avancement téléchargé par le mobile (EF-SYN-04) :
les fiches de route ouvertes du technicien et leurs étapes, sous la forme
de ``GET /api/fiches-route``. Déclaré par ``avancement/apps.py``."""

from typing import Any

from domaines.avancement import selecteurs
from domaines.avancement.api import serialiseurs as s
from domaines.avancement.constantes import FICHE_OUVERTE
from socle.synchronisation import JeuReference


def fiches_route(utilisateur: Any) -> Any:
    ouvertes = selecteurs.fiches(utilisateur.pk).filter(statut=FICHE_OUVERTE)
    return s.FicheRouteSerializer(ouvertes, many=True).data


JEUX = (JeuReference("fiches_route", fiches_route, "fiches-route"),)
