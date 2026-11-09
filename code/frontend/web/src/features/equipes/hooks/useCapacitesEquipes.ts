/*
  Capacités du module équipes pour le rôle de la session. Les écrans appellent
  ce crochet et ne touchent jamais au rôle brut.
*/

import { useRole } from '@/app/role-context'
import { capacitesEquipesPourRole, type CapacitesEquipes } from '@/features/equipes/config/capacites'

export function useCapacitesEquipes(): CapacitesEquipes {
  const { role } = useRole()
  return capacitesEquipesPourRole(role)
}
