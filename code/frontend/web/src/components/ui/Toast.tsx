import { CheckCircle, type Icon, Info, Warning, WarningOctagon, X } from '@phosphor-icons/react'
import { cn } from '@/lib/cn'
import type { TonToast } from '@/components/ui/toast-context'

export type ToastProps = {
  /** Phrase principale. */
  titre: string
  /** Précision facultative. */
  message?: string
  /** Tonalité. `information` par défaut. */
  ton?: TonToast
  /** Appelé au clic sur la croix. Omettre pour une notification non refermable. */
  onFermer?: () => void
  /** Vrai pendant l'animation de fermeture. */
  sortie?: boolean
  className?: string
}

const ICONE_PAR_TON: Record<TonToast, Icon> = {
  information: Info,
  succes: CheckCircle,
  alerte: Warning,
  danger: WarningOctagon,
}

const COULEUR_PAR_TON: Record<TonToast, string> = {
  information: 'text-sarcelle',
  succes: 'text-succes',
  alerte: 'text-or',
  danger: 'text-danger',
}

const FILET_PAR_TON: Record<TonToast, string> = {
  information: 'border-l-sarcelle',
  succes: 'border-l-succes',
  alerte: 'border-l-or',
  danger: 'border-l-danger',
}

export function Toast({
  titre,
  message,
  ton = 'information',
  onFermer,
  sortie = false,
  className,
}: ToastProps) {
  const Icone = ICONE_PAR_TON[ton]

  return (
    <div
      // Une erreur interrompt la lecture en cours, une confirmation attend la
      // fin de la phrase : les deux rôles ARIA ne sont pas interchangeables.
      role={ton === 'danger' ? 'alert' : 'status'}
      className={cn(
        'flex items-start gap-3 rounded-carte border border-bordure border-l-4 bg-surface p-4 shadow-levee',
        FILET_PAR_TON[ton],
        sortie ? 'animate-toast-sortie' : 'animate-toast-entree',
        className,
      )}
    >
      <Icone
        size={20}
        weight="regular"
        aria-hidden
        className={cn('mt-0.5', COULEUR_PAR_TON[ton])}
      />

      <div className="min-w-0 flex-1 space-y-0.5">
        <p className="text-sm font-semibold text-texte">{titre}</p>
        {message && <p className="text-sm text-texte-secondaire">{message}</p>}
      </div>

      {onFermer && (
        <button
          type="button"
          onClick={onFermer}
          aria-label="Fermer la notification"
          className={cn(
            'shrink-0 rounded-controle p-1 text-texte-attenue',
            'transition-colors duration-[var(--duree-bouton)] ease-out hover:bg-fond hover:text-texte',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle',
          )}
        >
          <X size={16} weight="bold" aria-hidden />
        </button>
      )}
    </div>
  )
}
