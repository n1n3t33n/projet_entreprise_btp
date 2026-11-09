/*
  Capacités du module pilotage par rôle.

  L'accès aux écrans « Tableau de bord » et « Journal d'exécution » est décidé
  par la matrice des droits, qui est une donnée modifiable par
  l'administrateur (CL-1 : rôles et permissions sont des tables, pas des
  énumérations). Ce fichier ne règle donc pas l'accès à l'écran : il règle la
  composition de l'écran, section par section, selon le tableau des profils du
  cahier des charges.

  Répartition retenue, et sa justification :
  - Direction et responsable technique voient tout le tableau de bord
    (EF-DSH-01 à 05).
  - Le commercial n'a droit qu'à l'avancement, et sous une forme simplifiée :
    le tableau des profils lui accorde « l'avancement simplifié d'un
    logement », pas le détail par corps d'état, ni le stock, ni le journal.
  - L'administrateur fonctionnel n'a « pas d'accès aux données métier » : il
    administre les comptes et les droits. Aucune section ne lui est ouverte,
    même si la matrice lui ouvrait l'écran.
  - L'acquéreur dispose de son propre espace et n'entre pas ici.

  Si une section est fermée pour un rôle, elle n'est pas affichée en lecture
  grisée : elle n'est pas demandée au serveur du tout. Cela évite de faire
  circuler des données que le rôle n'a pas le droit de voir.
*/

import type { Role } from '@/app/role-context'

export type CapacitesPilotage = {
  /** Voir l'avancement agrégé (EF-DSH-01). */
  peutVoirAvancement: boolean
  /** Voir le détail par corps d'état (EF-DSH-02). */
  peutVoirCorpsEtat: boolean
  /** Voir la synthèse de stock et les mouvements récents (EF-DSH-04). */
  peutVoirStock: boolean
  /** Voir les retards et les blocages (EF-DSH-05). */
  peutVoirAlertes: boolean
  /** Voir le journal d'exécution (EF-DSH-03). */
  peutVoirJournal: boolean
}

const AUCUNE: CapacitesPilotage = {
  peutVoirAvancement: false,
  peutVoirCorpsEtat: false,
  peutVoirStock: false,
  peutVoirAlertes: false,
  peutVoirJournal: false,
}

const TOUT: CapacitesPilotage = {
  peutVoirAvancement: true,
  peutVoirCorpsEtat: true,
  peutVoirStock: true,
  peutVoirAlertes: true,
  peutVoirJournal: true,
}

const CAPACITES_PAR_ROLE: Record<Role, CapacitesPilotage> = {
  direction: TOUT,
  responsable_technique: TOUT,
  commercial: {
    peutVoirAvancement: true,
    peutVoirCorpsEtat: false,
    peutVoirStock: false,
    peutVoirAlertes: false,
    peutVoirJournal: false,
  },
  administrateur: AUCUNE,
  acquereur: AUCUNE,
}

export function capacitesPilotagePourRole(role: Role): CapacitesPilotage {
  return CAPACITES_PAR_ROLE[role]
}
