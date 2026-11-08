/*
  Petit crochet de chargement de données, sans dépendance externe.

  Il expose un état explicite — attente, chargement, succès, erreur — plutôt
  qu'un simple « données ou undefined » : chaque écran peut alors afficher un
  squelette pendant le chargement et un message en cas d'échec, sans réinventer
  cette mécanique. C'est l'équivalent maison d'une bibliothèque de requêtes,
  suffisant pour le périmètre du pilote.

  DUPLICATION ASSUMÉE : ce crochet est pour l'instant identique à celui des
  modules stock et avancement. La factorisation vers `lib/` (un seul
  `useRequete` partagé) est volontairement renvoyée à une branche de nettoyage
  dédiée, pour que le diff de cette étape reste centré sur la fonctionnalité
  livrée et testable isolément.
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

/**
 * Charge une donnée asynchrone et suit son état.
 *
 * @param charger fonction qui produit la promesse à chaque exécution
 * @param deps dépendances qui, en changeant, relancent le chargement
 * @returns l'état courant et une fonction `recharger` pour forcer un nouvel appel
 */
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

    // On conserve les données précédentes pendant un rechargement, pour éviter
    // un clignotement de la liste quand l'utilisateur change de filtre.
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

    // Le nettoyage marque l'appel comme obsolète : si les dépendances changent
    // avant la fin de la promesse, sa réponse tardive est ignorée.
    return () => {
      annule = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, compteur])

  return { ...etat, recharger }
}
