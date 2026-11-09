/*
  Formes servies par l'API pour les comptes et la session, calquées sur CL-1 et
  sur les conventions du MPD (snake_case, énumérés en `UPPER_SNAKE`).

  Le mot de passe ne circule que dans le corps de la requête de connexion, en
  clair sur HTTPS, et n'est jamais renvoyé : le cahier des charges impose des
  mots de passe « hachés » côté serveur.
*/

export type PerimetreDto = {
  id_perimetre: string
  libelle: string
}

export type UtilisateurDto = {
  id_utilisateur: string
  identifiant: string
  nom: string
  prenom: string
  fonction: string
  /** `UPPER_SNAKE` : ACTIF, INACTIF. */
  statut: string
  date_creation: string
  /** Code du rôle affecté (table `role`). */
  role_code_role: string
  perimetre_id_perimetre: string
  /** Libellé du périmètre, joint par le serveur. */
  libelle_perimetre: string
}

export type SessionDto = {
  jeton: string
  utilisateur: UtilisateurDto
}

/** Corps d'erreur renvoyé par `POST /auth/connexion` en cas d'échec. */
export type EchecConnexionDto = {
  /** `IDENTIFIANTS`, `COMPTE_INACTIF` ou `VERROUILLE`. */
  motif: string
  message: string
  secondes_restantes?: number
}
