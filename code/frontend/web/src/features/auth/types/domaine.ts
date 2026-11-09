/*
  Types du domaine « Accès et droits » côté comptes et session, dérivés de CL-1.

  CL-1 fournit :
  - `Utilisateur { idUtilisateur, identifiant, nom, prenom, fonction, statut,
    dateCreation }`, avec `seConnecter(pin)`, `aLeDroit(action)`, `desactiver()` ;
  - `AffectationRole { idAffectation, dateDebut, dateFin }`, avec `estActive()`
    et `revoquer()`, qui relie un utilisateur à un rôle ;
  - `Perimetre { idPerimetre, libelle }`, avec `couvre(chantier)` et
    `couvre(magasin)`.

  EXIGENCES COUVERTES : EF-AUT-01 (comptes nominatifs), EF-AUT-02 (rôle limité
  à un périmètre), EF-AUT-04 (connexion web par identifiant et mot de passe,
  verrouillage temporaire après échecs répétés).

  SIGNALÉ : EF-AUT-04 figure parmi les quatorze exigences que le README de
  modélisation (§ 2.1) recense comme couvertes par AUCUN cas d'utilisation, et
  le diagramme UC-4 n'est pas dans les fichiers fournis. Cet écran s'appuie
  donc sur le seul texte du cahier des charges.

  SIGNALÉ : aucune durée d'expiration n'est fixée pour une session WEB. Le
  verrou de 14 jours (AC-1, ET-4 ; H17 à 7 jours est périmé) vise la session
  LOCALE du mobile hors-ligne. La session web vit donc le temps de l'onglet,
  en attendant une règle explicite.
*/

import type { Role } from '@/app/role-context'

/** Statut d'un compte (CL-1 `Utilisateur.statut : Statut`). */
export type StatutCompte = 'actif' | 'inactif'

/** Périmètre d'exercice d'un rôle (CL-1 `Perimetre`). */
export type Perimetre = {
  id: string
  libelle: string
}

/** Compte nominatif (CL-1 `Utilisateur`), avec son affectation de rôle active. */
export type Utilisateur = {
  id: string
  /** Identifiant de connexion, unique. */
  identifiant: string
  nom: string
  prenom: string
  fonction: string
  statut: StatutCompte
  /** Date de création, calendaire. */
  dateCreation: string
  /** Rôle actuellement affecté (CL-1 `AffectationRole` active). */
  role: Role
  /** Périmètre de cette affectation (EF-AUT-02). */
  idPerimetre: string
  libellePerimetre: string
}

/** Session ouverte sur le poste de pilotage. */
export type Session = {
  utilisateur: Utilisateur
  /** Jeton opaque fourni par le serveur ; jamais interprété par le client. */
  jeton: string
}

/** Saisie de l'écran de connexion (EF-AUT-04 : identifiant + mot de passe). */
export type IdentifiantsConnexion = {
  identifiant: string
  motDePasse: string
}

/**
 * Échec de connexion, tel que le serveur le qualifie.
 *
 * `verrouille` correspond au verrouillage temporaire après échecs répétés
 * exigé par EF-AUT-04 ; `secondesRestantes` indique l'attente.
 */
export type EchecConnexion = {
  motif: 'identifiants' | 'compte_inactif' | 'verrouille'
  message: string
  secondesRestantes?: number
}

/** Création ou modification d'un compte (EF-AUT-01, EF-AUT-02). */
export type SaisieCompte = {
  identifiant: string
  nom: string
  prenom: string
  fonction: string
  role: Role
  idPerimetre: string
  statut: StatutCompte
}
