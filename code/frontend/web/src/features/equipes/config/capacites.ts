/*
  Capacités du module équipes par rôle.

  L'ACCÈS à l'écran est décidé par la matrice des droits (donnée modifiable). Ce
  fichier règle la MODIFICATION : créer des affectations (fiches de route) est
  réservé au responsable technique, à qui le tableau des profils confie le fait
  d'« affecter » le travail. Les autres rôles qui pourraient recevoir l'accès à
  l'écran le consultent sans affecter.
*/

import type { Role } from '@/app/role-context'

/** Rôle qui affecte le travail, selon le tableau des profils (RTC). */
const ROLE_AFFECTATION: Role = 'responsable_technique'

export type CapacitesEquipes = {
  /** Créer une affectation (fiche de route) pour un membre. */
  peutAffecter: boolean
}

export function capacitesEquipesPourRole(role: Role): CapacitesEquipes {
  return { peutAffecter: role === ROLE_AFFECTATION }
}
