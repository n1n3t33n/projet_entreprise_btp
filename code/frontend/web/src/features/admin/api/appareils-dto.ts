/*
  Contrats de transport du domaine « appareils », tels que le serveur les
  expose. Convention du projet : `snake_case`, énumérations en `UPPER_SNAKE`,
  horodatages ISO 8601. Rien de ce fichier ne sort du dossier `api`.

  Calqué sur MPD-1 table `appareil` : `empreinte_materiel`, `plateforme`,
  `version_application`, `derniere_synchronisation`, `statut` et la clé
  étrangère `#utilisateur_id_utilisateur`. Le serveur joint le compte
  propriétaire (identifiant et nom) pour que la supervision soit lisible sans
  appel supplémentaire, comme le journal d'exécution joint déjà son contexte.
*/

/** `UPPER_SNAKE`, littéral du modèle (MPD-1 `ck_appareil_statut`) : ACTIF, REVOQUE, INACTIF. */
export type StatutAppareilDb = 'ACTIF' | 'REVOQUE' | 'INACTIF'

export type AppareilDto = {
  id_appareil: string
  empreinte_materiel: string
  plateforme: string
  version_application: string
  /** ISO 8601, ou `null` si l'appareil n'a jamais synchronisé. */
  derniere_synchronisation: string | null
  statut: StatutAppareilDb
  utilisateur_id_utilisateur: string
  /** Jointure de lecture : identifiant de connexion du propriétaire. */
  identifiant_utilisateur: string
  /** Jointure de lecture : nom complet du propriétaire. */
  nom_utilisateur: string
}
