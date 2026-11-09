/*
  Capacités du module gammes par rôle.

  L'accès à l'écran est décidé par la matrice des droits (donnée modifiable).
  Ce fichier ne règle que les actions à l'intérieur de l'écran.

  Tableau des profils et UC-3 : « Définir les corps d'état » (EF-REF-05) et
  « Publier une version de gamme » (EF-REF-09) relèvent du seul responsable
  technique. L'administrateur fonctionnel n'a pas accès aux données métier ;
  s'il voyait l'écran (droit accordé dans la matrice), il le consulterait sans
  pouvoir l'éditer.
*/

import type { Role } from '@/app/role-context'

export type CapacitesGammes = {
  /** Voir les corps d'état et les gammes. */
  peutConsulter: boolean
  /** Créer et modifier corps d'état, étapes-modèles, versions (EF-REF-05/09). */
  peutEditer: boolean
}

const CAPACITES_PAR_ROLE: Record<Role, CapacitesGammes> = {
  responsable_technique: { peutConsulter: true, peutEditer: true },
  administrateur: { peutConsulter: true, peutEditer: false },
  direction: { peutConsulter: false, peutEditer: false },
  commercial: { peutConsulter: false, peutEditer: false },
  acquereur: { peutConsulter: false, peutEditer: false },
}

export function capacitesGammesPourRole(role: Role): CapacitesGammes {
  return CAPACITES_PAR_ROLE[role]
}
