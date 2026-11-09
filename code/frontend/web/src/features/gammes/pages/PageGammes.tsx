/*
  Écran /gammes du poste de pilotage : gammes opératoires et corps d'état.

  Couvre EF-REF-05 (corps d'état et gammes) et EF-REF-09 (publication d'une
  version). Deux onglets : les corps d'état, référentiel transversal, et les
  gammes, qui s'y réfèrent. L'accès à l'écran est décidé par la matrice des
  droits (responsable technique) ; l'édition par les capacités.
*/

import { useState } from 'react'
import { HardHat, Stack } from '@phosphor-icons/react'
import { Card, Tabs } from '@/components/ui'
import { CorpsEtatReferentiel } from '@/features/gammes/pages/CorpsEtatReferentiel'
import { GammesReferentiel } from '@/features/gammes/pages/GammesReferentiel'
import { useCapacitesGammes } from '@/features/gammes/hooks/useCapacitesGammes'

export function PageGammes() {
  const capacites = useCapacitesGammes()
  const [onglet, setOnglet] = useState('gammes')

  if (!capacites.peutConsulter) {
    return (
      <Card titre="Accès non autorisé">
        <p className="text-sm text-texte-secondaire">
          Ce rôle n'a pas accès aux gammes opératoires du poste de pilotage.
        </p>
      </Card>
    )
  }

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <Tabs
        intitule="Gammes et corps d'état"
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'gammes', libelle: 'Gammes opératoires', icone: Stack },
          { id: 'corps', libelle: "Corps d'état", icone: HardHat },
        ]}
      >
        {onglet === 'gammes' && <GammesReferentiel peutEditer={capacites.peutEditer} />}
        {onglet === 'corps' && <CorpsEtatReferentiel peutEditer={capacites.peutEditer} />}
      </Tabs>
    </div>
  )
}
