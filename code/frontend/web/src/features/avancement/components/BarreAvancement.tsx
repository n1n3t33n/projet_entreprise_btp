/*
  Barre d'avancement à deux niveaux : déclaré et validé.

  DÉCISION (étape 8) : le composant reste local au module avancement.
  - Ses trois consommateurs sont tous dans ce module ; aucun autre module n'en
    a besoin aujourd'hui.
  - Son contrat porte des notions métier propres au suivi des étapes (part
    « déclarée » et part « validée », issues des états d'étape ET-1 et de
    l'avancement agrégé CL-5). La bibliothèque `components/ui` n'accueille que
    des composants sans notion métier.
  Critère de remontée : si un autre module affiche un jour une progression à
  deux niveaux, on extraira une jauge générique (`valeur`, `valeurSecondaire`)
  dans `components/ui`, que ce composant habillera avec ses libellés métier.

  La part validée (pleine, couleur succès) se superpose à la part déclarée
  (atténuée) sur une même piste, de sorte que l'écart déclaré / validé se lit
  d'un coup d'œil.
*/

import { cn } from '@/lib/cn'
import { formatPourcentage } from '@/lib/format'

export type BarreAvancementProps = {
  pourcentageDeclare: number
  pourcentageValide: number
  taille?: 'sm' | 'md'
  afficherLegende?: boolean
  className?: string
}

function borne(valeur: number): number {
  if (valeur < 0) return 0
  if (valeur > 100) return 100
  return valeur
}

export function BarreAvancement({
  pourcentageDeclare,
  pourcentageValide,
  taille = 'md',
  afficherLegende = true,
  className,
}: BarreAvancementProps) {
  const declare = borne(pourcentageDeclare)
  const valide = borne(pourcentageValide)

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
        aria-valuenow={Math.round(valide)}
        aria-label={`Avancement validé ${Math.round(valide)} %, déclaré ${Math.round(declare)} %`}
      >
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-sarcelle/35"
          style={{ width: `${declare}%` }}
        />
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-succes"
          style={{ width: `${valide}%` }}
        />
      </div>

      {afficherLegende && (
        <div className="flex items-center gap-3 text-xs text-texte-secondaire">
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-succes" aria-hidden />
            Validé {formatPourcentage(valide)}
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-sarcelle/35" aria-hidden />
            Déclaré {formatPourcentage(declare)}
          </span>
        </div>
      )}
    </div>
  )
}
