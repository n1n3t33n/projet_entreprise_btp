import {
  CheckCircle,
  Circle,
  Clock,
  type Icon,
  Warning,
  WarningOctagon,
} from '@phosphor-icons/react'
import { cn } from '@/lib/cn'

/**
 * Tonalité d'un statut.
 *
 * Volontairement générique : le composant ne connaît aucun statut métier de
 * ChantierSync. C'est l'écran appelant qui traduit « fiche de route terminée »
 * ou « magasin en rupture » en tonalité et en libellé.
 */
export type TonStatut = 'neutre' | 'information' | 'succes' | 'alerte' | 'danger'

export type StatusPillProps = {
  /** Texte affiché. Toujours présent : la couleur ne porte jamais seule le sens. */
  libelle: string
  /** Tonalité. `neutre` par défaut. */
  ton?: TonStatut
  /** Icône Phosphor. Une icône par défaut est associée à chaque tonalité. */
  icone?: Icon
  /** Gabarit. `md` par défaut. */
  taille?: 'sm' | 'md'
  className?: string
}

const PAR_TON: Record<TonStatut, string> = {
  neutre: 'bg-fond-alt text-texte-secondaire',
  information: 'bg-fond-alt text-marine',
  succes: 'bg-succes/10 text-succes',
  alerte: 'bg-or-clair text-or',
  danger: 'bg-danger/10 text-danger',
}

const ICONE_PAR_TON: Record<TonStatut, Icon> = {
  neutre: Circle,
  information: Clock,
  succes: CheckCircle,
  alerte: Warning,
  danger: WarningOctagon,
}

export function StatusPill({
  libelle,
  ton = 'neutre',
  icone,
  taille = 'md',
  className,
}: StatusPillProps) {
  const Icone = icone ?? ICONE_PAR_TON[ton]

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        taille === 'sm' ? 'gap-1 px-2 py-0.5 text-xs' : 'gap-1.5 px-3 py-1 text-sm',
        PAR_TON[ton],
        className,
      )}
    >
      <Icone size={taille === 'sm' ? 14 : 16} weight="regular" aria-hidden />
      {libelle}
    </span>
  )
}
