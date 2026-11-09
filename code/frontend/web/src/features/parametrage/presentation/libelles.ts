/*
  Libellés d'interface du module parametrage.
*/

import type { OperateurRegle, TypeEvenement, TypeValeur } from '@/features/parametrage/types'

export const LIBELLE_TYPE_VALEUR: Record<TypeValeur, string> = {
  entier: 'Entier',
  decimal: 'Décimal',
  booleen: 'Booléen',
  texte: 'Texte',
}

export const TYPES_VALEUR: { valeur: TypeValeur; libelle: string }[] = [
  { valeur: 'entier', libelle: 'Entier' },
  { valeur: 'decimal', libelle: 'Décimal' },
  { valeur: 'booleen', libelle: 'Booléen' },
  { valeur: 'texte', libelle: 'Texte' },
]

export const LIBELLE_EVENEMENT: Record<TypeEvenement, string> = {
  declaration_etape: "Déclaration d'une étape",
  validation_etape: "Validation d'une étape",
  ecart_inventaire: "Écart d'inventaire",
  mouvement_stock: 'Mouvement de stock',
}

export const TYPES_EVENEMENT: { valeur: TypeEvenement; libelle: string }[] = [
  { valeur: 'declaration_etape', libelle: "Déclaration d'une étape" },
  { valeur: 'validation_etape', libelle: "Validation d'une étape" },
  { valeur: 'ecart_inventaire', libelle: "Écart d'inventaire" },
  { valeur: 'mouvement_stock', libelle: 'Mouvement de stock' },
]

/** Symbole lisible de l'opérateur, pour l'affichage d'une règle. */
export const SYMBOLE_OPERATEUR: Record<OperateurRegle, string> = {
  inferieur_egal: '≤',
  superieur_egal: '≥',
  egal: '=',
  inferieur: '<',
  superieur: '>',
}

export const OPERATEURS: { valeur: OperateurRegle; libelle: string }[] = [
  { valeur: 'inferieur_egal', libelle: '≤ (inférieur ou égal)' },
  { valeur: 'superieur_egal', libelle: '≥ (supérieur ou égal)' },
  { valeur: 'egal', libelle: '= (égal)' },
  { valeur: 'inferieur', libelle: '< (inférieur)' },
  { valeur: 'superieur', libelle: '> (supérieur)' },
]
