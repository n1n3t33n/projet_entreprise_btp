/*
  Écran /referentiels du poste de pilotage : point d'entrée du module.

  Orchestre les trois référentiels du cœur structurant via des onglets :
  - le catalogue d'articles (EF-REF-03) ;
  - les magasins (EF-REF-02) ;
  - les chantiers, zones et logements (EF-REF-01).

  Il applique le filtrage par rôle via les capacités et transmet le droit
  d'édition aux écrans ; ceux-ci chargent leurs propres données. Les référentiels
  restants (gammes et corps d'état, unités et conditionnements en édition,
  paramétrage et règles) relèvent d'une étape ultérieure.
*/

import { useState } from 'react'
import { Buildings, Package, Warehouse } from '@phosphor-icons/react'
import { Card, Tabs } from '@/components/ui'
import { useCapacitesReferentiels } from '@/features/referentiels/hooks/useCapacitesReferentiels'
import { CatalogueArticles } from '@/features/referentiels/pages/CatalogueArticles'
import { ChantiersZones } from '@/features/referentiels/pages/ChantiersZones'
import { MagasinsReferentiel } from '@/features/referentiels/pages/MagasinsReferentiel'

export function PageReferentiels() {
  const capacites = useCapacitesReferentiels()
  const [onglet, setOnglet] = useState('catalogue')

  if (!capacites.peutConsulter) {
    return (
      <Card titre="Accès non autorisé">
        <p className="text-sm text-texte-secondaire">
          Ce rôle n'a pas accès aux référentiels du poste de pilotage.
        </p>
      </Card>
    )
  }

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <Tabs
        intitule="Référentiels"
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'catalogue', libelle: 'Catalogue', icone: Package },
          { id: 'magasins', libelle: 'Magasins', icone: Warehouse },
          { id: 'chantiers', libelle: 'Chantiers & zones', icone: Buildings },
        ]}
      >
        {onglet === 'catalogue' && <CatalogueArticles peutEditer={capacites.peutEditer} />}
        {onglet === 'magasins' && <MagasinsReferentiel peutEditer={capacites.peutEditer} />}
        {onglet === 'chantiers' && <ChantiersZones peutEditer={capacites.peutEditer} />}
      </Tabs>
    </div>
  )
}
