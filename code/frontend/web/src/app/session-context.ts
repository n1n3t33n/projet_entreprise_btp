/*
  Session du poste de pilotage.

  Le rôle courant n'est plus choisi dans la barre supérieure : il provient du
  compte connecté (CL-1 `AffectationRole`). Ce contexte est la seule source de
  la session ; `role-context` n'en est qu'une projection, pour que les modules
  existants continuent d'appeler `useRole()` sans rien savoir de la connexion.
*/

import { createContext, useContext } from 'react'
import type { Session } from '@/features/auth/types/domaine'

export type SessionContexteValeur = {
  session: Session | null
  /** Vrai dès qu'une session est ouverte. */
  connecte: boolean
  /** Enregistre la session après une connexion réussie. */
  ouvrirSession: (session: Session) => void
  /** Ferme la session, localement et côté serveur. */
  fermerSession: () => void
}

export const SessionContexte = createContext<SessionContexteValeur | null>(null)

export function useSession(): SessionContexteValeur {
  const contexte = useContext(SessionContexte)

  if (!contexte) {
    throw new Error("useSession doit être utilisé à l'intérieur de SessionProvider.")
  }

  return contexte
}
