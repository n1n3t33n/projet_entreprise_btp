"""Jeu de référence du stock téléchargé par le mobile (EF-SYN-04) : le
stock courant des magasins couverts par le droit de lecture, sous la forme
de ``GET /api/stock/arborescence``. Déclaré par ``stock/apps.py``."""

from typing import Any

from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.stock import selecteurs
from domaines.stock.api import serialiseurs as s
from domaines.stock.services import acces
from socle.synchronisation import JeuReference


def stock(utilisateur: Any) -> Any:
    couverts = acces.magasins_couverts(utilisateur, "stock", "LIRE")
    magasins = selecteurs_organisation.magasins().select_related("chantier")
    if couverts is not None:
        magasins = magasins.filter(id_magasin__in=couverts)
    return s.NoeudStockSerializer(selecteurs.arborescence(magasins), many=True).data


JEUX = (JeuReference("stock", stock, "stock"),)
