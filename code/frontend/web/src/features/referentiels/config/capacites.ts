/*
  Capacités du module référentiels par rôle — filtrage des actions d'écriture.

  L'accès à l'écran est décidé par la matrice unique de `config/navigation`
  (administrateur et responsable technique). Ce fichier ne règle que les
  actions, référentiel par référentiel, selon la répartition de l'UC-3 et du
  tableau des profils du cahier des charges :
  - Structure des chantiers, zones, logements (EF-REF-01) : Responsable
    technique.
  - Magasins (EF-REF-02) et unités (EF-REF-04) : Administrateur fonctionnel.
  - Catalogue d'articles (EF-REF-03) : Gestionnaire de stock — rôle absent du
    poste de pilotage, dont le responsable technique tient lieu sur le web
    (même transposition que pour le module stock).
  Chaque rôle autorisé consulte l'ensemble des référentiels.
*/

import type { Role } from '@/app/role-context'

export type CapacitesReferentiels = {
  /** Voir les référentiels (catalogue, magasins, structure). */
  peutConsulter: boolean
  /** Créer et modifier les articles du catalogue (EF-REF-03). */
  peutEditerCatalogue: boolean
  /** Créer et modifier les magasins (EF-REF-02). */
  peutEditerMagasins: boolean
  /** Modifier le chantier, créer et modifier zones et logements (EF-REF-01). */
  peutEditerStructure: boolean
}

const AUCUNE: CapacitesReferentiels = {
  peutConsulter: false,
  peutEditerCatalogue: false,
  peutEditerMagasins: false,
  peutEditerStructure: false,
}

const CAPACITES_PAR_ROLE: Record<Role, CapacitesReferentiels> = {
  administrateur: {
    peutConsulter: true,
    peutEditerCatalogue: false,
    peutEditerMagasins: true,
    peutEditerStructure: false,
  },
  responsable_technique: {
    peutConsulter: true,
    peutEditerCatalogue: true,
    peutEditerMagasins: false,
    peutEditerStructure: true,
  },
  direction: AUCUNE,
  commercial: AUCUNE,
  acquereur: AUCUNE,
}

export function capacitesReferentielsPourRole(role: Role): CapacitesReferentiels {
  return CAPACITES_PAR_ROLE[role]
}
