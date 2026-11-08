/*
  Rôle courant du poste de pilotage.

  En attendant l'authentification, le rôle est choisi par le sélecteur de la
  barre supérieure. Il est conservé dans le stockage de session du navigateur :
  un rechargement de page ne le remet plus à « Direction ». Le stockage peut
  être indisponible (navigation privée stricte) : on retombe alors sans erreur
  sur le rôle par défaut.
*/

import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { RoleContexte, ROLES, type Role } from '@/app/role-context'

const CLE_STOCKAGE = 'chantiersync.role'
const ROLE_PAR_DEFAUT: Role = 'direction'

function estRole(valeur: unknown): valeur is Role {
  return ROLES.some((item) => item.value === valeur)
}

function lireRoleMemorise(): Role {
  try {
    const valeur = window.sessionStorage.getItem(CLE_STOCKAGE)
    return estRole(valeur) ? valeur : ROLE_PAR_DEFAUT
  } catch {
    return ROLE_PAR_DEFAUT
  }
}

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>(lireRoleMemorise)

  const definirRole = useCallback((nouveau: Role) => {
    setRole(nouveau)
    try {
      window.sessionStorage.setItem(CLE_STOCKAGE, nouveau)
    } catch {
      // Stockage indisponible : le rôle reste valable pour la session en cours.
    }
  }, [])

  const valeur = useMemo(() => ({ role, definirRole }), [role, definirRole])

  return <RoleContexte.Provider value={valeur}>{children}</RoleContexte.Provider>
}
