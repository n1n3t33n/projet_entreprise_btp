import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export type EnTetePageProps = {
  /** Intitulé de l'écran. */
  titre: string
  /** Phrase de contexte sous l'intitulé. */
  description?: string
  /** Information de contexte à droite du titre, par exemple une pilule de statut. */
  etiquette?: ReactNode
  /** Contrôles principaux de l'écran, alignés à droite. */
  actions?: ReactNode
  /**
   * Niveau du titre. `1` quand l'écran porte son propre titre, `2` quand la
   * barre supérieure de l'application affiche déjà le nom de la page.
   */
  niveauTitre?: 1 | 2
  className?: string
}

export function EnTetePage({
  titre,
  description,
  etiquette,
  actions,
  niveauTitre = 2,
  className,
}: EnTetePageProps) {
  const Titre = niveauTitre === 1 ? 'h1' : 'h2'

  return (
    <header className={cn('flex flex-wrap items-start justify-between gap-4', className)}>
      <div className="min-w-0 space-y-1">
        <div className="flex flex-wrap items-center gap-3">
          <Titre className="text-xl font-bold text-marine">{titre}</Titre>
          {etiquette}
        </div>
        {description && <p className="max-w-2xl text-sm text-texte-secondaire">{description}</p>}
      </div>

      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </header>
  )
}
