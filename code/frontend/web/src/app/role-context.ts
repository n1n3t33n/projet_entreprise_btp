/*
  Rôle courant du poste de pilotage.

  Depuis l'arrivée de l'authentification, le rôle n'est plus choisi par
  l'utilisateur : il vient de l'affectation du compte connecté (CL-1
  `AffectationRole`). Ce contexte est alimenté par `SessionProvider` ; les
  modules continuent d'appeler `useRole()` sans connaître la session.

  `ROLES` sert encore à afficher le libellé d'un rôle et à alimenter le choix
  du rôle d'un compte dans l'écran d'administration.
*/

import { createContext, useContext } from 'react'

export type Role =
  'direction' | 'administrateur' | 'commercial' | 'acquereur' | 'responsable_technique'

export const ROLES: { value: Role; libelle: string }[] = [
  { value: 'direction', libelle: 'Direction' },
  { value: 'administrateur', libelle: 'Administrateur' },
  { value: 'commercial', libelle: 'Commercial' },
  { value: 'responsable_technique', libelle: 'Responsable technique' },
  { value: 'acquereur', libelle: 'Acquéreur' },
]

export function libelleRole(role: Role): string {
  return ROLES.find((item) => item.value === role)?.libelle ?? role
}

export type RoleContexteValeur = {
  role: Role
}

export const RoleContexte = createContext<RoleContexteValeur | null>(null)

export function useRole(): RoleContexteValeur {
  const contexte = useContext(RoleContexte)

  if (!contexte) {
    throw new Error("useRole doit être utilisé à l'intérieur de SessionProvider.")
  }

  return contexte
}
