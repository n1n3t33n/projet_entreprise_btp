/*
  Capacités du module stock par rôle — filtrage des actions d'écriture.

  L'accès à l'écran lui-même est décidé par la matrice unique de
  `config/navigation` ; ce fichier ne règle que les actions. Les valeurs
  suivent le tableau des profils du cahier des charges.

  La modélisation décrit des acteurs de terrain (Magasinier, Gestionnaire de
  stock, Chef de chantier) qui n'existent pas dans le jeu de rôles du poste de
  pilotage web (`Role`). Sur le web, l'écriture est donc portée par les rôles
  bureau qui en tiennent lieu. Règle imposée : l'acquéreur ne voit aucune action
  d'écriture.

  Table déclarative : une action n'apparaît que si la capacité correspondante
  est vraie. Modifier le filtrage se fait ici, sans toucher aux écrans — ce qui
  préserve la modularité et prépare le passage à des droits servis par l'API.

  Le contrôle « auteur ≠ validateur » (RG-D11) s'ajoute à ces capacités au cas
  par cas, dans les formulaires : il ne dépend pas du rôle mais de l'événement.
*/

import type { Role } from '@/app/role-context'

export type CapacitesStock = {
  /** Voir le stock, les fiches, l'historique. */
  peutConsulter: boolean
  /** Saisir une entrée, une sortie, un contre-mouvement. */
  peutSaisir: boolean
  /** Valider ou refuser un mouvement soumis à validation. */
  peutValider: boolean
  /** Définir les seuils minimal et critique (EF-STK-06). */
  peutDefinirSeuils: boolean
  /** Ouvrir et traiter un inventaire. */
  peutInventaire: boolean
}

const AUCUNE: CapacitesStock = {
  peutConsulter: false,
  peutSaisir: false,
  peutValider: false,
  peutDefinirSeuils: false,
  peutInventaire: false,
}

const CAPACITES_STOCK_PAR_ROLE: Record<Role, CapacitesStock> = {
  // Saisie + validation + seuils + inventaire : tient lieu de gestionnaire de
  // stock sur le poste de pilotage (le gestionnaire n'est pas un rôle bureau).
  responsable_technique: {
    peutConsulter: true,
    peutSaisir: true,
    peutValider: true,
    peutDefinirSeuils: true,
    peutInventaire: true,
  },
  // Cahier des charges : « voir l'avancement et le stock, sans modifier ».
  // Corrigé : la direction ne valide plus de mouvement (lecture seule stricte).
  direction: {
    peutConsulter: true,
    peutSaisir: false,
    peutValider: false,
    peutDefinirSeuils: false,
    peutInventaire: false,
  },
  // Cahier des charges : « pas d'accès aux données métier ». Corrigé : aucun
  // accès au stock (il en avait un complet jusqu'ici).
  administrateur: AUCUNE,
  commercial: AUCUNE,
  // Phase 2 : l'acquéreur ne voit que son logement (espace acquéreur).
  acquereur: AUCUNE,
}

export function capacitesStockPourRole(role: Role): CapacitesStock {
  return CAPACITES_STOCK_PAR_ROLE[role]
}

/** Vrai si le rôle n'a aucune action d'écriture : l'écran passe en lecture seule. */
export function estLectureSeule(capacites: CapacitesStock): boolean {
  return (
    !capacites.peutSaisir &&
    !capacites.peutValider &&
    !capacites.peutDefinirSeuils &&
    !capacites.peutInventaire
  )
}
