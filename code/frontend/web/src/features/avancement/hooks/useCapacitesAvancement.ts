/*
  Capacités du module avancement pour le rôle actuellement sélectionné.
*/

import { useRole } from '@/app/role-context'
import {
  capacitesAvancementPourRole,
  type CapacitesAvancement,
} from '@/features/avancement/config/capacites'

export function useCapacitesAvancement(): CapacitesAvancement {
  const { role } = useRole()
  return capacitesAvancementPourRole(role)
}
