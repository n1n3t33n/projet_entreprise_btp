import type { Icon } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export type CardProps = {
  /** Intitulé de la carte. Rendu comme un titre de niveau `niveauTitre`. */
  titre?: ReactNode
  /** Phrase de contexte affichée sous l'intitulé. */
  description?: ReactNode
  /** Icône Phosphor facultative, affichée devant l'intitulé. */
  icone?: Icon
  /** Contrôles alignés à droite de l'en-tête (boutons, filtres). */
  actions?: ReactNode
  /** Bande de bas de carte, séparée par un filet. */
  pied?: ReactNode
  /** Contenu principal. */
  children?: ReactNode
  /** Supprime la marge intérieure du contenu : à utiliser pour un tableau. */
  sansRemplissage?: boolean
  /** Ajoute une élévation au survol, pour une carte cliquable. */
  survolable?: boolean
  /** Niveau du titre, à choisir selon la hiérarchie de l'écran. */
  niveauTitre?: 2 | 3 | 4
  className?: string
}

export function Card({
  titre,
  description,
  icone,
  actions,
  pied,
  children,
  sansRemplissage = false,
  survolable = false,
  niveauTitre = 3,
  className,
}: CardProps) {
  const Icone = icone
  const Titre = `h${niveauTitre}` as 'h2' | 'h3' | 'h4'
  const aUnEntete = Boolean(titre || description || actions)

  return (
    <section
      className={cn(
        'flex flex-col rounded-carte border border-bordure bg-surface shadow-douce',
        'transition-shadow duration-[var(--duree-survol)] ease-out',
        survolable && 'hover:shadow-levee',
        className,
      )}
    >
      {aUnEntete && (
        <header
          className={cn(
            'flex items-start justify-between gap-4 px-5 pt-5',
            !children && !pied && 'pb-5',
          )}
        >
          <div className="min-w-0 space-y-1">
            {titre && (
              <div className="flex items-center gap-2">
                {Icone && (
                  <Icone size={20} weight="regular" aria-hidden className="text-sarcelle" />
                )}
                <Titre className="text-base font-bold text-marine">{titre}</Titre>
              </div>
            )}
            {description && <p className="text-sm text-texte-secondaire">{description}</p>}
          </div>
          {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
        </header>
      )}

      {children && (
        <div
          className={cn(
            'min-w-0 flex-1',
            sansRemplissage ? '' : 'px-5 py-5',
            aUnEntete && !sansRemplissage && 'pt-4',
          )}
        >
          {children}
        </div>
      )}

      {pied && <footer className="border-t border-bordure px-5 py-3">{pied}</footer>}
    </section>
  )
}
