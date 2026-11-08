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

  INFORMATION MANQUANTE SIGNALÉE : les dossiers de modélisation fournis ne
  contiennent pas de MPD du domaine « accès et droits » (seuls MPD-2 à MPD-5
  sont présents ; le README cite un `MPD_postgresql.drawio` d'ensemble absent
  des fichiers). Les littéraux de `Action` et de `Portee` ne sont donc fondés
  sur aucune source : les valeurs ci-dessous sont les seules employées par
  l'écran, et devront être confrontées au MPD complet.
*/

import type { IdEcran } from '@/config/navigation'

/** Action portée par une permission (CL-1 `Permission.action : Action`). */
export type ActionPermission = 'consulter' | 'creer' | 'modifier' | 'valider'

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
 * `ressource = <identifiant de l'écran>`, `action = 'consulter'`. La même
 * structure accueillera plus tard les permissions d'action (créer, valider…)
 * sans changer de forme.
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
