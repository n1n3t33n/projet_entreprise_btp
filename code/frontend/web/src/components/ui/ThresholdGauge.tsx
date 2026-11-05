import {
  CheckCircle,
  Gauge,
  type Icon,
  Prohibit,
  Warning,
  WarningOctagon,
} from '@phosphor-icons/react'
import {
  calculerNiveauSeuil,
  referenceRemplissage,
  type NiveauSeuil,
  type ParametresSeuil,
} from '@/components/ui/seuils'
import { cn } from '@/lib/cn'

export type ThresholdGaugeProps = ParametresSeuil & {
  /** Unité de la quantité, par exemple « sac » ou « m³ ». */
  unite?: string
  /**
   * Impose le niveau au lieu de le déduire des seuils.
   * À utiliser quand le niveau est déjà calculé côté API.
   */
  niveau?: NiveauSeuil
  /** Affiche la quantité et les seuils sous la jauge. */
  afficherValeurs?: boolean
  /** Gabarit. `md` par défaut. */
  taille?: 'sm' | 'md'
  className?: string
}

const LIBELLE_PAR_NIVEAU: Record<NiveauSeuil, string> = {
  negatif: 'Stock négatif signalé',
  vide: 'Vide',
  critique: 'Critique',
  mini: 'Mini',
  plein: 'Plein',
}

const ICONE_PAR_NIVEAU: Record<NiveauSeuil, Icon> = {
  negatif: Prohibit,
  vide: WarningOctagon,
  critique: Warning,
  mini: Gauge,
  plein: CheckCircle,
}

const TEXTE_PAR_NIVEAU: Record<NiveauSeuil, string> = {
  negatif: 'text-danger',
  vide: 'text-danger',
  critique: 'text-or',
  mini: 'text-sarcelle',
  plein: 'text-succes',
}

const REMPLISSAGE_PAR_NIVEAU: Record<NiveauSeuil, string> = {
  negatif: 'bg-danger',
  vide: 'bg-danger',
  critique: 'bg-or',
  mini: 'bg-sarcelle',
  plein: 'bg-succes',
}

export function ThresholdGauge({
  valeur,
  seuilMini,
  seuilConfort,
  capacite,
  unite,
  niveau,
  afficherValeurs = true,
  taille = 'md',
  className,
}: ThresholdGaugeProps) {
  const parametres: ParametresSeuil = { valeur, seuilMini, seuilConfort, capacite }
  const niveauEffectif = niveau ?? calculerNiveauSeuil(parametres)

  const reference = referenceRemplissage(parametres)
  const proportion =
    niveauEffectif === 'negatif' || reference <= 0
      ? 0
      : Math.min(1, Math.max(0, valeur / reference))

  const Icone = ICONE_PAR_NIVEAU[niveauEffectif]
  const libelle = LIBELLE_PAR_NIVEAU[niveauEffectif]

  return (
    <div className={cn('flex min-w-0 flex-col gap-1.5', className)}>
      <div
        className={cn(
          'flex items-center gap-1.5 font-semibold',
          taille === 'sm' ? 'text-xs' : 'text-sm',
          TEXTE_PAR_NIVEAU[niveauEffectif],
        )}
      >
        <Icone size={taille === 'sm' ? 14 : 16} weight="regular" aria-hidden />
        <span>{libelle}</span>
      </div>

      <div
        role="meter"
        aria-label={`Niveau de stock : ${libelle}`}
        aria-valuemin={0}
        aria-valuemax={reference}
        aria-valuenow={Math.max(0, valeur)}
        aria-valuetext={`${valeur}${unite ? ` ${unite}` : ''} — ${libelle}`}
        className={cn(
          'w-full overflow-hidden rounded-full bg-bordure',
          taille === 'sm' ? 'h-1.5' : 'h-2',
        )}
      >
        {/*
          Le remplissage est obtenu par « scaleX » et non par une largeur :
          seules les propriétés « transform » et « opacity » sont animées,
          pour éviter que le navigateur recalcule la mise en page à chaque image.
        */}
        <div
          className={cn(
            'h-full origin-left transition-transform duration-[var(--duree-survol)] ease-out',
            REMPLISSAGE_PAR_NIVEAU[niveauEffectif],
          )}
          style={{ transform: `scaleX(${proportion})` }}
        />
      </div>

      {afficherValeurs && (
        <p className="text-xs text-texte-secondaire">
          {valeur}
          {unite ? ` ${unite}` : ''} · seuil mini {seuilMini}
          {capacite !== undefined ? ` · capacité ${capacite}` : ''}
        </p>
      )}
    </div>
  )
}
