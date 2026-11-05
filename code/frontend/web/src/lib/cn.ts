type ValeurClasse = string | false | null | undefined

/**
 * Assemble une liste de classes utilitaires en ignorant les valeurs vides.
 *
 * Permet d'écrire `cn('base', actif && 'classe-active')` sans faire apparaître
 * « false » ni d'espaces superflus dans l'attribut `class` du document.
 */
export function cn(...valeurs: ValeurClasse[]): string {
  return valeurs.filter(Boolean).join(' ')
}
