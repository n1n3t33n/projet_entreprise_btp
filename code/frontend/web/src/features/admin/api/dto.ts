/*
  Formes servies par l'API pour le domaine « accès et droits », calquées sur
  les classes de CL-1 et sur les conventions de nommage du MPD (snake_case,
  clés étrangères suffixées par leur table, énumérés en `UPPER_SNAKE`).

  Ces types ne sortent jamais de la couche `api`.
*/

export type RoleDto = {
  code_role: string
  libelle: string
  systeme: boolean
  actif: boolean
}

export type PermissionDto = {
  code_permission: string
  /** `ecran` pour une permission d'accès à un écran. */
  module: string
  /** Identifiant de l'écran visé. */
  ressource: string
  /** `UPPER_SNAKE` : CONSULTER, CREER, MODIFIER, VALIDER. */
  action: string
  libelle: string
}

export type DroitAccordeDto = {
  role_code_role: string
  permission_code_permission: string
  /** `UPPER_SNAKE` : GLOBALE, PERIMETRE. */
  portee: string
}
