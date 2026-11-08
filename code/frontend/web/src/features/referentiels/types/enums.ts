/*
  Énumérations du domaine « Référentiels et catalogue ».

  Origine des valeurs — vérifiée sur les sources :
  - Les listes `CHECK` du MPD (MPD-2, MPD-3) sont les seules sources qui
    énumèrent des littéraux ; elles sont volontairement illustratives
    (« ∈ {ACHAT, PRODUCTION_INTERNE, RECUPERATION, …} »). Les diagrammes de
    classes (CL-2, CL-3a) nomment les types énumérés (`Origine`, `TypeUnite`,
    `TypeZone`, `Statut`) mais n'en définissent aucun littéral.
  - Le README de modélisation (§ 6.5) confirme : 15 types énumérés implémentés
    en `varchar` + contrainte `CHECK`, extensibles sans migration.

  Convention : l'application manipule des valeurs en minuscules (`achat`) ; la
  correspondance avec les libellés `UPPER_SNAKE` de la base est faite dans
  `api/mapping`. Aucun code n'est affiché tel quel (charte § 8).

  Incohérence signalée à l'étape 7 et résolue à l'étape 8 : le module `stock`
  employait `'local' | 'import'`, sans fondement dans la modélisation. Il
  utilise désormais les mêmes valeurs que ce module (MPD-3).
*/

/** Origine d'un article (MPD-3 `article.origine ∈ {ACHAT, PRODUCTION_INTERNE, RECUPERATION, …}`). */
export type OrigineArticle = 'achat' | 'production_interne' | 'recuperation'

/**
 * Type d'unité de mesure (MPD-3 `unite_mesure.type_unite ∈ {MASSE, VOLUME,
 * LONGUEUR, …}`). `unite` et `surface` complètent la liste illustrative du MPD
 * (le « … » l'autorise) et alignent ce module sur le module stock déjà livré,
 * qui emploie le même ensemble.
 */
export type TypeUnite = 'unite' | 'masse' | 'volume' | 'longueur' | 'surface'

/** Type d'une zone de chantier (MPD-2 `zone.type_zone ∈ {BATIMENT, NIVEAU, TRANCHE, …}`). */
export type TypeZone = 'batiment' | 'niveau' | 'tranche'

/**
 * Statut administratif d'un chantier (MPD-2 `chantier.statut ∈ {ACTIF,
 * INACTIF, OUVERT, …}`). Deux valeurs métier retenues parmi la liste
 * illustrative ; aucune valeur n'est inventée hors de cette liste.
 */
export type StatutChantier = 'actif' | 'inactif'

/**
 * Statut administratif d'un logement (MPD-2 `logement.statut`, même liste
 * `CHECK` générique que le chantier). Distinct de l'avancement des travaux, qui
 * est porté par les étapes (module avancement), non par cet attribut.
 */
export type StatutLogement = 'actif' | 'inactif'
