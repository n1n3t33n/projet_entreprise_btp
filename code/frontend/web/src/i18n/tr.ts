/*
  Traduction des écrans métier à partir du texte français.

  `tr('Enregistrer')` rend « Save » en anglais, « Salva » en italien, et le
  texte français tel quel si la traduction manque : un écran n'est donc jamais
  cassé par un oubli. La langue est lue une fois, au chargement de la page ;
  changer de langue recharge la page, ce qui garde ce module utilisable partout
  — y compris dans les constantes déclarées hors des composants.
*/

import { estLangue, type Langue } from '@/i18n/dictionnaires'
import { TEXTES_EN } from '@/i18n/textes.en'
import { TEXTES_IT } from '@/i18n/textes.it'

export const CLE_LANGUE = 'chantiersync.langue'

function lireLangue(): Langue {
  try {
    const enregistree = window.localStorage.getItem(CLE_LANGUE)
    if (estLangue(enregistree)) {
      return enregistree
    }
  } catch {
    // Stockage indisponible (navigation privée) : on suit le navigateur.
  }
  const navigateur = window.navigator.language.slice(0, 2)
  return estLangue(navigateur) ? navigateur : 'fr'
}

/** Langue de la page, fixée au chargement. */
export const LANGUE_COURANTE: Langue = lireLangue()

const TABLES: Record<Langue, Record<string, string> | null> = {
  fr: null,
  en: TEXTES_EN,
  it: TEXTES_IT,
}

/** Code de langue pour les formats de date et de nombre. */
export const LOCALE_COURANTE = { fr: 'fr-FR', en: 'en-GB', it: 'it-IT' }[LANGUE_COURANTE]

/**
 * Traduit un texte d'interface écrit en français. Les variables entre
 * accolades sont remplacées : `tr('{n} articles', { n: 12 })`.
 */
export function tr(texte: string, variables?: Record<string, string | number>): string {
  const traduit = TABLES[LANGUE_COURANTE]?.[texte] ?? texte
  if (!variables) {
    return traduit
  }
  return traduit.replace(/\{(\w+)\}/g, (entier, nom: string) =>
    nom in variables ? String(variables[nom]) : entier,
  )
}
