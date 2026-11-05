import { type Icon, X } from '@phosphor-icons/react'
import { cn } from '@/lib/cn'

export type FilterPillProps = {
  /** Critère filtré, par exemple « Corps d'état ». */
  libelle: string
  /** Valeur retenue pour ce critère, par exemple « Gros œuvre ». */
  valeur?: string
  /** Vrai quand le filtre est appliqué. */
  actif?: boolean
  /** Icône Phosphor facultative. */
  icone?: Icon
  /** Rend la pilule inopérante. */
  desactive?: boolean
  /** Appelé au clic sur la pilule. Omettre pour une pilule simplement lisible. */
  onBasculer?: () => void
  /** Ajoute une croix de retrait. Omettre pour une pilule non retirable. */
  onRetirer?: () => void
  className?: string
}

export function FilterPill({
  libelle,
  valeur,
  actif = false,
  icone,
  desactive = false,
  onBasculer,
  onRetirer,
  className,
}: FilterPillProps) {
  const Icone = icone

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border text-sm font-medium',
        'transition-colors duration-[var(--duree-survol)] ease-out',
        actif
          ? 'border-marine bg-marine text-white'
          : 'border-bordure bg-surface text-texte hover:bg-fond',
        desactive && 'pointer-events-none opacity-50',
        className,
      )}
    >
      <button
        type="button"
        onClick={onBasculer}
        disabled={desactive || !onBasculer}
        aria-pressed={onBasculer ? actif : undefined}
        className={cn(
          'flex items-center gap-1.5 rounded-full py-1.5',
          onRetirer ? 'pl-3 pr-1.5' : 'px-3',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle',
          'focus-visible:ring-offset-2 focus-visible:ring-offset-surface',
          onBasculer ? 'cursor-pointer' : 'cursor-default',
        )}
      >
        {Icone && <Icone size={14} weight="regular" aria-hidden />}
        <span>{libelle}</span>
        {valeur && (
          <span className={cn('font-normal', actif ? 'text-white/80' : 'text-texte-secondaire')}>
            · {valeur}
          </span>
        )}
      </button>

      {onRetirer && (
        <button
          type="button"
          onClick={onRetirer}
          disabled={desactive}
          aria-label={`Retirer le filtre ${libelle}`}
          className={cn(
            'mr-1 rounded-full p-1 transition-colors duration-[var(--duree-bouton)] ease-out',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle',
            'focus-visible:ring-offset-2 focus-visible:ring-offset-surface',
            actif ? 'hover:bg-white/20' : 'hover:bg-fond-alt',
          )}
        >
          <X size={12} weight="bold" aria-hidden />
        </button>
      )}
    </span>
  )
}
