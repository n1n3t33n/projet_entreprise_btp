/*
  Capacités du module gammes pour le rôle de la session. Les écrans appellent ce
  crochet et ne touchent jamais au rôle brut.
*/

import { useRole } from '@/app/role-context'
import { capacitesGammesPourRole, type CapacitesGammes } from '@/features/gammes/config/capacites'

export function useCapacitesGammes(): CapacitesGammes {
  const { role } = useRole()
  return capacitesGammesPourRole(role)
}
