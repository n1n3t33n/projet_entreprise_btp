"""Valeurs énumérées du domaine « organisation du chantier ».

Chaque énuméré du MPD est un varchar(32) assorti d'une contrainte CHECK, et
non un type ENUM PostgreSQL (MPD § 6.5 : une contrainte CHECK se remplace,
un ENUM impose une migration de type). Les valeurs vivent ICI, dans un module
de constantes : la contrainte est construite à partir de ces tuples, si bien
qu'ajouter une valeur ne demande qu'une migration de contrainte.

PROVISOIRE — à arbitrer : le MPD-2 écrit ``ck_chantier_statut : statut ∈
{ACTIF, INACTIF, OUVERT, …}``, ensemble générique tronqué (incohérence I-12).
L'arbitrage Q8 n'a fixé que les énumérés du domaine identité. On retient ici
les trois valeurs explicitement écrites au MPD, sans en inventer d'autre.
"""

STATUT_CHANTIER_ACTIF = "ACTIF"
STATUT_CHANTIER_INACTIF = "INACTIF"
STATUT_CHANTIER_OUVERT = "OUVERT"

STATUTS_CHANTIER: tuple[str, ...] = (
    STATUT_CHANTIER_ACTIF,
    STATUT_CHANTIER_INACTIF,
    STATUT_CHANTIER_OUVERT,
)
