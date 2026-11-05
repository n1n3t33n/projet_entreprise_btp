import { X } from '@phosphor-icons/react'
import { useId, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '@/components/ui/Button'
import { DUREE_SORTIE_MS } from '@/components/ui/motion'
import { useFocusPiege, usePresence, useVerrouScroll } from '@/components/ui/useOverlay'
import { cn } from '@/lib/cn'

export type LargeurDrawer = 'sm' | 'md' | 'lg'

export type DrawerProps = {
  /** État d'ouverture, piloté par l'écran appelant. */
  ouvert: boolean
  /** Appelé sur la croix, la touche Échap et le clic sur le voile. */
  onFermer: () => void
  /** Intitulé du tiroir. Sert aussi de nom accessible au dialogue. */
  titre: string
  /** Phrase de contexte sous l'intitulé. */
  description?: string
  /** Contenu défilant du tiroir. */
  children?: ReactNode
  /** Bande d'actions en bas du tiroir, qui ne défile pas. */
  pied?: ReactNode
  /** Largeur du panneau. `md` par défaut. */
  largeur?: LargeurDrawer
  /** Autorise la fermeture par clic sur le voile. Vrai par défaut. */
  fermetureParVoile?: boolean
}

const PAR_LARGEUR: Record<LargeurDrawer, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-2xl',
}

export function Drawer({
  ouvert,
  onFermer,
  titre,
  description,
  children,
  pied,
  largeur = 'md',
  fermetureParVoile = true,
}: DrawerProps) {
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

  /*
    Rendu par un portail, directement sous « body » : resté enfant de la carte
    ou du tableau qui l'a ouvert, le panneau hériterait de ses marges, de son
    découpage (« overflow: hidden ») et de son contexte d'empilement, donc
    serait tronqué ou passerait sous la barre de navigation.
  */
  return createPortal(
    <div className="fixed inset-0 z-40 flex justify-end">
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
          'relative flex h-full w-full flex-col bg-surface shadow-levee',
          PAR_LARGEUR[largeur],
          phase === 'entree' ? 'animate-tiroir-entree' : 'animate-tiroir-sortie',
        )}
      >
        <header className="flex items-start justify-between gap-4 border-b border-bordure px-5 py-4">
          <div className="min-w-0 space-y-1">
            <h2 id={idTitre} className="text-lg font-bold text-marine">
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

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5">{children}</div>

        {pied && (
          <footer className="flex flex-wrap items-center justify-end gap-2 border-t border-bordure px-5 py-4">
            {pied}
          </footer>
        )}
      </div>
    </div>,
    document.body,
  )
}
