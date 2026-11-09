/*
  Capacités du module pilotage pour le rôle de la session.

  Lit le rôle dans le contexte de l'application et le traduit en capacités via
  la table déclarative de `config/capacites`. Les écrans appellent ce crochet
  et ne touchent jamais au rôle brut.
*/

import { useRole } from '@/app/role-context'
import {
  capacitesPilotagePourRole,
  type CapacitesPilotage,
} from '@/features/pilotage/config/capacites'

export function useCapacitesPilotage(): CapacitesPilotage {
  const { role } = useRole()
  return capacitesPilotagePourRole(role)
}
