import { CaretDown, CaretRight, type Icon } from '@phosphor-icons/react'
import { useMemo, useRef, useState, type KeyboardEvent, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

export type NoeudArbre = {
  /** Identifiant unique dans tout l'arbre. */
  id: string
  /** Libellé affiché. */
  libelle: string
  /** Icône Phosphor facultative. */
  icone?: Icon
  /** Information courte alignée à droite, par exemple un nombre d'articles. */
  badge?: ReactNode
  /** Nœuds enfants. Un nœud sans enfants est une feuille. */
  enfants?: NoeudArbre[]
  /** Rend le nœud non sélectionnable, sans le retirer de l'arbre. */
  desactive?: boolean
}

export type TreeProps = {
  /** Nom de l'arbre, lu par les lecteurs d'écran. */
  intitule: string
  /** Racines de l'arbre. */
  noeuds: NoeudArbre[]
  /** Identifiant du nœud sélectionné. L'arbre est piloté par l'appelant. */
  selectionne?: string
  /** Appelé avec l'identifiant du nœud choisi. */
  onSelectionner?: (id: string) => void
  /** Nœuds dépliés au premier affichage. */
  ouvertsInitiaux?: string[]
  /** Autorise la navigation et le dépliage, mais plus la sélection. */
  lectureSeule?: boolean
  className?: string
}

type NoeudAplati = {
  noeud: NoeudArbre
  niveau: number
  parentId: string | null
}

/**
 * Aplatit les nœuds actuellement visibles dans l'ordre d'affichage.
 *
 * L'arbre reste rendu de façon imbriquée, pour que la structure du document
 * traduise la hiérarchie. Cette liste à plat ne sert qu'au clavier : les
 * flèches haut et bas doivent se déplacer de ligne en ligne, en traversant les
 * niveaux, ce qu'une structure imbriquée ne permet pas d'exprimer simplement.
 */
function aplatir(
  noeuds: NoeudArbre[],
  ouverts: string[],
  niveau = 0,
  parentId: string | null = null,
): NoeudAplati[] {
  return noeuds.flatMap((noeud) => {
    const entree: NoeudAplati = { noeud, niveau, parentId }
    const enfants = noeud.enfants

    if (enfants && enfants.length > 0 && ouverts.includes(noeud.id)) {
      return [entree, ...aplatir(enfants, ouverts, niveau + 1, noeud.id)]
    }

    return [entree]
  })
}

export function Tree({
  intitule,
  noeuds,
  selectionne,
  onSelectionner,
  ouvertsInitiaux = [],
  lectureSeule = false,
  className,
}: TreeProps) {
  const [ouverts, setOuverts] = useState<string[]>(ouvertsInitiaux)
  const [focusId, setFocusId] = useState<string | null>(null)
  const [arbreFocalise, setArbreFocalise] = useState(false)
  const references = useRef<Map<string, HTMLLIElement>>(new Map())

  const visibles = useMemo(() => aplatir(noeuds, ouverts), [noeuds, ouverts])

  /*
    Un arbre ne comporte qu'un seul arrêt de tabulation. Tant que l'utilisateur
    n'a pas déplacé le focus, c'est le premier nœud visible qui le porte.
  */
  const premierVisible = visibles[0]
  const idFocusable = focusId ?? premierVisible?.noeud.id ?? null

  function enregistrerReference(id: string, element: HTMLLIElement | null) {
    if (element) {
      references.current.set(id, element)
    } else {
      references.current.delete(id)
    }
  }

  function deplacerFocus(id: string) {
    setFocusId(id)
    references.current.get(id)?.focus()
  }

  function ouvrirNoeud(id: string) {
    setOuverts((liste) => (liste.includes(id) ? liste : [...liste, id]))
  }

  function fermerNoeud(id: string) {
    setOuverts((liste) => liste.filter((identifiant) => identifiant !== id))
  }

  function basculerNoeud(id: string) {
    setOuverts((liste) =>
      liste.includes(id) ? liste.filter((identifiant) => identifiant !== id) : [...liste, id],
    )
  }

  function selectionnerNoeud(noeud: NoeudArbre) {
    if (lectureSeule || noeud.desactive === true) {
      return
    }
    onSelectionner?.(noeud.id)
  }

  function auClavier(evenement: KeyboardEvent<HTMLUListElement>) {
    if (!idFocusable) {
      return
    }

    const position = visibles.findIndex((entree) => entree.noeud.id === idFocusable)
    const courant = position >= 0 ? visibles[position] : undefined
    if (!courant) {
      return
    }

    const enfants = courant.noeud.enfants
    const aDesEnfants = Boolean(enfants && enfants.length > 0)
    const estOuvert = ouverts.includes(courant.noeud.id)

    switch (evenement.key) {
      case 'ArrowDown': {
        const suivant = visibles[position + 1]
        if (suivant) {
          evenement.preventDefault()
          deplacerFocus(suivant.noeud.id)
        }
        break
      }

      case 'ArrowUp': {
        const precedent = visibles[position - 1]
        if (precedent) {
          evenement.preventDefault()
          deplacerFocus(precedent.noeud.id)
        }
        break
      }

      case 'ArrowRight': {
        evenement.preventDefault()
        if (aDesEnfants && !estOuvert) {
          ouvrirNoeud(courant.noeud.id)
          break
        }
        // Un nœud déjà déplié : la flèche droite entre dans le premier enfant,
        // qui est forcément la ligne visible suivante.
        const premierEnfant = visibles[position + 1]
        if (aDesEnfants && estOuvert && premierEnfant) {
          deplacerFocus(premierEnfant.noeud.id)
        }
        break
      }

      case 'ArrowLeft': {
        evenement.preventDefault()
        if (aDesEnfants && estOuvert) {
          fermerNoeud(courant.noeud.id)
          break
        }
        if (courant.parentId) {
          deplacerFocus(courant.parentId)
        }
        break
      }

      case 'Home': {
        if (premierVisible) {
          evenement.preventDefault()
          deplacerFocus(premierVisible.noeud.id)
        }
        break
      }

      case 'End': {
        const dernier = visibles[visibles.length - 1]
        if (dernier) {
          evenement.preventDefault()
          deplacerFocus(dernier.noeud.id)
        }
        break
      }

      case 'Enter':
      case ' ': {
        evenement.preventDefault()
        if (aDesEnfants) {
          basculerNoeud(courant.noeud.id)
        }
        selectionnerNoeud(courant.noeud)
        break
      }

      default:
        break
    }
  }

  function rendreNiveau(liste: NoeudArbre[], niveau: number) {
    return liste.map((noeud) => {
      const enfants = noeud.enfants
      const aDesEnfants = Boolean(enfants && enfants.length > 0)
      const estOuvert = ouverts.includes(noeud.id)
      const estSelectionne = selectionne === noeud.id
      const porteLeFocus = arbreFocalise && idFocusable === noeud.id
      const Icone = noeud.icone
      const CaretNoeud = estOuvert ? CaretDown : CaretRight

      return (
        <li
          key={noeud.id}
          ref={(element) => {
            enregistrerReference(noeud.id, element)
          }}
          role="treeitem"
          aria-expanded={aDesEnfants ? estOuvert : undefined}
          aria-selected={selectionne !== undefined ? estSelectionne : undefined}
          aria-level={niveau + 1}
          aria-disabled={noeud.desactive === true ? true : undefined}
          tabIndex={idFocusable === noeud.id ? 0 : -1}
          // Les évènements de focus remontent l'arbre du document : sans ce
          // test, focaliser un enfant déclencherait aussi le gestionnaire de
          // chacun de ses parents, et le nœud retenu finirait toujours par
          // être la racine.
          onFocus={(evenement) => {
            if (evenement.target === evenement.currentTarget) {
              setFocusId(noeud.id)
            }
          }}
          onClick={(evenement) => {
            evenement.stopPropagation()
            deplacerFocus(noeud.id)
            selectionnerNoeud(noeud)
          }}
          className="outline-none"
        >
          <div
            className={cn(
              'flex items-center gap-2 rounded-controle py-1.5 pr-3 text-sm',
              'transition-colors duration-[var(--duree-survol)] ease-out',
              estSelectionne ? 'bg-fond-alt font-semibold text-marine' : 'text-texte hover:bg-fond',
              noeud.desactive === true && 'cursor-not-allowed text-texte-attenue',
              porteLeFocus && 'ring-2 ring-sarcelle',
            )}
            style={{ paddingLeft: `${niveau * 1.25 + 0.5}rem` }}
          >
            {aDesEnfants ? (
              // L'équivalent clavier de ce chevron est la flèche droite ou
              // gauche : l'état est déjà porté par « aria-expanded » du nœud,
              // le chevron n'a donc rien à annoncer de plus.
              <span
                aria-hidden
                onClick={(evenement) => {
                  evenement.stopPropagation()
                  deplacerFocus(noeud.id)
                  basculerNoeud(noeud.id)
                }}
                className="shrink-0 cursor-pointer rounded p-0.5 text-texte-secondaire hover:bg-bordure"
              >
                <CaretNoeud size={14} weight="bold" />
              </span>
            ) : (
              <span aria-hidden className="w-[1.4rem] shrink-0" />
            )}

            {Icone && (
              <Icone
                size={18}
                weight="regular"
                aria-hidden
                className={estSelectionne ? 'text-marine' : 'text-sarcelle'}
              />
            )}

            <span className="min-w-0 flex-1 truncate">{noeud.libelle}</span>

            {noeud.badge !== undefined && (
              <span className="shrink-0 text-xs font-medium text-texte-secondaire">
                {noeud.badge}
              </span>
            )}
          </div>

          {aDesEnfants && estOuvert && enfants && (
            <ul role="group">{rendreNiveau(enfants, niveau + 1)}</ul>
          )}
        </li>
      )
    })
  }

  return (
    <ul
      role="tree"
      aria-label={intitule}
      aria-multiselectable={false}
      onKeyDown={auClavier}
      onFocus={() => setArbreFocalise(true)}
      // Un déplacement d'un nœud à l'autre fait sortir le focus du premier
      // avant d'entrer dans le second : sans ce test, l'indicateur de focus
      // clignoterait à chaque flèche.
      onBlur={(evenement) => {
        if (!evenement.currentTarget.contains(evenement.relatedTarget)) {
          setArbreFocalise(false)
        }
      }}
      className={cn('min-w-0 space-y-0.5', className)}
    >
      {rendreNiveau(noeuds, 0)}
    </ul>
  )
}
