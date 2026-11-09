/*
  Chargement et mise à disposition de la matrice des droits.

  Les droits sont chargés une fois au démarrage, puis rechargés après chaque
  enregistrement dans l'écran d'administration. Tant qu'ils ne sont pas
  arrivés, `chargement` reste vrai : la garde de route attend plutôt que de
  rediriger à tort.
*/

import { useCallback, useMemo, type ReactNode } from 'react'
import { DroitsContexte, type DroitsContexteValeur } from '@/app/droits-context'
import type { Role } from '@/app/role-context'
import { ECRANS, type EntreeNavigation, type IdEcran } from '@/config/navigation'
import { chargerDroits } from '@/features/admin/api'
import { useRequete } from '@/lib/hooks/useRequete'

export function DroitsProvider({ children }: { children: ReactNode }) {
  const etatRequete = useRequete(chargerDroits, [])
  const etat = etatRequete.donnees

  /*
    Index « rôle → écrans autorisés », reconstruit à chaque changement de
    l'état. Un droit accordé ne compte que s'il porte sur une permission de
    lecture d'écran (`action = 'lire'`, littéral du modèle MPD-1) : les futures
    permissions d'action (créer, valider…) n'ouvriront pas un écran à elles
    seules.
  */
  const parRole = useMemo(() => {
    const index = new Map<string, Set<IdEcran>>()
    if (!etat) {
      return index
    }

    const ecranParPermission = new Map(
      etat.permissions
        .filter((permission) => permission.action === 'lire')
        .map((permission) => [permission.code, permission.idEcran]),
    )

    for (const droit of etat.accordes) {
      const idEcran = ecranParPermission.get(droit.codePermission)
      if (!idEcran) {
        continue
      }
      const ensemble = index.get(droit.codeRole) ?? new Set<IdEcran>()
      ensemble.add(idEcran)
      index.set(droit.codeRole, ensemble)
    }

    return index
  }, [etat])

  const ecransAutorises = useCallback(
    (role: Role): EntreeNavigation[] => {
      const autorises = parRole.get(role)
      if (!autorises) {
        return []
      }
      return ECRANS.filter((ecran) => autorises.has(ecran.id))
    },
    [parRole],
  )

  const ecranAutorise = useCallback(
    (ecran: IdEcran, role: Role): boolean => parRole.get(role)?.has(ecran) ?? false,
    [parRole],
  )

  const cheminAccueil = useCallback(
    (role: Role): string | null => ecransAutorises(role)[0]?.chemin ?? null,
    [ecransAutorises],
  )

  const valeur = useMemo<DroitsContexteValeur>(
    () => ({
      chargement: etatRequete.statut === 'attente' || etatRequete.statut === 'chargement',
      erreur: etatRequete.statut === 'erreur' ? etatRequete.erreur : null,
      etat,
      ecransAutorises,
      ecranAutorise,
      cheminAccueil,
      recharger: etatRequete.recharger,
    }),
    [
      etatRequete.statut,
      etatRequete.erreur,
      etatRequete.recharger,
      etat,
      ecransAutorises,
      ecranAutorise,
      cheminAccueil,
    ],
  )

  return <DroitsContexte.Provider value={valeur}>{children}</DroitsContexte.Provider>
}
