/*
  Capacités du module stock pour le rôle actuellement sélectionné.

  Lit le rôle dans le contexte de l'application et le traduit en capacités via
  la table déclarative de `config/capacites`. Les écrans appellent ce crochet
  et ne touchent jamais au rôle brut.
*/

import { useRole } from '@/app/role-context'
import { capacitesStockPourRole, type CapacitesStock } from '@/features/stock/config/capacites'

export function useCapacitesStock(): CapacitesStock {
  const { role } = useRole()
  return capacitesStockPourRole(role)
}
