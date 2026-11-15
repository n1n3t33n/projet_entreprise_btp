/*
  Libellés d'interface du module parametrage.
*/

import type { OperateurRegle, TypeEvenement, TypeValeur } from '@/features/parametrage/types'
import { tr } from '@/i18n/tr'

export const LIBELLE_TYPE_VALEUR: Record<TypeValeur, string> = {
  entier: tr('Entier'),
  decimal: tr('Décimal'),
  booleen: tr('Booléen'),
  texte: tr('Texte'),
}

export const TYPES_VALEUR: { valeur: TypeValeur; libelle: string }[] = [
  { valeur: 'entier', libelle: tr('Entier') },
  { valeur: 'decimal', libelle: tr('Décimal') },
  { valeur: 'booleen', libelle: tr('Booléen') },
  { valeur: 'texte', libelle: tr('Texte') },
]

export const LIBELLE_EVENEMENT: Record<TypeEvenement, string> = {
  declaration_etape: tr("Déclaration d'une étape"),
  validation_etape: tr("Validation d'une étape"),
  ecart_inventaire: tr("Écart d'inventaire"),
  mouvement_stock: tr('Mouvement de stock'),
}

export const TYPES_EVENEMENT: { valeur: TypeEvenement; libelle: string }[] = [
  { valeur: 'declaration_etape', libelle: tr("Déclaration d'une étape") },
  { valeur: 'validation_etape', libelle: tr("Validation d'une étape") },
  { valeur: 'ecart_inventaire', libelle: tr("Écart d'inventaire") },
  { valeur: 'mouvement_stock', libelle: tr('Mouvement de stock') },
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
  { valeur: 'inferieur_egal', libelle: tr('≤ (inférieur ou égal)') },
  { valeur: 'superieur_egal', libelle: tr('≥ (supérieur ou égal)') },
  { valeur: 'egal', libelle: '= (égal)' },
  { valeur: 'inferieur', libelle: '< (inférieur)' },
  { valeur: 'superieur', libelle: '> (supérieur)' },
]
