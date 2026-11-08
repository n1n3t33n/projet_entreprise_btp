/*
  Catalogue des écrans du poste de pilotage.

  Ce fichier ne décrit QUE l'existence des écrans : identifiant, libellé, icône
  et chemin. Il ne dit plus qui y a accès.

  Qui accède à quoi est une DONNÉE, pas du code : la modélisation range les
  rôles et les permissions parmi « les référentiels appelés à vivre [qui] ne
  sont pas des énumérations du tout : ce sont des tables, conformément à la
  décision "données en base et non du code" » (README § 6.5), et CL-1 donne à
  `Role` les opérations `accorder(permission)` et `retirer(permission)`. La
  matrice est donc chargée depuis l'API (`features/admin/api`), exposée par
  `app/droits-context`, et modifiable par l'administrateur depuis l'écran
  « Comptes et matrice des droits » (charte § 9.2, écran 12).
*/

import {
  ArrowsClockwise,
  ChartLineUp,
  HouseLine,
  type Icon,
  Package,
  ShieldCheck,
  SquaresFour,
  Stack,
} from '@phosphor-icons/react'

export type IdEcran =
  | 'tableau-de-bord'
  | 'avancement'
  | 'stock'
  | 'referentiels'
  | 'administration'
  | 'synchronisation'
  | 'espace-acquereur'

export type EntreeNavigation = {
  id: IdEcran
  libelle: string
  icone: Icon
  chemin: string
}

/** Écrans du poste de pilotage, dans l'ordre d'affichage du menu. */
export const ECRANS: EntreeNavigation[] = [
  {
    id: 'tableau-de-bord',
    libelle: 'Tableau de bord',
    icone: SquaresFour,
    chemin: '/tableau-de-bord',
  },
  { id: 'avancement', libelle: 'Avancement', icone: ChartLineUp, chemin: '/avancement' },
  { id: 'stock', libelle: 'Stock', icone: Package, chemin: '/stock' },
  { id: 'referentiels', libelle: 'Référentiels', icone: Stack, chemin: '/referentiels' },
  {
    id: 'administration',
    libelle: 'Administration',
    icone: ShieldCheck,
    chemin: '/administration',
  },
  {
    id: 'synchronisation',
    libelle: 'Synchronisation',
    icone: ArrowsClockwise,
    chemin: '/synchronisation',
  },
  {
    id: 'espace-acquereur',
    libelle: 'Espace acquéreur',
    icone: HouseLine,
    chemin: '/espace-acquereur',
  },
]

const IDS = new Set<string>(ECRANS.map((ecran) => ecran.id))

/** Vrai si la chaîne désigne un écran existant. Filtre les données servies. */
export function EST_ID_ECRAN(valeur: string): boolean {
  return IDS.has(valeur)
}

export function ecranParId(id: IdEcran): EntreeNavigation | undefined {
  return ECRANS.find((ecran) => ecran.id === id)
}
