/*
  Types du domaine « Accès et droits », dérivés de CL-1.

  CL-1 modélise trois classes et une classe-association :
  - `Role { codeRole, libelle, systeme, actif }`, avec les opérations
    `accorder(permission)` et `retirer(permission)` ;
  - `Permission { codePermission, module, ressource, action, libelle }` ;
  - `DroitAccorde { portee }`, qui relie un rôle à une permission ;
  - (hors de cette étape) `Utilisateur`, `AffectationRole`, `Perimetre`.

  Décision de modélisation reprise ici (README § 6.5) : « les référentiels
  appelés à vivre — rôles, permissions… — ne sont pas des énumérations du tout :
  ce sont des tables, conformément à la décision "données en base et non du
  code" ». La matrice des accès est donc une DONNÉE, chargée depuis l'API et
  modifiable par l'administrateur, et non une table figée dans le code.

  Littéral de `Action` aligné sur le modèle : MPD-1 (domaine « identité,
  comptes et droits ») contraint `permission.action ∈ {LIRE, CREER, MODIFIER,
  …}` et CL-1 type l'attribut comme une énumération `Action`. L'application lit
  donc `LIRE` (et non plus `CONSULTER`) pour la permission d'accès à un écran.
  `Portee` reste `{GLOBALE, PERIMETRE}` : les littéraux de `droit_accorde.portee`
  ne sont pas figés par le MPD (CHECK générique terminé par « … »), ce sont les
  seuls employés par l'écran et ils devront être confirmés avec le cahier.
*/

import type { IdEcran } from '@/config/navigation'

/**
 * Action portée par une permission (CL-1 `Permission.action : Action`).
 *
 * Littéraux du modèle (MPD-1 CHECK `ck_permission_action`), en forme domaine :
 * `lire` ← `LIRE`, `creer` ← `CREER`, `modifier` ← `MODIFIER`, `valider` est
 * ajouté pour les futures permissions d'action du suivi d'avancement.
 */
export type ActionPermission = 'lire' | 'creer' | 'modifier' | 'valider'

/** Portée d'un droit accordé (CL-1 `DroitAccorde.portee : Portee`). */
export type PorteeDroit = 'globale' | 'perimetre'

/** Rôle applicatif (CL-1 `Role`). */
export type RoleDroit = {
  /** Code référentiel, clé primaire `varchar` (README § 6.5). */
  code: string
  libelle: string
  /** Rôle du système, qui ne peut pas être privé de ses droits essentiels. */
  systeme: boolean
  actif: boolean
}

/**
 * Permission d'accès à un écran du poste de pilotage (CL-1 `Permission`).
 *
 * Pour un écran, le triplet du modèle vaut : `module = 'ecran'`,
 * `ressource = <identifiant de l'écran>`, `action = 'lire'`. La même structure
 * accueillera plus tard les permissions d'action (créer, valider…) sans changer
 * de forme.
 */
export type PermissionEcran = {
  code: string
  idEcran: IdEcran
  action: ActionPermission
  libelle: string
}

/** Droit accordé à un rôle sur une permission (CL-1 `DroitAccorde`). */
export type DroitAccorde = {
  codeRole: string
  codePermission: string
  portee: PorteeDroit
}

/** État complet des droits, tel que chargé puis enregistré par l'écran. */
export type EtatDroits = {
  roles: RoleDroit[]
  permissions: PermissionEcran[]
  accordes: DroitAccorde[]
}
