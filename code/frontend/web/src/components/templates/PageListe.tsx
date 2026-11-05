import type { ReactNode } from 'react'
import { EnTetePage } from '@/components/templates/EnTetePage'
import { delaiCascade } from '@/components/ui/motion'
import { cn } from '@/lib/cn'

export type PageListeProps = {
  /** Intitulé de l'écran. */
  titre: string
  /** Phrase de contexte sous l'intitulé. */
  description?: string
  /** Information de contexte à droite du titre. */
  etiquette?: ReactNode
  /**
   * Contrôles d'écriture de l'écran (créer, importer, valider).
   * Ignorés quand `lectureSeule` est vrai : c'est ce qui permet de servir le
   * même écran à un rôle consultant sans en écrire une seconde version.
   */
  actions?: ReactNode
  /** Rangée d'indicateurs, généralement des `KpiCard`. */
  indicateurs?: ReactNode
  /** Barre de filtres, généralement des `FilterPill` et un champ de recherche. */
  filtres?: ReactNode
  /** Contenu principal : un tableau, une liste de cartes, un arbre. */
  children: ReactNode
  /** Retire les actions d'écriture de l'écran. */
  lectureSeule?: boolean
  className?: string
}

/**
 * Gabarit des écrans de consultation : en-tête, indicateurs, filtres, contenu.
 *
 * Premier gabarit dégagé du lot de maquettes : la majorité des écrans du poste
 * de pilotage suivent cette même ossature. Les modules la composent avec leurs
 * propres données au lieu de recopier la mise en page.
 */
export function PageListe({
  titre,
  description,
  etiquette,
  actions,
  indicateurs,
  filtres,
  children,
  lectureSeule = false,
  className,
}: PageListeProps) {
  /*
    Les bandes entrent en cascade : chacune porte la même animation, décalée
    par sa position. Le regard suit ainsi la construction de l'écran de haut en
    bas au lieu de recevoir tout le contenu d'un seul coup.
  */
  let position = 0
  const prochainDelai = () => {
    const delai = delaiCascade(position)
    position += 1
    return delai
  }

  return (
    <div className={cn('flex min-w-0 flex-col gap-6', className)}>
      <div className="animate-cascade" style={prochainDelai()}>
        <EnTetePage
          titre={titre}
          description={description}
          etiquette={etiquette}
          actions={lectureSeule ? undefined : actions}
        />
      </div>

      {indicateurs && (
        <div
          className="animate-cascade grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
          style={prochainDelai()}
        >
          {indicateurs}
        </div>
      )}

      {filtres && (
        <div className="animate-cascade flex flex-wrap items-center gap-2" style={prochainDelai()}>
          {filtres}
        </div>
      )}

      <div className="animate-cascade min-w-0" style={prochainDelai()}>
        {children}
      </div>
    </div>
  )
}
