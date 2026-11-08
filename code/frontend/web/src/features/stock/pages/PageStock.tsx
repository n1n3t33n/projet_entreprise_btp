/*
  Écran /stock du poste de pilotage : point d'entrée du module.

  Orchestre les cinq écrans de l'étape :
  - la liste des articles du magasin (onglet « Articles ») ;
  - la fiche article en tiroir ;
  - les formulaires d'entrée et de sortie, en modale ;
  - l'arborescence magasins / familles (onglet « Magasins & familles »).

  Il porte l'état partagé entre ces écrans — le magasin courant, les données
  chargées, le filtre, la fiche ouverte, les modales — et applique le filtrage
  par rôle via les capacités. Les composants enfants reçoivent données et
  rappels par propriétés : ils ne chargent rien eux-mêmes, hormis l'historique
  et l'arborescence, qui ont leur propre cycle.
*/

import { useState } from 'react'
import { Package, TreeStructure } from '@phosphor-icons/react'
import { Card, Tabs } from '@/components/ui'
import { listerMagasins, listerStockMagasin, listerTypesMouvement } from '@/features/stock/api'
import { estLectureSeule } from '@/features/stock/config/capacites'
import { useCapacitesStock } from '@/features/stock/hooks/useCapacitesStock'
import { useRequete } from '@/features/stock/hooks/useRequete'
import { ArborescenceMagasins } from '@/features/stock/pages/ArborescenceMagasins'
import { FicheArticleTiroir } from '@/features/stock/pages/FicheArticleTiroir'
import { FormulaireEntree } from '@/features/stock/pages/FormulaireEntree'
import { FormulaireSortie } from '@/features/stock/pages/FormulaireSortie'
import { ListeArticlesStock } from '@/features/stock/pages/ListeArticlesStock'
import type { FiltreStock, LigneStock } from '@/features/stock/types'

const FILTRE_INITIAL: FiltreStock = { recherche: '', niveau: 'tous', codeFamille: 'toutes' }

export function PageStock() {
  const capacites = useCapacitesStock()

  const [onglet, setOnglet] = useState('articles')
  const [filtre, setFiltre] = useState<FiltreStock>(FILTRE_INITIAL)
  const [ligneFiche, setLigneFiche] = useState<LigneStock | null>(null)
  const [modaleEntree, setModaleEntree] = useState(false)
  const [modaleSortie, setModaleSortie] = useState(false)

  const magasinsEtat = useRequete(listerMagasins, [])
  const magasin = magasinsEtat.donnees?.[0] ?? null
  const idMagasin = magasin?.idMagasin ?? ''

  const stockEtat = useRequete(
    () => (idMagasin ? listerStockMagasin(idMagasin) : Promise.resolve<LigneStock[]>([])),
    [idMagasin],
  )
  const typesEtat = useRequete(listerTypesMouvement, [])

  const lignes = stockEtat.donnees ?? []
  const types = typesEtat.donnees ?? []
  const typesEntree = types.filter((type) => type.sens === 'entree')
  const typesSortie = types.filter((type) => type.sens === 'sortie')
  const chargement =
    magasinsEtat.statut === 'chargement' || stockEtat.statut === 'chargement' || magasin === null

  if (!capacites.peutConsulter) {
    return (
      <Card titre="Accès non autorisé">
        <p className="text-sm text-texte-secondaire">
          Ce rôle n'a pas accès au stock du poste de pilotage.
        </p>
      </Card>
    )
  }

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <Tabs
        intitule="Vues du stock"
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'articles', libelle: 'Articles', icone: Package },
          { id: 'arborescence', libelle: 'Magasins & familles', icone: TreeStructure },
        ]}
      >
        {onglet === 'articles' ? (
          stockEtat.statut === 'erreur' ? (
            <Card>
              <p className="text-sm text-danger">{stockEtat.erreur}</p>
            </Card>
          ) : (
            <ListeArticlesStock
              lignes={lignes}
              chargement={chargement}
              magasinLibelle={magasin?.libelle ?? '…'}
              chantierLibelle={magasin?.libelleChantier ?? ''}
              filtre={filtre}
              onFiltre={setFiltre}
              lectureSeule={estLectureSeule(capacites)}
              peutSaisir={capacites.peutSaisir}
              onNouvelleEntree={() => setModaleEntree(true)}
              onNouvelleSortie={() => setModaleSortie(true)}
              onVoirFiche={setLigneFiche}
            />
          )
        ) : (
          <ArborescenceMagasins />
        )}
      </Tabs>

      <FicheArticleTiroir
        ligne={ligneFiche}
        idMagasin={idMagasin}
        capacites={capacites}
        onFermer={() => setLigneFiche(null)}
        onMiseAJour={() => stockEtat.recharger()}
      />

      {capacites.peutSaisir && (
        <>
          <FormulaireEntree
            ouvert={modaleEntree}
            onFermer={() => setModaleEntree(false)}
            idMagasin={idMagasin}
            articles={lignes}
            typesEntree={typesEntree}
            onEnregistre={() => stockEtat.recharger()}
          />
          <FormulaireSortie
            ouvert={modaleSortie}
            onFermer={() => setModaleSortie(false)}
            idMagasin={idMagasin}
            articles={lignes}
            typesSortie={typesSortie}
            onEnregistre={() => stockEtat.recharger()}
          />
        </>
      )}
    </div>
  )
}
