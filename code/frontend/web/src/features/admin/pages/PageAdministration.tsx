/*
  Écran /administration : « Comptes et matrice des droits » (charte § 9.2,
  écran 12).

  Deux volets :
  - la matrice des droits, livrée ici : qui accède à quel écran ;
  - les comptes utilisateurs, qui viendront avec l'authentification (CL-1
    `Utilisateur`, `AffectationRole`, `Perimetre`), puisqu'un compte n'a de
    sens qu'une fois la connexion en place.
*/

import { Card } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import { useDroits } from '@/app/droits-context'
import { useRole } from '@/app/role-context'
import { capacitesAdminPourRole } from '@/features/admin/config/capacites'
import { MatriceDroits } from '@/features/admin/pages/MatriceDroits'

export function PageAdministration() {
  const { role } = useRole()
  const { etat, erreur } = useDroits()
  const capacites = capacitesAdminPourRole(role)

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Comptes et matrice des droits"
        description="Accès aux écrans du poste de pilotage, rôle par rôle"
        niveauTitre={2}
      />

      {erreur && (
        <Card titre="Droits indisponibles">
          <p className="text-sm text-danger">{erreur}</p>
        </Card>
      )}

      {etat && <MatriceDroits etat={etat} peutModifier={capacites.peutModifierDroits} />}

      <Card
        titre="Comptes utilisateurs"
        description="Création des comptes, affectation des rôles et des périmètres, révocation"
      >
        <p className="text-sm text-texte-secondaire">
          Ce volet arrive avec l'authentification : un compte suppose une connexion, une affectation
          de rôle datée et un périmètre de chantier ou de magasin. Pour l'instant, le rôle courant
          se choisit dans la barre supérieure, et c'est la matrice ci-dessus qui décide des accès.
        </p>
      </Card>
    </div>
  )
}
