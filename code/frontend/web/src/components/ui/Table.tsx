import { CaretDown, CaretLeft, CaretRight, CaretUp, CaretUpDown, X } from '@phosphor-icons/react'
import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/cn'

/** Alignement du contenu d'une colonne. */
export type AlignementColonne = 'gauche' | 'centre' | 'droite'

/**
 * Description d'une colonne.
 *
 * `T` est le type d'une ligne : le tableau n'impose aucune forme aux données,
 * l'écran appelant fournit les lignes et la façon de les lire.
 */
export type ColonneTable<T> = {
  /** Identifiant unique de la colonne, utilisé pour l'état de tri. */
  cle: string
  /** En-tête affiché. */
  entete: ReactNode
  /** Contenu de la cellule pour une ligne donnée. */
  rendu: (ligne: T) => ReactNode
  /** Rend l'en-tête cliquable. Nécessite `valeurTri`. */
  triable?: boolean
  /** Valeur comparable utilisée pour le tri de cette colonne. */
  valeurTri?: (ligne: T) => string | number
  /** Alignement du contenu. `gauche` par défaut. */
  alignement?: AlignementColonne
  /** Largeur fixe, par exemple `'12rem'`. */
  largeur?: string
}

export type SensTri = 'asc' | 'desc'

/** État de tri courant : quelle colonne, dans quel sens. */
export type EtatTri = { cle: string; sens: SensTri }

export type TableProps<T> = {
  /** Objet du tableau. Rendu dans une légende destinée aux lecteurs d'écran. */
  intitule: string
  /** Colonnes, dans l'ordre d'affichage. */
  colonnes: ColonneTable<T>[]
  /** Lignes à afficher. Aucune donnée n'est produite par le composant. */
  lignes: T[]
  /** Identifiant stable d'une ligne, utilisé comme clé React et pour la sélection. */
  cleLigne: (ligne: T) => string
  /** Tri appliqué au premier affichage. */
  triInitial?: EtatTri
  /** Ajoute une case à cocher par ligne et une case « tout sélectionner ». */
  selectionnable?: boolean
  /** Appelé à chaque changement de sélection, avec les clés retenues. */
  onSelectionChanger?: (cles: string[]) => void
  /**
   * Barre d'actions groupées, affichée dès qu'au moins une ligne est
   * sélectionnée. Reçoit les lignes retenues et une fonction pour vider la
   * sélection après exécution de l'action.
   */
  actionsGroupees?: (lignes: T[], reinitialiser: () => void) => ReactNode
  /** Nombre de lignes par page. Omettre pour afficher toutes les lignes. */
  parPage?: number
  /** Message affiché quand `lignes` est vide. */
  messageVide?: string
  /** Affiche des lignes d'attente à la place des données. */
  chargement?: boolean
  /** Retire la sélection et les actions groupées, sans toucher au tri. */
  lectureSeule?: boolean
  /** Hauteur maximale de la zone défilante, par exemple `'28rem'`. */
  hauteurMax?: string
  className?: string
}

const CLASSE_ALIGNEMENT: Record<AlignementColonne, string> = {
  gauche: 'text-left',
  centre: 'text-center',
  droite: 'text-right',
}

const ARIA_SORT: Record<SensTri, 'ascending' | 'descending'> = {
  asc: 'ascending',
  desc: 'descending',
}

export function Table<T>({
  intitule,
  colonnes,
  lignes,
  cleLigne,
  triInitial,
  selectionnable = false,
  onSelectionChanger,
  actionsGroupees,
  parPage,
  messageVide = 'Aucune ligne à afficher.',
  chargement = false,
  lectureSeule = false,
  hauteurMax,
  className,
}: TableProps<T>) {
  const [tri, setTri] = useState<EtatTri | null>(triInitial ?? null)
  const [page, setPage] = useState(0)
  const [selection, setSelection] = useState<string[]>([])
  const referenceToutCocher = useRef<HTMLInputElement>(null)

  const selectionActive = selectionnable && !lectureSeule
  const taillePage = parPage && parPage > 0 ? parPage : 0

  const lignesTriees = useMemo(() => {
    if (!tri) {
      return lignes
    }

    const colonne = colonnes.find((element) => element.cle === tri.cle)
    const extraire = colonne?.valeurTri
    if (!extraire) {
      return lignes
    }

    const triees = [...lignes].sort((a, b) => {
      const valeurA = extraire(a)
      const valeurB = extraire(b)

      if (typeof valeurA === 'number' && typeof valeurB === 'number') {
        return valeurA - valeurB
      }
      return String(valeurA).localeCompare(String(valeurB), 'fr', {
        numeric: true,
        sensitivity: 'base',
      })
    })

    return tri.sens === 'desc' ? triees.reverse() : triees
  }, [colonnes, lignes, tri])

  const nombrePages = taillePage ? Math.max(1, Math.ceil(lignesTriees.length / taillePage)) : 1

  // Si le filtrage amont réduit la liste, la page courante peut ne plus exister.
  useEffect(() => {
    if (page > nombrePages - 1) {
      setPage(0)
    }
  }, [nombrePages, page])

  const lignesVisibles = taillePage
    ? lignesTriees.slice(page * taillePage, page * taillePage + taillePage)
    : lignesTriees

  const clesVisibles = lignesVisibles.map(cleLigne)
  const nombreSelectionneVisible = clesVisibles.filter((cle) => selection.includes(cle)).length
  const toutesVisiblesSelectionnees =
    clesVisibles.length > 0 && nombreSelectionneVisible === clesVisibles.length

  // L'état « partiellement cochée » d'une case n'existe pas en HTML :
  // il se pose sur l'élément du document, après le rendu.
  useEffect(() => {
    const caseEntete = referenceToutCocher.current
    if (caseEntete) {
      caseEntete.indeterminate =
        nombreSelectionneVisible > 0 && nombreSelectionneVisible < clesVisibles.length
    }
  }, [nombreSelectionneVisible, clesVisibles.length])

  const lignesSelectionnees = useMemo(
    () => lignes.filter((ligne) => selection.includes(cleLigne(ligne))),
    [cleLigne, lignes, selection],
  )

  function appliquerSelection(cles: string[]) {
    setSelection(cles)
    onSelectionChanger?.(cles)
  }

  function basculerLigne(cle: string) {
    appliquerSelection(
      selection.includes(cle)
        ? selection.filter((element) => element !== cle)
        : [...selection, cle],
    )
  }

  function basculerPageEntiere() {
    if (toutesVisiblesSelectionnees) {
      appliquerSelection(selection.filter((cle) => !clesVisibles.includes(cle)))
      return
    }
    const ajoutees = clesVisibles.filter((cle) => !selection.includes(cle))
    appliquerSelection([...selection, ...ajoutees])
  }

  function viderSelection() {
    appliquerSelection([])
  }

  /** Cycle de tri d'une colonne : croissant, décroissant, puis ordre d'origine. */
  function basculerTri(cle: string) {
    setTri((precedent) => {
      if (!precedent || precedent.cle !== cle) {
        return { cle, sens: 'asc' }
      }
      if (precedent.sens === 'asc') {
        return { cle, sens: 'desc' }
      }
      return null
    })
  }

  const nombreColonnes = colonnes.length + (selectionActive ? 1 : 0)
  const premiereLigneAffichee = lignesTriees.length === 0 ? 0 : page * taillePage + 1
  const derniereLigneAffichee = taillePage
    ? Math.min(lignesTriees.length, page * taillePage + taillePage)
    : lignesTriees.length

  return (
    <div className={cn('flex min-w-0 flex-col', className)}>
      {selectionActive && actionsGroupees && selection.length > 0 && (
        <div className="animate-cascade mb-3 flex flex-wrap items-center gap-3 rounded-controle border border-sarcelle/30 bg-fond-alt px-4 py-3">
          <p className="text-sm font-semibold text-marine">
            {selection.length} ligne{selection.length > 1 ? 's' : ''} sélectionnée
            {selection.length > 1 ? 's' : ''}
          </p>
          <div className="flex flex-wrap items-center gap-2">
            {actionsGroupees(lignesSelectionnees, viderSelection)}
          </div>
          <Button
            variante="discret"
            taille="sm"
            icone={X}
            onClick={viderSelection}
            className="ml-auto"
          >
            Tout désélectionner
          </Button>
        </div>
      )}

      {/* Un seul conteneur gère les deux défilements : horizontal pour les
          colonnes nombreuses, vertical pour l'en-tête collant. */}
      <div
        className="min-w-0 overflow-auto rounded-carte border border-bordure bg-surface"
        style={hauteurMax ? { maxHeight: hauteurMax } : undefined}
      >
        <table className="w-full border-collapse text-sm">
          <caption className="sr-only">{intitule}</caption>

          <thead className="sticky top-0 z-10 bg-fond-alt">
            <tr>
              {selectionActive && (
                <th scope="col" className="w-12 px-4 py-3">
                  <input
                    ref={referenceToutCocher}
                    type="checkbox"
                    checked={toutesVisiblesSelectionnees}
                    onChange={basculerPageEntiere}
                    aria-label="Sélectionner toutes les lignes de la page"
                    className="size-4 cursor-pointer accent-marine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle focus-visible:ring-offset-2"
                  />
                </th>
              )}

              {colonnes.map((colonne) => {
                const estTriee = tri?.cle === colonne.cle
                const triPossible = colonne.triable === true && Boolean(colonne.valeurTri)
                const IconeTri = !estTriee ? CaretUpDown : tri?.sens === 'asc' ? CaretUp : CaretDown

                return (
                  <th
                    key={colonne.cle}
                    scope="col"
                    aria-sort={
                      triPossible ? (estTriee && tri ? ARIA_SORT[tri.sens] : 'none') : undefined
                    }
                    style={colonne.largeur ? { width: colonne.largeur } : undefined}
                    className={cn(
                      'whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-wide text-texte-secondaire',
                      CLASSE_ALIGNEMENT[colonne.alignement ?? 'gauche'],
                    )}
                  >
                    {triPossible ? (
                      <button
                        type="button"
                        onClick={() => basculerTri(colonne.cle)}
                        className={cn(
                          'inline-flex items-center gap-1.5 rounded-controle px-1 py-0.5 uppercase tracking-wide',
                          'transition-colors duration-[var(--duree-bouton)] ease-out hover:text-marine',
                          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle',
                          estTriee && 'text-marine',
                        )}
                      >
                        <span>{colonne.entete}</span>
                        <IconeTri size={14} weight="bold" aria-hidden />
                        <span className="sr-only">Trier par cette colonne</span>
                      </button>
                    ) : (
                      colonne.entete
                    )}
                  </th>
                )
              })}
            </tr>
          </thead>

          <tbody>
            {chargement &&
              Array.from({ length: taillePage || 5 }, (_, index) => (
                <tr key={`attente-${index}`} className="border-t border-bordure">
                  {Array.from({ length: nombreColonnes }, (__, colonne) => (
                    <td key={`attente-${index}-${colonne}`} className="px-4 py-3">
                      <div className="h-4 w-full animate-pulse rounded bg-fond-alt" />
                    </td>
                  ))}
                </tr>
              ))}

            {!chargement && lignesVisibles.length === 0 && (
              <tr>
                <td
                  colSpan={nombreColonnes}
                  className="px-4 py-10 text-center text-texte-secondaire"
                >
                  {messageVide}
                </td>
              </tr>
            )}

            {!chargement &&
              lignesVisibles.map((ligne) => {
                const cle = cleLigne(ligne)
                const selectionnee = selection.includes(cle)

                return (
                  <tr
                    key={cle}
                    className={cn(
                      'border-t border-bordure transition-colors duration-[var(--duree-survol)] ease-out',
                      selectionnee ? 'bg-or-vif/30' : 'hover:bg-fond',
                    )}
                  >
                    {selectionActive && (
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          checked={selectionnee}
                          onChange={() => basculerLigne(cle)}
                          aria-label={`Sélectionner la ligne ${cle}`}
                          className="size-4 cursor-pointer accent-marine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle focus-visible:ring-offset-2"
                        />
                      </td>
                    )}

                    {colonnes.map((colonne) => (
                      <td
                        key={colonne.cle}
                        className={cn(
                          'whitespace-nowrap px-4 py-3 text-texte',
                          CLASSE_ALIGNEMENT[colonne.alignement ?? 'gauche'],
                        )}
                      >
                        {colonne.rendu(ligne)}
                      </td>
                    ))}
                  </tr>
                )
              })}
          </tbody>
        </table>
      </div>

      {taillePage > 0 && !chargement && (
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-texte-secondaire" aria-live="polite">
            {lignesTriees.length === 0
              ? 'Aucune ligne'
              : `Lignes ${premiereLigneAffichee} à ${derniereLigneAffichee} sur ${lignesTriees.length}`}
          </p>

          <div className="flex items-center gap-2">
            <Button
              variante="secondaire"
              taille="sm"
              icone={CaretLeft}
              disabled={page === 0}
              onClick={() => setPage((precedente) => Math.max(0, precedente - 1))}
            >
              Précédent
            </Button>
            <span className="text-sm text-texte-secondaire">
              Page {page + 1} sur {nombrePages}
            </span>
            <Button
              variante="secondaire"
              taille="sm"
              icone={CaretRight}
              positionIcone="apres"
              disabled={page >= nombrePages - 1}
              onClick={() => setPage((precedente) => Math.min(nombrePages - 1, precedente + 1))}
            >
              Suivant
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
