import { CheckCircle, Gauge, type Icon, Warning, WarningOctagon } from '@phosphor-icons/react'
import { cn } from '@/lib/cn'
import {
  calculerNiveauSeuil,
  estStockNegatif,
  referenceRemplissage,
  type NiveauSeuil,
  type ParametresSeuil,
} from '@/lib/seuils'

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
  vide: 'Vide',
  critique: 'Critique',
  mini: 'Mini',
  plein: 'Plein',
}

/*
  Anomalie de stock négatif (cahier des charges : « un stock négatif est
  autorisé et signalé comme anomalie à corriger » ; charte : « représentation
  explicite du stock négatif »). Elle ne remplace pas le niveau — qui reste
  « vide » comme en base — mais prend sa place à l'affichage, pour qu'une
  quantité négative ne se confonde jamais avec un stock épuisé à zéro.
*/
const LIBELLE_ANOMALIE = 'Stock négatif'

const ICONE_PAR_NIVEAU: Record<NiveauSeuil, Icon> = {
  vide: WarningOctagon,
  critique: Warning,
  mini: Gauge,
  plein: CheckCircle,
}

const TEXTE_PAR_NIVEAU: Record<NiveauSeuil, string> = {
  vide: 'text-danger',
  critique: 'text-or',
  mini: 'text-sarcelle',
  plein: 'text-succes',
}

const REMPLISSAGE_PAR_NIVEAU: Record<NiveauSeuil, string> = {
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
  const anomalie = estStockNegatif(valeur)
  // La barre ne peut pas représenter une quantité négative : elle reste vide.
  // La valeur réelle, elle, continue d'être affichée telle quelle — c'est
  // l'anomalie à corriger, la masquer reviendrait à la dissimuler.
  const remplissage = Math.max(0, valeur)
  const proportion = reference <= 0 ? 0 : Math.min(1, remplissage / reference)

  const Icone = anomalie ? WarningOctagon : ICONE_PAR_NIVEAU[niveauEffectif]
  const libelle = anomalie ? LIBELLE_ANOMALIE : LIBELLE_PAR_NIVEAU[niveauEffectif]
  const classeTexte = anomalie ? 'text-danger' : TEXTE_PAR_NIVEAU[niveauEffectif]

  return (
    <div className={cn('flex min-w-0 flex-col gap-1.5', className)}>
      <div
        className={cn(
          'flex items-center gap-1.5 font-semibold',
          taille === 'sm' ? 'text-xs' : 'text-sm',
          classeTexte,
        )}
      >
        <Icone
          size={taille === 'sm' ? 14 : 16}
          weight={anomalie ? 'fill' : 'regular'}
          aria-hidden
        />
        <span>{libelle}</span>
      </div>

      <div
        role="meter"
        aria-label={`Niveau de stock : ${libelle}`}
        aria-valuemin={0}
        aria-valuemax={reference}
        aria-valuenow={remplissage}
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
        <p
          className={cn('text-xs', anomalie ? 'font-medium text-danger' : 'text-texte-secondaire')}
        >
          {valeur}
          {unite ? ` ${unite}` : ''} · alerte à {seuilMini} · confort à {seuilConfort}
          {capacite !== undefined ? ` · capacité ${capacite}` : ''}
        </p>
      )}
    </div>
  )
}
