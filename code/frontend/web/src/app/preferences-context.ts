/*
  Préférences d'affichage : langue et thème (clair, sombre, ou celui du
  système). Elles sont propres au navigateur et conservées localement.
*/

import { createContext, useContext } from 'react'
import { DICTIONNAIRES, type Dictionnaire, type Langue } from '@/i18n/dictionnaires'

export type Theme = 'clair' | 'sombre' | 'systeme'

export type PreferencesContexteValeur = {
  langue: Langue
  theme: Theme
  definirLangue: (langue: Langue) => void
  definirTheme: (theme: Theme) => void
}

export const PreferencesContexte = createContext<PreferencesContexteValeur | null>(null)

export function usePreferences(): PreferencesContexteValeur {
  const contexte = useContext(PreferencesContexte)
  if (!contexte) {
    throw new Error("usePreferences doit être utilisé à l'intérieur de PreferencesProvider.")
  }
  return contexte
}

/** Textes de l'interface dans la langue choisie. */
export function useT(): Dictionnaire {
  return DICTIONNAIRES[usePreferences().langue]
}
