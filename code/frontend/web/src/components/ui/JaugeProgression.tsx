/*
  Jauge de progression générique, sans notion métier.

  Deux valeurs se superposent sur une même piste : `valeur` (part pleine, au
  premier plan) et `valeurSecondaire` (part atténuée, en arrière-plan). Le
  composant n'impose aucun vocabulaire : les libellés de légende sont fournis
  par l'appelant, qui seul connaît la signification des deux niveaux.

  Historique : extraite du composant `BarreAvancement` du module avancement à
  l'étape 10, lorsqu'un second module (pilotage) a eu besoin d'afficher une
  progression à deux niveaux. C'était le critère de remontée inscrit dans ce
  composant à l'étape 8.
*/

import { cn } from '@/lib/cn'
import { formatPourcentage } from '@/lib/format'

export type JaugeProgressionProps = {
  /** Part principale, affichée pleine au premier plan (0 à 100). */
  valeur: number
  /** Part de référence, affichée atténuée en arrière-plan (0 à 100). */
  valeurSecondaire: number
  /** Libellé de légende de la part principale. */
  libelleValeur?: string
  /** Libellé de légende de la part de référence. */
  libelleValeurSecondaire?: string
  /** Texte lu par les lecteurs d'écran ; remplace la description par défaut. */
  descriptionAccessible?: string
  taille?: 'sm' | 'md'
  afficherLegende?: boolean
  className?: string
}

function borne(valeur: number): number {
  if (valeur < 0) return 0
  if (valeur > 100) return 100
  return valeur
}

export function JaugeProgression({
  valeur,
  valeurSecondaire,
  libelleValeur = 'Valeur',
  libelleValeurSecondaire = 'Référence',
  descriptionAccessible,
  taille = 'md',
  afficherLegende = true,
  className,
}: JaugeProgressionProps) {
  const principale = borne(valeur)
  const secondaire = borne(valeurSecondaire)

  const description =
    descriptionAccessible ??
    `${libelleValeur} ${Math.round(principale)} %, ${libelleValeurSecondaire} ${Math.round(secondaire)} %`

  return (
    <div className={cn('flex flex-col gap-1', className)}>
      <div
        className={cn(
          'relative w-full overflow-hidden rounded-full bg-fond-alt',
          taille === 'sm' ? 'h-2' : 'h-2.5',
        )}
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(principale)}
        aria-label={description}
      >
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-sarcelle/35"
          style={{ width: `${secondaire}%` }}
        />
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-succes"
          style={{ width: `${principale}%` }}
        />
      </div>

      {afficherLegende && (
        <div className="flex items-center gap-3 text-xs text-texte-secondaire">
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-succes" aria-hidden />
            {libelleValeur} {formatPourcentage(principale)}
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-sarcelle/35" aria-hidden />
            {libelleValeurSecondaire} {formatPourcentage(secondaire)}
          </span>
        </div>
      )}
    </div>
  )
}
