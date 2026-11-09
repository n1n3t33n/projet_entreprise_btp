/*
  Énumérations du domaine parametrage.

  `TypeValeur` est contraint par le MPD (ENTIER, DECIMAL, BOOLEEN, …). Les deux
  autres listes (type d'événement, opérateur) ne sont pas contraintes par le
  modèle : ce sont des varchar libres. Les valeurs ci-dessous sont un jeu de
  départ cohérent avec les événements du système, à confirmer avec le cahier des
  charges (signalé dans le backlog).
*/

export type TypeValeur = 'entier' | 'decimal' | 'booleen' | 'texte'

/** Type d'événement sur lequel porte une règle de validation. */
export type TypeEvenement =
  'declaration_etape' | 'validation_etape' | 'ecart_inventaire' | 'mouvement_stock'

/** Opérateur de comparaison d'une règle de validation. */
export type OperateurRegle =
  'inferieur_egal' | 'superieur_egal' | 'egal' | 'inferieur' | 'superieur'
