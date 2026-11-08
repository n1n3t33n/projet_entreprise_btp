/*
  Crochet de chargement de données avec état explicite (attente, chargement,
  succès, erreur) et garde anti-course.

  Note : identique à `features/stock/hooks/useRequete`. Il est dupliqué ici pour
  garder le module autonome ; un nettoyage ultérieur pourrait le remonter dans
  un dossier partagé `lib/hooks` consommé par les deux modules.
*/

import { useCallback, useEffect, useState } from 'react'

export type EtatRequete<T> =
  | { statut: 'attente'; donnees: null; erreur: null }
  | { statut: 'chargement'; donnees: T | null; erreur: null }
  | { statut: 'succes'; donnees: T; erreur: null }
  | { statut: 'erreur'; donnees: null; erreur: string }

function messageErreur(erreur: unknown): string {
  if (erreur instanceof Error && erreur.message.length > 0) {
    return erreur.message
  }
  return 'Une erreur est survenue pendant le chargement.'
}

export function useRequete<T>(
  charger: () => Promise<T>,
  deps: readonly unknown[],
): EtatRequete<T> & { recharger: () => void } {
  const [etat, setEtat] = useState<EtatRequete<T>>({
    statut: 'attente',
    donnees: null,
    erreur: null,
  })
  const [compteur, setCompteur] = useState(0)

  const recharger = useCallback(() => setCompteur((valeur) => valeur + 1), [])

  useEffect(() => {
    let annule = false

    setEtat((precedent) => ({
      statut: 'chargement',
      donnees: precedent.statut === 'succes' ? precedent.donnees : null,
      erreur: null,
    }))

    charger()
      .then((donnees) => {
        if (!annule) {
          setEtat({ statut: 'succes', donnees, erreur: null })
        }
      })
      .catch((erreur: unknown) => {
        if (!annule) {
          setEtat({ statut: 'erreur', donnees: null, erreur: messageErreur(erreur) })
        }
      })

    return () => {
      annule = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, compteur])

  return { ...etat, recharger }
}
