/*
  Contrats de transport du journal d'audit (MPD-1 table `journal_audit`).

  Convention du projet : `snake_case`, horodatage ISO 8601. MPD-1 donne
  `action`, `type_objet`, `horodatage`, `adresse_ip` et la clé étrangère
  `#utilisateur_id_utilisateur`. Deux champs de lecture sont ajoutés par le
  serveur pour que l'écran soit lisible sans jointure côté client :
  `resume` (phrase décrivant l'action, construite serveur) et l'identité de
  l'auteur (`identifiant_utilisateur`, `nom_utilisateur`). `id_objet` porte
  l'identifiant de l'objet concerné quand il y en a un (un appareil, un compte).
*/

export type EntreeAuditDto = {
  id_entree: string
  /** Verbe d'action en `UPPER_SNAKE` : REVOCATION_APPAREIL, CREATION_COMPTE, … */
  action: string
  /** Type d'objet concerné : appareil, utilisateur, matrice_droits, … */
  type_objet: string
  /** Identifiant de l'objet concerné, ou `null` si l'action n'en vise pas un seul. */
  id_objet: string | null
  /** Phrase décrivant l'action, construite par le serveur. */
  resume: string
  horodatage: string
  adresse_ip: string
  utilisateur_id_utilisateur: string
  identifiant_utilisateur: string
  nom_utilisateur: string
}
