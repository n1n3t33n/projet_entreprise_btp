import type { CSSProperties } from 'react'

/**
 * Durée d'une animation de sortie, en millisecondes.
 *
 * Doit rester identique à `--duree-sortie` dans `src/index.css` : la feuille de
 * style pilote l'animation, cette constante indique au code JavaScript combien
 * de temps garder un panneau monté avant de le retirer du document.
 */
export const DUREE_SORTIE_MS = 140

/** Décalage par défaut entre deux éléments d'une même cascade, en millisecondes. */
export const PAS_CASCADE_MS = 40

/**
 * Décalage d'entrée d'un élément à l'intérieur d'une cascade.
 *
 * À combiner avec la classe `animate-cascade` : la classe porte l'animation,
 * ce style en ligne porte seulement le retard propre à la position de l'élément.
 */
export function delaiCascade(index: number, pasMs: number = PAS_CASCADE_MS): CSSProperties {
  return { animationDelay: `${index * pasMs}ms` }
}
