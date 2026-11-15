import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { PreferencesContexte, type Theme } from '@/app/preferences-context'
import type { Langue } from '@/i18n/dictionnaires'
import { CLE_LANGUE, LANGUE_COURANTE } from '@/i18n/tr'

const CLE_THEME = 'chantiersync.theme'

/** Lit une préférence ; le stockage peut être indisponible (navigation privée). */
function lire(cle: string): string | null {
  try {
    return window.localStorage.getItem(cle)
  } catch {
    return null
  }
}

function ecrire(cle: string, valeur: string): void {
  try {
    window.localStorage.setItem(cle, valeur)
  } catch {
    // Préférence non conservée : l'interface reste utilisable.
  }
}

function themeInitial(): Theme {
  const enregistre = lire(CLE_THEME)
  return enregistre === 'clair' || enregistre === 'sombre' ? enregistre : 'systeme'
}

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [langue, setLangue] = useState<Langue>(LANGUE_COURANTE)
  const [theme, setTheme] = useState<Theme>(themeInitial)

  // Le thème est porté par un attribut de la racine du document : les jetons
  // de couleur de la feuille de style en dépendent.
  useEffect(() => {
    const racine = document.documentElement
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const appliquer = () => {
      const sombre = theme === 'sombre' || (theme === 'systeme' && media.matches)
      racine.dataset.theme = sombre ? 'sombre' : 'clair'
    }
    appliquer()
    media.addEventListener('change', appliquer)
    return () => media.removeEventListener('change', appliquer)
  }, [theme])

  useEffect(() => {
    document.documentElement.lang = langue
  }, [langue])

  const valeur = useMemo(
    () => ({
      langue,
      theme,
      definirLangue: (suivante: Langue) => {
        setLangue(suivante)
        ecrire(CLE_LANGUE, suivante)
        // Les textes des écrans sont résolus au chargement : on recharge la page.
        if (suivante !== LANGUE_COURANTE) {
          window.location.reload()
        }
      },
      definirTheme: (suivant: Theme) => {
        setTheme(suivant)
        ecrire(CLE_THEME, suivant)
      },
    }),
    [langue, theme],
  )

  return <PreferencesContexte.Provider value={valeur}>{children}</PreferencesContexte.Provider>
}
