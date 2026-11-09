/*
  Capacités du module administration.

  L'ACCÈS à l'écran est décidé par la matrice des droits, comme pour tout autre
  écran. La MODIFICATION de cette matrice est, elle, réservée au rôle système
  (CL-1 `Role.systeme : boolean`). Sans cette réserve, un rôle à qui l'on
  ouvrirait l'écran d'administration pourrait s'accorder lui-même n'importe
  quel droit : la matrice ne protégerait plus rien.

  Conséquence volontaire : un autre rôle peut recevoir l'accès à l'écran pour
  CONSULTER la matrice, sans pouvoir la modifier.
*/

import type { Role } from '@/app/role-context'

/** Rôle système du poste de pilotage, seul habilité à modifier les droits. */
const ROLE_SYSTEME: Role = 'administrateur'

export type CapacitesAdmin = {
  /** Modifier la matrice des droits et l'enregistrer. */
  peutModifierDroits: boolean
  /**
   * Révoquer un appareil (EF-AUT-06). Réservé au rôle système, pour la même
   * raison que la modification des droits : couper l'accès d'un terminal ne
   * doit pas dépendre du seul fait qu'un rôle a reçu l'accès en lecture à
   * l'écran d'administration.
   */
  peutRevoquerAppareil: boolean
  /** Importer des référentiels en CSV (EF-ADM-02). Réservé au rôle système : un import écrit en masse. */
  peutImporter: boolean
}

export function capacitesAdminPourRole(role: Role): CapacitesAdmin {
  const estSysteme = role === ROLE_SYSTEME
  return {
    peutModifierDroits: estSysteme,
    peutRevoquerAppareil: estSysteme,
    peutImporter: estSysteme,
  }
}

/**
 * Écran dont l'accès ne peut jamais être retiré au rôle système.
 *
 * Garde-fou contre l'auto-exclusion : décocher cette case priverait
 * définitivement l'application de tout moyen de modifier les droits.
 */
export const ECRAN_VERROUILLE = 'administration'
export const ROLE_VERROUILLE: Role = ROLE_SYSTEME
