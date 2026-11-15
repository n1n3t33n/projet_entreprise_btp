import { Desktop, Moon, Sun, type Icon } from '@phosphor-icons/react'
import { usePreferences, useT, type Theme } from '@/app/preferences-context'
import { LANGUES } from '@/i18n/dictionnaires'
import { cn } from '@/lib/cn'

const THEMES: { valeur: Theme; icone: Icon }[] = [
  { valeur: 'clair', icone: Sun },
  { valeur: 'systeme', icone: Desktop },
  { valeur: 'sombre', icone: Moon },
]

type ReglagesProps = {
  /** Vrai sur un fond marine (page de connexion). */
  surMarine?: boolean
}

/** Choix de la langue et du thème : deux groupes de boutons en pilule. */
export function Reglages({ surMarine = false }: ReglagesProps) {
  const t = useT()
  const { langue, theme, definirLangue, definirTheme } = usePreferences()

  const piste = surMarine ? 'bg-white/10' : 'bg-fond-alt'
  const repos = surMarine
    ? 'text-white/75 hover:text-white'
    : 'text-texte-secondaire hover:text-texte'
  const actif = surMarine
    ? 'bg-white text-encre shadow-douce'
    : 'bg-surface text-marine shadow-douce'
  const bouton =
    'flex h-8 items-center justify-center rounded-full px-2.5 text-xs font-semibold transition-colors duration-[var(--duree-bouton)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle'

  return (
    <div className="flex items-center gap-2">
      <div
        role="group"
        aria-label={t.reglages.langue}
        className={cn('flex rounded-full p-1', piste)}
      >
        {LANGUES.map((option) => (
          <button
            key={option.code}
            type="button"
            title={option.nom}
            aria-pressed={langue === option.code}
            onClick={() => definirLangue(option.code)}
            className={cn(bouton, 'uppercase', langue === option.code ? actif : repos)}
          >
            {option.code}
          </button>
        ))}
      </div>

      <div
        role="group"
        aria-label={t.reglages.theme}
        className={cn('flex rounded-full p-1', piste)}
      >
        {THEMES.map(({ valeur, icone: Icone }) => (
          <button
            key={valeur}
            type="button"
            title={t.reglages[valeur]}
            aria-label={t.reglages[valeur]}
            aria-pressed={theme === valeur}
            onClick={() => definirTheme(valeur)}
            className={cn(bouton, theme === valeur ? actif : repos)}
          >
            <Icone size={16} weight="regular" aria-hidden />
          </button>
        ))}
      </div>
    </div>
  )
}
