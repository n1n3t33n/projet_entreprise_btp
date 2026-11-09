/*
  Écran /administration : « Comptes et matrice des droits » (charte § 9.2,
  écran 12).

  Deux onglets :
  - les comptes nominatifs, leur rôle et leur périmètre (EF-AUT-01, EF-AUT-02) ;
  - la matrice des droits : quel rôle accède à quel écran (CL-1
    `Role.accorder/retirer(permission)`).

  La séparation est volontaire : un compte reçoit un RÔLE, et c'est le rôle qui
  porte les droits. Modifier un accès pour tout un métier ne demande donc pas
  de reprendre les comptes un par un.
*/

import { useState } from 'react'
import { ShieldCheck, UsersThree } from '@phosphor-icons/react'
import { Card, Tabs } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import { useDroits } from '@/app/droits-context'
import { useRole } from '@/app/role-context'
import { capacitesAdminPourRole } from '@/features/admin/config/capacites'
import { ComptesUtilisateurs } from '@/features/admin/pages/ComptesUtilisateurs'
import { MatriceDroits } from '@/features/admin/pages/MatriceDroits'

export function PageAdministration() {
  const { role } = useRole()
  const { etat, erreur } = useDroits()
  const capacites = capacitesAdminPourRole(role)
  const [onglet, setOnglet] = useState('comptes')

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Comptes et matrice des droits"
        description="Comptes nominatifs et accès aux écrans du poste de pilotage"
        niveauTitre={2}
      />

      <Tabs
        intitule="Administration"
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'comptes', libelle: 'Comptes utilisateurs', icone: UsersThree },
          { id: 'droits', libelle: 'Matrice des droits', icone: ShieldCheck },
        ]}
      >
        {onglet === 'comptes' && (
          <ComptesUtilisateurs peutModifier={capacites.peutModifierDroits} />
        )}

        {onglet === 'droits' && (
          <>
            {erreur && (
              <Card titre="Droits indisponibles">
                <p className="text-sm text-danger">{erreur}</p>
              </Card>
            )}
            {etat && <MatriceDroits etat={etat} peutModifier={capacites.peutModifierDroits} />}
          </>
        )}
      </Tabs>
    </div>
  )
}
