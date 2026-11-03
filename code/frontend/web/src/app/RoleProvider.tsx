import { useMemo, useState, type ReactNode } from 'react'
import { RoleContexte, type Role } from '@/app/role-context'

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, definirRole] = useState<Role>('direction')
  const valeur = useMemo(() => ({ role, definirRole }), [role])

  return <RoleContexte.Provider value={valeur}>{children}</RoleContexte.Provider>
}
