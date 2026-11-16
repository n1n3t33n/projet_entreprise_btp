/*
  Rôle courant du poste de pilotage.

  Depuis ltr('arrivée de l')authentification, le rôle n'est plus choisi par
  l'utilisateur : il vient de l'affectation du compte connecté (CL-1
  `AffectationRole`). Ce contexte est alimenté par `SessionProvider` ; les
  modules continuent d'appeler `useRole()` sans connaître la session.

  `ROLES` sert encore à afficher le libellé d'un rôle et à alimenter le choix
  du rôle d'un compte dans l'écran d'administration.
*/

import { createContext, useContext } from 'react'
import { tr } from '@/i18n/tr'

export type Role =
  'direction' | 'administrateur' | 'commercial' | 'acquereur' | 'responsable_technique'

export const ROLES: { value: Role; libelle: string }[] = [
  { value: 'direction', libelle: tr('Direction') },
  { value: 'administrateur', libelle: tr('Administrateur') },
  { value: 'commercial', libelle: tr('Commercial') },
  { value: 'responsable_technique', libelle: tr('Responsable technique') },
  { value: 'acquereur', libelle: tr('Acquéreur') },
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
