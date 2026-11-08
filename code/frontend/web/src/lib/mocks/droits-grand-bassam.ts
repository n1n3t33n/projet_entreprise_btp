/*
  Données de démonstration du domaine « accès et droits ».

  Elles imitent les tables `role`, `permission` et `droit_accorde` de CL-1 :
  une permission de consultation par écran, et une matrice initiale conforme
  au tableau des profils du cahier des charges. Cette matrice est un POINT DE
  DÉPART modifiable, pas une règle figée : l'administrateur la change depuis
  l'écran « Comptes et matrice des droits », et la modification vit en mémoire
  le temps de la session, comme le reste des données simulées.

  Justification de la matrice initiale (cahier des charges, tableau des
  profils) :
  - ADM « Créer les comptes, attribuer les rôles… Pas d'accès aux données
    métier » → administration, référentiels (administrateur fonctionnel au sens
    d'UC-3) et synchronisation.
  - DIR « Voir l'avancement et le stock, sans modifier » → tableau de bord,
    avancement, stock.
  - RTC « Définir les gammes, affecter, valider, suivre les retards » → les
    écrans de pilotage et les référentiels.
  - COM « Connaître l'avancement simplifié d'un logement » → avancement.
  - ACQ « Phase 2 : voir l'avancement de son logement, en lecture seule » →
    espace acquéreur.
*/

import type { DroitAccordeDto, PermissionDto, RoleDto } from '@/features/admin/api/dto'
import { ECRANS } from '@/config/navigation'

const ROLES: RoleDto[] = [
  { code_role: 'direction', libelle: 'Direction', systeme: false, actif: true },
  { code_role: 'administrateur', libelle: 'Administrateur', systeme: true, actif: true },
  { code_role: 'commercial', libelle: 'Commercial', systeme: false, actif: true },
  {
    code_role: 'responsable_technique',
    libelle: 'Responsable technique',
    systeme: false,
    actif: true,
  },
  { code_role: 'acquereur', libelle: 'Acquéreur', systeme: false, actif: true },
]

/** Une permission de consultation par écran : `ecran.<id>.consulter`. */
const PERMISSIONS: PermissionDto[] = ECRANS.map((ecran) => ({
  code_permission: `ecran.${ecran.id}.consulter`,
  module: 'ecran',
  ressource: ecran.id,
  action: 'CONSULTER',
  libelle: `Consulter l'écran « ${ecran.libelle} »`,
}))

const MATRICE_INITIALE: Record<string, string[]> = {
  direction: ['tableau-de-bord', 'avancement', 'stock'],
  administrateur: ['referentiels', 'administration', 'synchronisation'],
  commercial: ['avancement'],
  responsable_technique: [
    'tableau-de-bord',
    'avancement',
    'stock',
    'referentiels',
    'synchronisation',
  ],
  acquereur: ['espace-acquereur'],
}

/** Droits accordés, modifiés sur place par l'écran d'administration. */
let droits: DroitAccordeDto[] = Object.entries(MATRICE_INITIALE).flatMap(([codeRole, ecrans]) =>
  ecrans.map((idEcran) => ({
    role_code_role: codeRole,
    permission_code_permission: `ecran.${idEcran}.consulter`,
    portee: 'GLOBALE',
  })),
)

/**
 * Droit sans lequel la matrice deviendrait définitivement non modifiable.
 * Le serveur le rétablit si une requête tente de le retirer : le garde-fou ne
 * repose pas seulement sur la case désactivée à l'écran.
 */
const DROIT_OBLIGATOIRE: DroitAccordeDto = {
  role_code_role: 'administrateur',
  permission_code_permission: 'ecran.administration.consulter',
  portee: 'GLOBALE',
}

export function listerRoles(): RoleDto[] {
  return ROLES
}

export function listerPermissions(): PermissionDto[] {
  return PERMISSIONS
}

export function listerDroits(): DroitAccordeDto[] {
  return droits
}

/** Remplace la matrice complète, en garantissant le droit obligatoire. */
export function remplacerDroits(corps: Record<string, unknown>): DroitAccordeDto[] {
  const recus = Array.isArray(corps.droits) ? corps.droits : []
  const codesPermissions = new Set(PERMISSIONS.map((p) => p.code_permission))
  const codesRoles = new Set(ROLES.map((r) => r.code_role))

  const retenus: DroitAccordeDto[] = []
  const vus = new Set<string>()

  for (const brut of recus) {
    if (!brut || typeof brut !== 'object') {
      continue
    }
    const entree = brut as Record<string, unknown>
    const codeRole = typeof entree.role_code_role === 'string' ? entree.role_code_role : ''
    const codePermission =
      typeof entree.permission_code_permission === 'string' ? entree.permission_code_permission : ''
    // On ignore les lignes inconnues plutôt que de rejeter tout l'envoi.
    if (!codesRoles.has(codeRole) || !codesPermissions.has(codePermission)) {
      continue
    }
    const identifiant = `${codeRole}::${codePermission}`
    if (vus.has(identifiant)) {
      continue
    }
    vus.add(identifiant)
    retenus.push({
      role_code_role: codeRole,
      permission_code_permission: codePermission,
      portee: typeof entree.portee === 'string' ? entree.portee : 'GLOBALE',
    })
  }

  const cleObligatoire = `${DROIT_OBLIGATOIRE.role_code_role}::${DROIT_OBLIGATOIRE.permission_code_permission}`
  if (!vus.has(cleObligatoire)) {
    retenus.push(DROIT_OBLIGATOIRE)
  }

  droits = retenus
  return droits
}
