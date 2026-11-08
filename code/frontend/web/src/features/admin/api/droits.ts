/*
  Appels réseau du domaine « accès et droits », sur le client axios partagé.

  Un seul chargement sert tout le poste de pilotage : la coquille de navigation
  (menu et garde de route) et l'écran d'administration lisent le même état.
*/

import { http } from '@/lib/api/http'
import { EST_ID_ECRAN, type IdEcran } from '@/config/navigation'
import type {
  ActionPermission,
  DroitAccorde,
  EtatDroits,
  PermissionEcran,
  PorteeDroit,
  RoleDroit,
} from '@/features/admin/types/domaine'
import type { DroitAccordeDto, PermissionDto, RoleDto } from '@/features/admin/api/dto'

const ACTION_DEPUIS_DB: Record<string, ActionPermission> = {
  CONSULTER: 'consulter',
  CREER: 'creer',
  MODIFIER: 'modifier',
  VALIDER: 'valider',
}

const PORTEE_DEPUIS_DB: Record<string, PorteeDroit> = {
  GLOBALE: 'globale',
  PERIMETRE: 'perimetre',
}

function mapperRole(dto: RoleDto): RoleDroit {
  return { code: dto.code_role, libelle: dto.libelle, systeme: dto.systeme, actif: dto.actif }
}

/**
 * Convertit une permission servie par l'API.
 *
 * Seules les permissions de module « ecran » dont la ressource désigne un
 * écran connu sont retenues : une permission portant sur un écran retiré de
 * l'application ne doit pas faire échouer tout le chargement.
 */
function mapperPermissionEcran(dto: PermissionDto): PermissionEcran | null {
  if (dto.module !== 'ecran' || !EST_ID_ECRAN(dto.ressource)) {
    return null
  }
  return {
    code: dto.code_permission,
    idEcran: dto.ressource as IdEcran,
    action: ACTION_DEPUIS_DB[dto.action] ?? 'consulter',
    libelle: dto.libelle,
  }
}

function mapperDroit(dto: DroitAccordeDto): DroitAccorde {
  return {
    codeRole: dto.role_code_role,
    codePermission: dto.permission_code_permission,
    portee: PORTEE_DEPUIS_DB[dto.portee] ?? 'globale',
  }
}

/** Charge rôles, permissions d'écran et droits accordés en une fois. */
export async function chargerDroits(): Promise<EtatDroits> {
  const [roles, permissions, accordes] = await Promise.all([
    http.get<RoleDto[]>('/droits/roles'),
    http.get<PermissionDto[]>('/droits/permissions'),
    http.get<DroitAccordeDto[]>('/droits/accordes'),
  ])

  return {
    roles: roles.data.map(mapperRole),
    permissions: permissions.data
      .map(mapperPermissionEcran)
      .filter((permission): permission is PermissionEcran => permission !== null),
    accordes: accordes.data.map(mapperDroit),
  }
}

/**
 * Enregistre la matrice complète des droits accordés.
 *
 * L'envoi porte l'intégralité de la matrice plutôt qu'un différentiel : le
 * serveur a ainsi l'état voulu en un seul appel, et deux administrateurs qui
 * enregistrent à la suite ne peuvent pas composer un résultat incohérent.
 */
export async function enregistrerDroits(accordes: DroitAccorde[]): Promise<void> {
  await http.put('/droits/accordes', {
    droits: accordes.map((droit) => ({
      role_code_role: droit.codeRole,
      permission_code_permission: droit.codePermission,
      portee: droit.portee.toUpperCase(),
    })),
  })
}
