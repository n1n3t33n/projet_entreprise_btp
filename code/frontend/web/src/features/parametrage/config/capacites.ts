/*
  Capacités du module parametrage par rôle.

  L'accès à l'écran est décidé par la matrice des droits (donnée modifiable).
  Ce fichier ne règle que les actions.

  Tableau des profils et UC-3 : « Paramétrer un chantier » (EF-REF-07) et
  « Définir les règles de validation » (EF-REF-08) sont accordés à
  l'administrateur fonctionnel ET au responsable technique. Les deux peuvent
  donc consulter et éditer.
*/

import type { Role } from '@/app/role-context'

export type CapacitesParametrage = {
  peutConsulter: boolean
  peutEditer: boolean
}

const CAPACITES_PAR_ROLE: Record<Role, CapacitesParametrage> = {
  administrateur: { peutConsulter: true, peutEditer: true },
  responsable_technique: { peutConsulter: true, peutEditer: true },
  direction: { peutConsulter: false, peutEditer: false },
  commercial: { peutConsulter: false, peutEditer: false },
  acquereur: { peutConsulter: false, peutEditer: false },
}

export function capacitesParametragePourRole(role: Role): CapacitesParametrage {
  return CAPACITES_PAR_ROLE[role]
}
