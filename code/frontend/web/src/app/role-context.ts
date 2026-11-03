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

export type RoleContexteValeur = {
  role: Role
  definirRole: (role: Role) => void
}

export const RoleContexte = createContext<RoleContexteValeur | null>(null)

export function useRole(): RoleContexteValeur {
  const contexte = useContext(RoleContexte)

  if (!contexte) {
    throw new Error("useRole doit être utilisé à l'intérieur de RoleProvider.")
  }

  return contexte
}
