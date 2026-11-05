import type { Icon } from '@phosphor-icons/react'
import type { KeyboardEvent, ReactNode } from 'react'
import { cn } from '@/lib/cn'

export type Onglet = {
  /** Identifiant unique de l'onglet. */
  id: string
  /** Libellé affiché. */
  libelle: string
  /** Icône Phosphor facultative. */
  icone?: Icon
  /** Compteur affiché à droite du libellé, par exemple un nombre d'alertes. */
  badge?: number
  /** Rend l'onglet inatteignable sans le retirer de la liste. */
  desactive?: boolean
}

export type TabsProps = {
  /** Nom de la série d'onglets, lu par les lecteurs d'écran. */
  intitule: string
  /** Onglets, dans l'ordre d'affichage. */
  onglets: Onglet[]
  /** Identifiant de l'onglet actif. Le composant est piloté par l'appelant. */
  actif: string
  /** Appelé avec l'identifiant de l'onglet demandé. */
  onChanger: (id: string) => void
  /** Contenu de l'onglet actif. */
  children?: ReactNode
  className?: string
}

export function Tabs({ intitule, onglets, actif, onChanger, children, className }: TabsProps) {
  const selectionnables = onglets.filter((onglet) => onglet.desactive !== true)

  /*
    Une série d'onglets ne comporte qu'un seul arrêt de tabulation : l'onglet
    actif porte `tabIndex=0`, les autres `tabIndex=-1`. La touche Tab fait donc
    entrer puis sortir de la série, et ce sont les flèches qui déplacent la
    sélection à l'intérieur.
  */
  function auClavier(evenement: KeyboardEvent<HTMLDivElement>) {
    const touchesGerees = ['ArrowRight', 'ArrowLeft', 'Home', 'End']
    if (!touchesGerees.includes(evenement.key) || selectionnables.length === 0) {
      return
    }

    evenement.preventDefault()
    const position = selectionnables.findIndex((onglet) => onglet.id === actif)

    if (evenement.key === 'Home') {
      const premier = selectionnables[0]
      if (premier) {
        onChanger(premier.id)
      }
      return
    }

    if (evenement.key === 'End') {
      const dernier = selectionnables[selectionnables.length - 1]
      if (dernier) {
        onChanger(dernier.id)
      }
      return
    }

    const pas = evenement.key === 'ArrowRight' ? 1 : -1
    const suivante = (position + pas + selectionnables.length) % selectionnables.length
    const cible = selectionnables[suivante]
    if (cible) {
      onChanger(cible.id)
    }
  }

  return (
    <div className={cn('flex min-w-0 flex-col', className)}>
      <div
        role="tablist"
        aria-label={intitule}
        onKeyDown={auClavier}
        className="flex min-w-0 gap-1 overflow-x-auto border-b border-bordure"
      >
        {onglets.map((onglet) => {
          const estActif = onglet.id === actif
          const Icone = onglet.icone

          return (
            <button
              key={onglet.id}
              type="button"
              role="tab"
              id={`onglet-${onglet.id}`}
              aria-selected={estActif}
              aria-controls={`panneau-${onglet.id}`}
              tabIndex={estActif ? 0 : -1}
              disabled={onglet.desactive}
              onClick={() => onChanger(onglet.id)}
              className={cn(
                'relative flex shrink-0 items-center gap-2 rounded-t-controle px-4 py-2.5 text-sm font-semibold',
                'transition-colors duration-[var(--duree-bouton)] ease-out',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle',
                'disabled:pointer-events-none disabled:opacity-40',
                estActif ? 'text-marine' : 'text-texte-secondaire hover:bg-fond hover:text-texte',
              )}
            >
              {Icone && <Icone size={18} weight="regular" aria-hidden />}
              <span>{onglet.libelle}</span>
              {onglet.badge !== undefined && (
                <span
                  className={cn(
                    'rounded-full px-1.5 py-0.5 text-xs font-bold',
                    estActif ? 'bg-marine text-white' : 'bg-fond-alt text-texte-secondaire',
                  )}
                >
                  {onglet.badge}
                </span>
              )}

              {/* Le soulignement actif est révélé par un changement d'échelle,
                  donc sans mesure de position ni recalcul de mise en page. */}
              <span
                aria-hidden
                className={cn(
                  'absolute inset-x-2 bottom-0 h-0.5 origin-center rounded-full bg-marine',
                  'transition-transform duration-[var(--duree-survol)] ease-out',
                  estActif ? 'scale-x-100' : 'scale-x-0',
                )}
              />
            </button>
          )
        })}
      </div>

      {children && (
        /* La clé change avec l'onglet : React remonte le panneau, ce qui rejoue
           l'animation d'entrée au lieu de simplement remplacer le contenu. */
        <div
          key={actif}
          role="tabpanel"
          id={`panneau-${actif}`}
          aria-labelledby={`onglet-${actif}`}
          tabIndex={0}
          className="animate-cascade min-w-0 pt-5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        >
          {children}
        </div>
      )}
    </div>
  )
}
