import { type Icon, Minus, TrendDown, TrendUp } from '@phosphor-icons/react'
import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

/** Sens dans lequel une variation est considérée comme favorable. */
export type TendanceSouhaitee = 'hausse' | 'baisse' | 'neutre'

/** Couleur de l'icône d'en-tête. */
export type AccentKpi = 'marine' | 'sarcelle' | 'or' | 'succes' | 'danger'

export type KpiCardProps = {
  /** Ce que mesure l'indicateur. */
  libelle: string
  /** Valeur mise en avant. Déjà formatée par l'appelant. */
  valeur: ReactNode
  /** Unité affichée en petit à droite de la valeur. */
  unite?: string
  /** Icône Phosphor facultative. */
  icone?: Icon
  /** Couleur de l'icône d'en-tête. */
  accent?: AccentKpi
  /**
   * Variation signée, exprimée en pourcentage (`3.2` pour « +3,2 % »).
   * La couleur dépend de `tendanceSouhaitee`, jamais du seul signe.
   */
  variation?: number
  /** Période de comparaison, par exemple « vs semaine passée ». */
  variationLibelle?: string
  /** Sens favorable de la variation. `hausse` par défaut. */
  tendanceSouhaitee?: TendanceSouhaitee
  /** Affiche des blocs d'attente à la place des valeurs. */
  chargement?: boolean
  className?: string
}

const PAR_ACCENT: Record<AccentKpi, string> = {
  marine: 'bg-fond-alt text-marine',
  sarcelle: 'bg-fond-alt text-sarcelle',
  or: 'bg-or-clair text-or',
  succes: 'bg-succes/10 text-succes',
  danger: 'bg-danger/10 text-danger',
}

const formatVariation = new Intl.NumberFormat('fr-FR', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
  signDisplay: 'always',
})

/** Indique si une variation va dans le sens souhaité. `null` si la question ne se pose pas. */
function estFavorable(variation: number, tendance: TendanceSouhaitee): boolean | null {
  if (tendance === 'neutre' || variation === 0) {
    return null
  }
  return variation > 0 === (tendance === 'hausse')
}

export function KpiCard({
  libelle,
  valeur,
  unite,
  icone,
  accent = 'sarcelle',
  variation,
  variationLibelle,
  tendanceSouhaitee = 'hausse',
  chargement = false,
  className,
}: KpiCardProps) {
  const Icone = icone
  const favorable = variation === undefined ? null : estFavorable(variation, tendanceSouhaitee)
  const IconeTendance =
    variation === undefined || variation === 0 ? Minus : variation > 0 ? TrendUp : TrendDown

  const couleurVariation =
    favorable === null ? 'text-texte-secondaire' : favorable ? 'text-succes' : 'text-danger'

  return (
    <article
      className={cn(
        'flex flex-col gap-3 rounded-carte border border-bordure bg-surface p-5 shadow-douce',
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium text-texte-secondaire">{libelle}</p>
        {Icone && (
          <span className={cn('rounded-controle p-2', PAR_ACCENT[accent])}>
            <Icone size={20} weight="regular" aria-hidden />
          </span>
        )}
      </div>

      {chargement ? (
        <div className="h-9 w-24 animate-pulse rounded-controle bg-fond-alt" />
      ) : (
        <p className="flex items-baseline gap-1.5">
          <span className="text-3xl font-bold leading-none text-marine">{valeur}</span>
          {unite && <span className="text-sm font-medium text-texte-secondaire">{unite}</span>}
        </p>
      )}

      {variation !== undefined && !chargement && (
        <p className={cn('flex items-center gap-1.5 text-sm font-medium', couleurVariation)}>
          <IconeTendance size={16} weight="bold" aria-hidden />
          <span>{formatVariation.format(variation)} %</span>
          {variationLibelle && (
            <span className="font-normal text-texte-secondaire">{variationLibelle}</span>
          )}
        </p>
      )}
    </article>
  )
}
