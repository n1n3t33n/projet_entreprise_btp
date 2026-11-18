"""Domaine « organisation du chantier » (CL-2, MPD-2).

En B1, seulement ``chantier`` et ``magasin`` : ce sont les tables socles dont
dépend l'identité (``perimetre`` délimite un chantier ou un magasin, README
§ 9.3 ; rapport B0 § 5.1). Le reste du MPD-2 (zone, logement, type de
logement, paramètres, acquéreur) arrive en B2 dans une migration suivante,
sans toucher à celles-ci.
"""
