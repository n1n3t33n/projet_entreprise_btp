/*
  Capacités du module référentiels par rôle — filtrage des actions d'écriture.

  La modélisation (UC-3) répartit la tenue des référentiels entre plusieurs
  acteurs : Responsable technique pour les chantiers, zones et logements
  (EF-REF-01) ; Administrateur fonctionnel pour les magasins et les unités
  (EF-REF-02, EF-REF-04) ; Gestionnaire de stock pour le catalogue d'articles
  (EF-REF-03, via UC-1). Ces acteurs n'existent pas tels quels dans le jeu de
  rôles du poste de pilotage (`Role`) : sur le web, l'écriture est portée par
  les rôles bureau qui en tiennent lieu — `administrateur` et
  `responsable_technique`. Règle imposée : l'acquéreur ne voit aucune action
  d'écriture ; le commercial n'a pas accès à ce module.

  Table déclarative : une action n'apparaît que si la capacité correspondante
  est vraie. Le filtrage se modifie ici, sans toucher aux écrans, ce qui prépare
  le passage à des droits servis par l'API.
*/

import type { Role } from '@/app/role-context'

export type CapacitesReferentiels = {
  /** Voir les référentiels (catalogue, magasins, structure). */
  peutConsulter: boolean
  /**
   * Créer et modifier les entrées des référentiels. Capacité unique sur le
   * web : la répartition fine par acteur du modèle est documentée ci-dessus et
   * pourra être rétablie quand l'API servira des droits par référentiel.
   */
  peutEditer: boolean
}

const CAPACITES_PAR_ROLE: Record<Role, CapacitesReferentiels> = {
  // Administrateur fonctionnel + gestionnaire de stock : tient l'ensemble des
  // référentiels sur le poste de pilotage.
  administrateur: { peutConsulter: true, peutEditer: true },
  // Responsable technique : tient la structure (chantiers, zones, logements) et
  // participe au catalogue.
  responsable_technique: { peutConsulter: true, peutEditer: true },
  // Pilotage : consulte les référentiels, ne les édite pas.
  direction: { peutConsulter: true, peutEditer: false },
  // Pas d'accès au module.
  commercial: { peutConsulter: false, peutEditer: false },
  // Consulte sans jamais écrire (lecture seule imposée).
  acquereur: { peutConsulter: true, peutEditer: false },
}

export function capacitesReferentielsPourRole(role: Role): CapacitesReferentiels {
  return CAPACITES_PAR_ROLE[role]
}
