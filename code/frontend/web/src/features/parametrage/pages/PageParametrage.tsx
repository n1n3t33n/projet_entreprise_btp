/*
  Écran /parametrage du poste de pilotage : paramétrage du chantier et règles
  de validation.

  Couvre EF-REF-07 (paramètres) et EF-REF-08 (règles de validation). Deux
  onglets. Ltr('accès à l')écran est décidé par la matrice des droits (administrateur
  et responsable technique) ; l'édition par les capacités.
*/

import { useState } from 'react'
import { ShieldCheck, SlidersHorizontal } from '@phosphor-icons/react'
import { Card, Tabs } from '@/components/ui'
import { ParametresChantier } from '@/features/parametrage/pages/ParametresChantier'
import { ReglesValidation } from '@/features/parametrage/pages/ReglesValidation'
import { useCapacitesParametrage } from '@/features/parametrage/hooks/useCapacitesParametrage'
import { tr } from '@/i18n/tr'

export function PageParametrage() {
  const capacites = useCapacitesParametrage()
  const [onglet, setOnglet] = useState('parametres')

  if (!capacites.peutConsulter) {
    return (
      <Card titre={tr('Accès non autorisé')}>
        <p className="text-sm text-texte-secondaire">
          {tr("Ce rôle n'a pas accès au paramétrage du poste de pilotage.")}
        </p>
      </Card>
    )
  }

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <Tabs
        intitule={tr('Paramétrage du chantier')}
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'parametres', libelle: tr('Paramètres'), icone: SlidersHorizontal },
          { id: 'regles', libelle: tr('Règles de validation'), icone: ShieldCheck },
        ]}
      >
        {onglet === 'parametres' && <ParametresChantier peutEditer={capacites.peutEditer} />}
        {onglet === 'regles' && <ReglesValidation peutEditer={capacites.peutEditer} />}
      </Tabs>
    </div>
  )
}
