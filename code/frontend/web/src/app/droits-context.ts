/*
  Droits d'accès aux écrans, chargés depuis l'API et partagés par la coquille.

  Le menu (`Sidebar`), la garde de route (`EcranProtege`) et l'écran
  d'administration lisent tous cet état : il n'existe aucune autre source de
  vérité sur « qui voit quel écran ». Modifier la matrice dans l'écran
  d'administration met donc immédiatement le menu à jour.
*/

import { createContext, useContext } from 'react'
import type { Role } from '@/app/role-context'
import type { EntreeNavigation, IdEcran } from '@/config/navigation'
import type { EtatDroits } from '@/features/admin/types/domaine'

export type DroitsContexteValeur = {
  /** Vrai tant que les droits n'ont pas été chargés : ne rien décider avant. */
  chargement: boolean
  /** Message d'erreur si le chargement a échoué. */
  erreur: string | null
  /** État brut (rôles, permissions, droits accordés), pour l'écran d'administration. */
  etat: EtatDroits | null
  /** Écrans ouverts à ce rôle, dans l'ordre du menu. */
  ecransAutorises: (role: Role) => EntreeNavigation[]
  /** Vrai si ce rôle peut ouvrir cet écran. */
  ecranAutorise: (ecran: IdEcran, role: Role) => boolean
  /** Premier écran ouvert à ce rôle, ou `null` si aucun. */
  cheminAccueil: (role: Role) => string | null
  /** Recharge la matrice après un enregistrement. */
  recharger: () => void
}

export const DroitsContexte = createContext<DroitsContexteValeur | null>(null)

export function useDroits(): DroitsContexteValeur {
  const contexte = useContext(DroitsContexte)

  if (!contexte) {
    throw new Error("useDroits doit être utilisé à l'intérieur de DroitsProvider.")
  }

  return contexte
}
