/*
  Arborescence magasins et familles d'articles.

  Affiche l'arbre chantier → magasin → familles servi par l'API, à l'aide du
  composant `Tree`. Vue de consultation : aucune action d'écriture, quel que
  soit le rôle.
*/

import { Buildings, type Icon, Package, Stack } from '@phosphor-icons/react'
import { Card, type NoeudArbre, Tree } from '@/components/ui'
import { listerArborescenceStock } from '@/features/stock/api'
import { useRequete } from '@/lib/hooks/useRequete'
import type { NoeudStock } from '@/features/stock/types'

const ICONE_PAR_TYPE: Record<NoeudStock['type'], Icon> = {
  chantier: Buildings,
  magasin: Package,
  famille: Stack,
}

function versNoeudArbre(noeud: NoeudStock): NoeudArbre {
  return {
    id: noeud.id,
    libelle: noeud.libelle,
    icone: ICONE_PAR_TYPE[noeud.type],
    badge: noeud.nombreArticles !== undefined ? noeud.nombreArticles : undefined,
    enfants: noeud.enfants.length > 0 ? noeud.enfants.map(versNoeudArbre) : undefined,
  }
}

export function ArborescenceMagasins() {
  const etat = useRequete(listerArborescenceStock, [])

  if (etat.statut === 'erreur') {
    return (
      <Card>
        <p className="text-sm text-danger">{etat.erreur}</p>
      </Card>
    )
  }

  const noeuds = (etat.donnees ?? []).map(versNoeudArbre)
  const ouvertsInitiaux = noeuds.flatMap((racine) => [
    racine.id,
    ...(racine.enfants ?? []).map((enfant) => enfant.id),
  ])

  return (
    <Card
      titre="Magasins et familles"
      description="Organisation du stock du chantier : magasin pilote et familles d'articles."
    >
      {etat.statut === 'chargement' && !etat.donnees ? (
        <div className="h-48 animate-pulse rounded-controle bg-fond-alt" />
      ) : (
        <Tree intitule="Magasins et familles d'articles" noeuds={noeuds} ouvertsInitiaux={ouvertsInitiaux} />
      )}
    </Card>
  )
}
