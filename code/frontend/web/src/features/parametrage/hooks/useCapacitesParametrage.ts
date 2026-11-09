/*
  Capacités du module parametrage pour le rôle de la session.
*/

import { useRole } from '@/app/role-context'
import {
  capacitesParametragePourRole,
  type CapacitesParametrage,
} from '@/features/parametrage/config/capacites'

export function useCapacitesParametrage(): CapacitesParametrage {
  const { role } = useRole()
  return capacitesParametragePourRole(role)
}
