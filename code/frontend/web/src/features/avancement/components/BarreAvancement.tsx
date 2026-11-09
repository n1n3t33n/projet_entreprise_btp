/*
  Barre d'avancement à deux niveaux : déclaré et validé.

  DÉCISION (étape 10) : la mécanique d'affichage a été extraite dans
  `components/ui/JaugeProgression`, composant générique sans notion métier.
  C'était exactement le critère de remontée inscrit ici à l'étape 8 : « si un
  autre module affiche un jour une progression à deux niveaux, on extraira une
  jauge générique ». Le module pilotage (étape 10) est ce second module.

  Ce composant reste dans le module avancement : il ne porte plus que
  l'habillage métier, c'est-à-dire les libellés « déclaré » et « validé »
  issus des états d'étape (ET-1) et de l'avancement agrégé (CL-5). Tout autre
  module qui doit afficher ces deux notions l'importe via l'index du module.

  La part validée (pleine, couleur succès) se superpose à la part déclarée
  (atténuée) sur une même piste, de sorte que l'écart déclaré / validé se lit
  d'un coup d'œil.
*/

import { JaugeProgression } from '@/components/ui'

export type BarreAvancementProps = {
  pourcentageDeclare: number
  pourcentageValide: number
  taille?: 'sm' | 'md'
  afficherLegende?: boolean
  className?: string
}

export function BarreAvancement({
  pourcentageDeclare,
  pourcentageValide,
  taille = 'md',
  afficherLegende = true,
  className,
}: BarreAvancementProps) {
  return (
    <JaugeProgression
      valeur={pourcentageValide}
      valeurSecondaire={pourcentageDeclare}
      libelleValeur="Validé"
      libelleValeurSecondaire="Déclaré"
      descriptionAccessible={`Avancement validé ${Math.round(pourcentageValide)} %, déclaré ${Math.round(pourcentageDeclare)} %`}
      taille={taille}
      afficherLegende={afficherLegende}
      className={className}
    />
  )
}
