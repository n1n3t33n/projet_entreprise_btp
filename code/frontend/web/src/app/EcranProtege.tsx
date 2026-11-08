/*
  Garde de route : n'affiche un écran que si le rôle courant y a accès.

  L'autorisation vient de la matrice des droits chargée depuis l'API
  (`app/droits-context`), jamais d'une liste écrite dans le code : ce que
  l'administrateur coche dans l'écran « Comptes et matrice des droits »
  s'applique aussitôt ici. Un accès direct par l'adresse ne peut donc pas
  contourner le menu (charte § 9.3 : « une action n'apparaît jamais pour un
  rôle qui n'y a pas droit »).
*/

import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { ChargementModule } from '@/app/ChargementModule'
import { useDroits } from '@/app/droits-context'
import { useRole } from '@/app/role-context'
import { Card } from '@/components/ui'
import type { IdEcran } from '@/config/navigation'

/** Message affiché à un rôle auquel plus aucun écran n'est ouvert. */
function AucunAcces({ message }: { message: string }) {
  return (
    <Card titre="Aucun écran accessible">
      <p className="text-sm text-texte-secondaire">{message}</p>
    </Card>
  )
}

/** Écran d'attente ou message d'erreur commun, tant que les droits manquent. */
function EtatDroitsIndisponible(): ReactNode | null {
  const { chargement, erreur } = useDroits()

  if (chargement) {
    return <ChargementModule />
  }
  if (erreur) {
    return (
      <Card titre="Droits d'accès indisponibles">
        <p className="text-sm text-danger">{erreur}</p>
      </Card>
    )
  }
  return null
}

export type EcranProtegeProps = {
  ecran: IdEcran
  children: ReactNode
}

export function EcranProtege({ ecran, children }: EcranProtegeProps) {
  const { role } = useRole()
  const { ecranAutorise, cheminAccueil } = useDroits()

  const indisponible = EtatDroitsIndisponible()
  if (indisponible) {
    return indisponible
  }

  if (ecranAutorise(ecran, role)) {
    return <>{children}</>
  }

  const accueil = cheminAccueil(role)
  if (!accueil) {
    // Aucun écran ouvert : rediriger bouclerait indéfiniment.
    return (
      <AucunAcces message="Aucun écran n'est ouvert à ce rôle. Un administrateur peut lui accorder des accès depuis la matrice des droits." />
    )
  }

  return <Navigate to={accueil} replace />
}

/** Redirection de la racine vers le premier écran ouvert au rôle courant. */
export function RedirectionAccueil() {
  const { role } = useRole()
  const { cheminAccueil } = useDroits()

  const indisponible = EtatDroitsIndisponible()
  if (indisponible) {
    return indisponible
  }

  const accueil = cheminAccueil(role)
  if (!accueil) {
    return (
      <AucunAcces message="Aucun écran n'est ouvert à ce rôle. Un administrateur peut lui accorder des accès depuis la matrice des droits." />
    )
  }

  return <Navigate to={accueil} replace />
}
