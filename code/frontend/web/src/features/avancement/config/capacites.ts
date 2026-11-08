/*
  Capacités du module avancement par rôle, et identité de l'utilisateur courant.

  Même constat que pour le stock : les acteurs de terrain de la modélisation
  (Technicien, Chef d'équipe, Chef de chantier) n'existent pas dans le jeu de
  rôles du poste de pilotage web. Sur le web, le contrôle des étapes et la
  déclaration de blocage sont donc portés par les rôles bureau. L'acquéreur
  n'accède pas à ce module : il suit son logement dans l'espace acquéreur.

  Table déclarative, modifiable sans toucher aux écrans — préserve la modularité
  et prépare des droits servis par l'API. L'accès à l'écran est décidé par la
  matrice de `config/navigation` ; les valeurs ci-dessous suivent le tableau des
  profils du cahier des charges.
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
  // Cahier des charges : gammes, affectation, validation, suivi des retards.
  responsable_technique: { peutConsulter: true, peutValider: true, peutDeclarerBlocage: true },
  // « Voir l'avancement et le stock, sans modifier » : corrigé, la direction ne
  // valide plus d'étape (lecture seule stricte).
  direction: { peutConsulter: true, peutValider: false, peutDeclarerBlocage: false },
  // « Connaître l'avancement simplifié d'un logement » : corrigé, le commercial
  // consulte (il n'avait aucun accès alors que le menu lui proposait l'écran).
  commercial: { peutConsulter: true, peutValider: false, peutDeclarerBlocage: false },
  // « Pas d'accès aux données métier » : corrigé, plus aucun accès.
  administrateur: AUCUNE,
  // Phase 2 : l'acquéreur suit son seul logement dans l'espace acquéreur.
  acquereur: AUCUNE,
}

export function capacitesAvancementPourRole(role: Role): CapacitesAvancement {
  return CAPACITES_AVANCEMENT_PAR_ROLE[role]
}

export function estLectureSeuleAvancement(capacites: CapacitesAvancement): boolean {
  return !capacites.peutValider && !capacites.peutDeclarerBlocage
}
