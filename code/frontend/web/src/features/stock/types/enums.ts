/*
  Énumérations du domaine « Stock et journal immuable ».

  Les valeurs sont dérivées de la modélisation (UML CL-4, états-transitions
  ET-2, MERISE MLD-4 / MPD-4). Les listes `CHECK` du MPD étant génériques
  (« {ACTIF, INACTIF, OUVERT, …} »), les valeurs métier réelles proviennent des
  diagrammes de classes et d'états, qui font foi.

  Convention : côté application on manipule des valeurs en minuscules
  (`a_valider`), la correspondance avec les libellés `UPPER_SNAKE` de la base
  est faite dans la couche `api/mapping`. Aucun de ces codes n'est affiché tel
  quel à l'écran (charte § 8 : « aucun code interne affiché »).
*/

/**
 * Statut de validation d'un mouvement de stock (ET-2).
 *
 * `en_alerte` est l'état d'un mouvement resté 24 h sans décision ; il est
 * distinct du niveau de stock et de la relance de validation (voir
 * `presentation/libelles`).
 */
export type StatutValidationMouvement =
  | 'enregistre'
  | 'a_valider'
  | 'en_alerte'
  | 'valide'
  | 'rejete'
  | 'annule'

/** Décision portée par un événement de validation (CL-4, MPD-4 `decision`). */
export type DecisionValidation = 'acceptee' | 'refusee'

/**
 * Sens d'un type de mouvement.
 *
 * Dérivé de `TypeMouvement.sens` (int au modèle) : une entrée augmente le
 * stock, une sortie le diminue.
 */
export type SensMouvement = 'entree' | 'sortie'

/** Nature d'une alerte de seuil (MPD-4 `ck_alerte_type_alerte`). */
export type TypeAlerteSeuil = 'seuil_minimal' | 'seuil_critique' | 'stock_negatif'

/** Statut d'une alerte de seuil. */
export type StatutAlerteSeuil = 'ouverte' | 'traitee' | 'ignoree'

/** Statut d'un inventaire (CL-4 `Inventaire.statut`). */
export type StatutInventaire = 'ouvert' | 'en_cours' | 'valide' | 'clos'

/** Statut d'une ligne d'inventaire (CL-4 `LigneInventaire.statut`). */
export type StatutLigneInventaire = 'a_compter' | 'comptee' | 'ecart' | 'ajustee'

/**
 * Origine d'un article (CL-3a `Article.origine : Origine`, littéraux du MPD-3
 * `article.origine ∈ {ACHAT, PRODUCTION_INTERNE, RECUPERATION, …}`).
 *
 * Corrigé à l'étape 8 : la version précédente (`'local' | 'import'`) n'avait
 * aucun fondement dans la modélisation. Les valeurs sont désormais identiques
 * à celles du module référentiels, qui est le propriétaire du catalogue.
 */
export type OrigineArticle = 'achat' | 'production_interne' | 'recuperation'

/** Type d'unité de mesure (CL-3a `UniteMesure.typeUnite`). */
export type TypeUnite = 'unite' | 'masse' | 'volume' | 'longueur' | 'surface'
