/*
  Conservation de la session et projection du rôle courant.

  La session est gardée dans le stockage de session du navigateur : un
  rechargement d'onglet ne déconnecte pas, mais la fermeture de l'onglet si.

  LIMITE ASSUMÉE : en production, un jeton de session se garde dans un cookie
  `httpOnly`, inaccessible au script, et non dans le stockage du navigateur.
  Le choix actuel tient tant que l'API est simulée ; il devra être repris avec
  le backend Django (le cahier des charges impose HTTPS et des mots de passe
  hachés, mais ne fixe pas le transport du jeton).
*/

import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { SessionContexte, type SessionContexteValeur } from '@/app/session-context'
import { RoleContexte, type Role } from '@/app/role-context'
import { seDeconnecter } from '@/features/auth/api'
import type { Session } from '@/features/auth/types/domaine'

const CLE_SESSION = 'chantiersync.session'

/** Rôle appliqué hors session : le plus restreint, pour ne rien ouvrir par défaut. */
const ROLE_SANS_SESSION: Role = 'acquereur'

function lireSessionMemorisee(): Session | null {
  try {
    const brut = window.sessionStorage.getItem(CLE_SESSION)
    if (!brut) {
      return null
    }
    const valeur = JSON.parse(brut) as Session
    return valeur.utilisateur?.identifiant ? valeur : null
  } catch {
    return null
  }
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(lireSessionMemorisee)

  const ouvrirSession = useCallback((nouvelle: Session) => {
    setSession(nouvelle)
    try {
      window.sessionStorage.setItem(CLE_SESSION, JSON.stringify(nouvelle))
    } catch {
      // Stockage indisponible : la session vaut pour l'onglet en cours.
    }
  }, [])

  const fermerSession = useCallback(() => {
    setSession(null)
    try {
      window.sessionStorage.removeItem(CLE_SESSION)
    } catch {
      // Rien à nettoyer si le stockage est indisponible.
    }
    // La déconnexion locale ne dépend pas de la réponse du serveur : on ne
    // laisse pas un réseau en panne retenir l'utilisateur dans l'application.
    void seDeconnecter().catch(() => undefined)
  }, [])

  const valeurSession = useMemo<SessionContexteValeur>(
    () => ({ session, connecte: session !== null, ouvrirSession, fermerSession }),
    [session, ouvrirSession, fermerSession],
  )

  const valeurRole = useMemo(
    () => ({ role: session?.utilisateur.role ?? ROLE_SANS_SESSION }),
    [session],
  )

  return (
    <SessionContexte.Provider value={valeurSession}>
      <RoleContexte.Provider value={valeurRole}>{children}</RoleContexte.Provider>
    </SessionContexte.Provider>
  )
}
