import { X } from '@phosphor-icons/react'
import { useId, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '@/components/ui/Button'
import { DUREE_SORTIE_MS } from '@/components/ui/motion'
import { useFocusPiege, usePresence, useVerrouScroll } from '@/components/ui/useOverlay'
import { cn } from '@/lib/cn'

export type TailleModal = 'sm' | 'md' | 'lg'

export type ModalProps = {
  /** État d'ouverture, piloté par l'écran appelant. */
  ouvert: boolean
  /** Appelé sur la croix, la touche Échap et le clic sur le voile. */
  onFermer: () => void
  /** Intitulé de la modale. Sert aussi de nom accessible au dialogue. */
  titre: string
  /** Phrase de contexte sous l'intitulé. */
  description?: string
  /** Contenu de la modale. */
  children?: ReactNode
  /** Boutons d'action, alignés à droite en bas de la modale. */
  actions?: ReactNode
  /** Gabarit. `md` par défaut. */
  taille?: TailleModal
  /** `danger` souligne une action irréversible par un filet rouge en en-tête. */
  ton?: 'neutre' | 'danger'
  /** Autorise la fermeture par clic sur le voile. Vrai par défaut. */
  fermetureParVoile?: boolean
}

const PAR_TAILLE: Record<TailleModal, string> = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-3xl',
}

export function Modal({
  ouvert,
  onFermer,
  titre,
  description,
  children,
  actions,
  taille = 'md',
  ton = 'neutre',
  fermetureParVoile = true,
}: ModalProps) {
  const referencePanneau = useRef<HTMLDivElement>(null)
  const identifiant = useId()
  const idTitre = `${identifiant}-titre`
  const idDescription = `${identifiant}-description`

  const { present, phase } = usePresence(ouvert, DUREE_SORTIE_MS)
  useVerrouScroll(present)
  useFocusPiege(referencePanneau, present && ouvert, onFermer)

  if (!present) {
    return null
  }

  // Même raison que pour le tiroir : un portail sort la modale de la mise en
  // page de l'écran appelant, pour qu'elle se centre sur la fenêtre entière.
  return createPortal(
    <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
      <div
        aria-hidden
        onClick={fermetureParVoile ? onFermer : undefined}
        className={cn(
          'absolute inset-0 bg-marine/40',
          phase === 'entree' ? 'animate-voile-entree' : 'animate-voile-sortie',
        )}
      />

      <div
        ref={referencePanneau}
        role="dialog"
        aria-modal="true"
        aria-labelledby={idTitre}
        aria-describedby={description ? idDescription : undefined}
        tabIndex={-1}
        className={cn(
          'relative flex max-h-full w-full flex-col overflow-hidden rounded-carte bg-surface shadow-levee',
          PAR_TAILLE[taille],
          phase === 'entree' ? 'animate-modale-entree' : 'animate-modale-sortie',
        )}
      >
        <header
          className={cn(
            'flex items-start justify-between gap-4 border-b px-5 py-4',
            ton === 'danger' ? 'border-danger/30' : 'border-bordure',
          )}
        >
          <div className="min-w-0 space-y-1">
            <h2
              id={idTitre}
              className={cn('text-lg font-bold', ton === 'danger' ? 'text-danger' : 'text-marine')}
            >
              {titre}
            </h2>
            {description && (
              <p id={idDescription} className="text-sm text-texte-secondaire">
                {description}
              </p>
            )}
          </div>
          <Button variante="discret" taille="sm" icone={X} aria-label="Fermer" onClick={onFermer} />
        </header>

        {children && <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5">{children}</div>}

        {actions && (
          <footer className="flex flex-wrap items-center justify-end gap-2 border-t border-bordure px-5 py-4">
            {actions}
          </footer>
        )}
      </div>
    </div>,
    document.body,
  )
}
