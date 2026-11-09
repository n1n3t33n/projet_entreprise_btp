/*
  Écran /administration : comptes, droits, appareils, journal d'audit et import
  (charte § 9.2 ; écrans 12, 13 et 14 regroupés sous l'acteur Administrateur).

  Onglets, tous rattachés à l'administrateur fonctionnel par UC-4 :
  - Comptes utilisateurs — comptes nominatifs, rôle et périmètre (EF-AUT-01/02) ;
  - Matrice des droits — quel rôle accède à quel écran (CL-1
    `Role.accorder/retirer(permission)`) ;
  - Appareils — supervision et révocation (EF-ADM-03, EF-AUT-06) ;
  - Journal d'audit — actions d'administration, lecture seule (EF-AUT-08) ;
  - Import CSV — données initiales des référentiels (EF-ADM-02).

  Regrouper ces écrans sous un seul point de menu suit UC-4, qui place toutes
  ces actions sous le même acteur. L'ACCÈS à l'écran reste décidé par la matrice
  des droits ; les capacités d'écriture (modifier les droits, révoquer, importer)
  sont réservées au rôle système (`capacites`).
*/

import { useState } from 'react'
import {
  DeviceMobile,
  FileArrowUp,
  ListMagnifyingGlass,
  ShieldCheck,
  UsersThree,
} from '@phosphor-icons/react'
import { Card, Tabs } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import { useDroits } from '@/app/droits-context'
import { useRole } from '@/app/role-context'
import { capacitesAdminPourRole } from '@/features/admin/config/capacites'
import { ComptesUtilisateurs } from '@/features/admin/pages/ComptesUtilisateurs'
import { MatriceDroits } from '@/features/admin/pages/MatriceDroits'
import { SupervisionAppareils } from '@/features/admin/pages/SupervisionAppareils'
import { JournalAudit } from '@/features/admin/pages/JournalAudit'
import { ImportReferentiels } from '@/features/admin/pages/ImportReferentiels'

export function PageAdministration() {
  const { role } = useRole()
  const { etat, erreur } = useDroits()
  const capacites = capacitesAdminPourRole(role)
  const [onglet, setOnglet] = useState('comptes')

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Administration"
        description="Comptes, droits, appareils, journal d'audit et import des référentiels"
        niveauTitre={2}
      />

      <Tabs
        intitule="Administration"
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'comptes', libelle: 'Comptes utilisateurs', icone: UsersThree },
          { id: 'droits', libelle: 'Matrice des droits', icone: ShieldCheck },
          { id: 'appareils', libelle: 'Appareils', icone: DeviceMobile },
          { id: 'audit', libelle: "Journal d'audit", icone: ListMagnifyingGlass },
          { id: 'import', libelle: 'Import CSV', icone: FileArrowUp },
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

        {onglet === 'appareils' && (
          <SupervisionAppareils peutModifier={capacites.peutRevoquerAppareil} />
        )}

        {onglet === 'audit' && <JournalAudit />}

        {onglet === 'import' && <ImportReferentiels peutImporter={capacites.peutImporter} />}
      </Tabs>
    </div>
  )
}
