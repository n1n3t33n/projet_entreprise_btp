import { useEffect, useRef, useState } from 'react'

/** Phase d'animation d'un panneau superposé. */
export type PhaseOverlay = 'entree' | 'sortie'

type ReferenceElement = { current: HTMLElement | null }

/**
 * Maintient un panneau monté le temps de son animation de sortie.
 *
 * Sans ce décalage, passer `ouvert` à `false` retirerait immédiatement le
 * panneau du document et l'animation de fermeture ne serait jamais visible.
 *
 * @param ouvert état demandé par le composant appelant
 * @param dureeSortieMs durée de l'animation de sortie
 */
export function usePresence(
  ouvert: boolean,
  dureeSortieMs: number,
): { present: boolean; phase: PhaseOverlay } {
  const [present, setPresent] = useState(ouvert)
  const [phase, setPhase] = useState<PhaseOverlay>(ouvert ? 'entree' : 'sortie')

  useEffect(() => {
    if (ouvert) {
      setPresent(true)
      setPhase('entree')
      return undefined
    }

    setPhase('sortie')
    const minuteur = window.setTimeout(() => setPresent(false), dureeSortieMs)
    return () => window.clearTimeout(minuteur)
  }, [ouvert, dureeSortieMs])

  return { present, phase }
}

/*
  Le verrou de défilement est compté : deux panneaux superposés peuvent être
  ouverts en même temps, et le défilement de la page ne doit être rendu qu'une
  fois le dernier refermé.
*/
let verrousActifs = 0
let debordementInitial = ''

/** Empêche la page de défiler derrière un panneau superposé ouvert. */
export function useVerrouScroll(actif: boolean): void {
  useEffect(() => {
    if (!actif) {
      return undefined
    }

    if (verrousActifs === 0) {
      debordementInitial = document.body.style.overflow
      document.body.style.overflow = 'hidden'
    }
    verrousActifs += 1

    return () => {
      verrousActifs -= 1
      if (verrousActifs === 0) {
        document.body.style.overflow = debordementInitial
      }
    }
  }, [actif])
}

const SELECTEUR_FOCUSABLE = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ')

/**
 * Confine le focus clavier à l'intérieur d'un panneau superposé.
 *
 * Trois responsabilités : placer le focus sur le premier contrôle à
 * l'ouverture, faire boucler la touche Tab sur les contrôles du panneau, et
 * rendre le focus au contrôle qui a ouvert le panneau à la fermeture.
 *
 * @param reference conteneur du panneau
 * @param actif vrai tant que le panneau est ouvert
 * @param onFermer appelé sur la touche Échap
 */
export function useFocusPiege(
  reference: ReferenceElement,
  actif: boolean,
  onFermer: () => void,
): void {
  const declencheur = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (!actif) {
      return undefined
    }

    const conteneur = reference.current
    if (!conteneur) {
      return undefined
    }

    declencheur.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null

    const listerFocusables = () =>
      Array.from(conteneur.querySelectorAll<HTMLElement>(SELECTEUR_FOCUSABLE)).filter(
        (element) => element.offsetParent !== null,
      )

    const premier = listerFocusables()[0]
    if (premier) {
      premier.focus()
    } else {
      conteneur.focus()
    }

    const auClavier = (evenement: KeyboardEvent) => {
      if (evenement.key === 'Escape') {
        evenement.preventDefault()
        evenement.stopPropagation()
        onFermer()
        return
      }

      if (evenement.key !== 'Tab') {
        return
      }

      const focusables = listerFocusables()
      const debut = focusables[0]
      const fin = focusables[focusables.length - 1]

      if (!debut || !fin) {
        evenement.preventDefault()
        conteneur.focus()
        return
      }

      const elementActif = document.activeElement

      if (evenement.shiftKey && (elementActif === debut || !conteneur.contains(elementActif))) {
        evenement.preventDefault()
        fin.focus()
        return
      }

      if (!evenement.shiftKey && elementActif === fin) {
        evenement.preventDefault()
        debut.focus()
      }
    }

    document.addEventListener('keydown', auClavier, true)

    return () => {
      document.removeEventListener('keydown', auClavier, true)
      declencheur.current?.focus()
    }
  }, [actif, onFermer, reference])
}
