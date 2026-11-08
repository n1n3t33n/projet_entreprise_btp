/*
  Capacités du module avancement par rôle, et identité de l'utilisateur courant.

  Même constat que pour le stock : les acteurs de terrain de la modélisation
  (Technicien, Chef d'équipe, Chef de chantier) n'existent pas dans le jeu de
  rôles du poste de pilotage web. Sur le web, le contrôle des étapes et la
  déclaration de blocage sont donc portés par les rôles bureau. Règle imposée :
  l'acquéreur ne voit aucune action d'écriture (il dispose d'une vue simplifiée
  de l'avancement, en lecture seule).

  Table déclarative, modifiable sans toucher aux écrans — préserve la modularité
  et prépare des droits servis par l'API.
*/

import type { Role } from '@/app/role-context'

/**
 * Identité de l'utilisateur courant du poste de pilotage.
 *
 * En production, elle viendrait de la session authentifiée. Ici, une constante
 * de démonstration : elle sert au contrôle « auteur ≠ validateur » (RG-D11),
 * qui interdit de valider une étape qu'on a soi-même déclarée terminée.
 */
export const ID_UTILISATEUR_COURANT = 'U-PILOTE'

export type CapacitesAvancement = {
  /** Consulter le suivi, les étapes, l'historique. */
  peutConsulter: boolean
  /** Valider ou rejeter une étape à contrôle (EF-AVA-06). */
  peutValider: boolean
  /** Déclarer une étape bloquée (EF-AVA-05). */
  peutDeclarerBlocage: boolean
}

const AUCUNE: CapacitesAvancement = {
  peutConsulter: false,
  peutValider: false,
  peutDeclarerBlocage: false,
}

const CAPACITES_AVANCEMENT_PAR_ROLE: Record<Role, CapacitesAvancement> = {
  administrateur: { peutConsulter: true, peutValider: true, peutDeclarerBlocage: true },
  responsable_technique: { peutConsulter: true, peutValider: true, peutDeclarerBlocage: true },
  // Pilotage : consulte et tranche les validations, ne déclare pas les blocages de terrain.
  direction: { peutConsulter: true, peutValider: true, peutDeclarerBlocage: false },
  commercial: AUCUNE,
  // Vue simplifiée en lecture seule.
  acquereur: { peutConsulter: true, peutValider: false, peutDeclarerBlocage: false },
}

export function capacitesAvancementPourRole(role: Role): CapacitesAvancement {
  return CAPACITES_AVANCEMENT_PAR_ROLE[role]
}

export function estLectureSeuleAvancement(capacites: CapacitesAvancement): boolean {
  return !capacites.peutValider && !capacites.peutDeclarerBlocage
}
