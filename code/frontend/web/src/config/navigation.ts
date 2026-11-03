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
import type { Role } from '@/app/role-context'

export type EntreeNavigation = {
  id: string
  libelle: string
  icone: Icon
  chemin: string
  roles: Role[]
}

export const navigation: EntreeNavigation[] = [
  {
    id: 'tableau-de-bord',
    libelle: 'Tableau de bord',
    icone: SquaresFour,
    chemin: '/tableau-de-bord',
    roles: ['direction', 'administrateur', 'commercial', 'responsable_technique'],
  },
  {
    id: 'avancement',
    libelle: 'Avancement',
    icone: ChartLineUp,
    chemin: '/avancement',
    roles: ['direction', 'commercial', 'responsable_technique'],
  },
  {
    id: 'stock',
    libelle: 'Stock',
    icone: Package,
    chemin: '/stock',
    roles: ['direction', 'administrateur', 'responsable_technique'],
  },
  {
    id: 'referentiels',
    libelle: 'Référentiels',
    icone: Stack,
    chemin: '/referentiels',
    roles: ['administrateur', 'responsable_technique'],
  },
  {
    id: 'administration',
    libelle: 'Administration',
    icone: ShieldCheck,
    chemin: '/administration',
    roles: ['administrateur'],
  },
  {
    id: 'synchronisation',
    libelle: 'Synchronisation',
    icone: ArrowsClockwise,
    chemin: '/synchronisation',
    roles: ['administrateur', 'responsable_technique'],
  },
  {
    id: 'espace-acquereur',
    libelle: 'Espace acquéreur',
    icone: HouseLine,
    chemin: '/espace-acquereur',
    roles: ['acquereur'],
  },
]
