/*
  Types du domaine « journal d'audit des actions d'administration » (EF-AUT-08),
  dérivés de CL-1 `JournalAudit` et de MPD-1 table `journal_audit`.

  CL-1 : `JournalAudit { idEntree, action, typeObjet, horodatage, adresseIp }`
  avec l'opération `consigner(acteur, action)` ; Utilisateur 1 → tracé par →
  0..* JournalAudit. Le journal est immuable (MPD-1 `trg_journal_audit_immuable`,
  RG-S8) : le domaine ne porte donc ni modification ni suppression, seulement la
  lecture.

  Distinction importante : ce journal trace l'ADMINISTRATION (comptes, droits,
  appareils), là où le journal d'exécution (module pilotage, CL-5
  `EvenementExecution`) trace les changements de statut des étapes. Les deux
  sont séparés par construction, comme UC-4 (« Consulter le journal d'audit »,
  EF-AUT-08) et UC-5 (« Consulter le journal d'exécution », EF-DSH-03) les
  séparent.
*/

/** Entrée du journal d'audit (CL-1 `JournalAudit`). */
export type EntreeAudit = {
  id: string
  /** Verbe d'action (forme domaine, ex. `revocation_appareil`). */
  action: string
  /** Type d'objet concerné (appareil, utilisateur, matrice_droits…). */
  typeObjet: string
  /** Identifiant de l'objet concerné, ou `null`. */
  idObjet: string | null
  /** Phrase lisible décrivant l'action. */
  resume: string
  horodatage: string
  adresseIp: string
  idAuteur: string
  identifiantAuteur: string
  nomAuteur: string
}

/** Filtres de lecture du journal d'audit, transmis au serveur en paramètres. */
export type FiltresAudit = {
  /** Type d'action, ou `null` pour toutes. */
  action: string | null
  /** Identifiant d'un auteur, ou `null` pour tous. */
  idAuteur: string | null
}

export const FILTRES_AUDIT_VIDES: FiltresAudit = {
  action: null,
  idAuteur: null,
}
