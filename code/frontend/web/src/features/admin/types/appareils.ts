/*
  Types du domaine « appareils enrôlés », dérivés de CL-1 (`Appareil`) et de
  MPD-1 (table `appareil`).

  CL-1 donne la classe `Appareil { idAppareil, empreinteMateriel, plateforme,
  versionApplication, derniereSynchronisation, statut }` avec les opérations
  `enregistrer()`, `revoquer()` et `verrouExpire()`. MPD-1 ajoute la clé
  étrangère `#utilisateur_id_utilisateur` (un appareil appartient à un compte,
  Utilisateur 1 → enrôle → 0..* Appareil) et contraint le statut par
  `CHECK ck_appareil_statut : statut ∈ {ACTIF, INACTIF, OUVERT, …}`.

  Littéraux retenus pour `StatutAppareil` : `actif` (← ACTIF, appareil enrôlé
  et en service, état « Session verrouillée/déverrouillée » d'ET-4), `revoque`
  (← RÉVOQUÉ, état « Appareil révoqué » d'ET-4, atteint par révocation de
  l'administrateur ou désactivation du compte) et `inactif` (← INACTIF). Le
  littéral RÉVOQUÉ n'est pas écrit dans la liste du CHECK (terminée par « … ») :
  il est DÉDUIT de l'état « Appareil révoqué » d'ET-4 et de l'opération
  `Appareil.revoquer()` de CL-1 — à confirmer avec le cahier comme les autres
  littéraux de statut.

  La « fraîcheur » de synchronisation (RG-Y7) n'est pas un attribut du modèle :
  c'est une lecture calculée de `derniereSynchronisation` au regard de l'heure
  de référence, utilisée par la supervision et par le tableau de bord
  (EF-DSH-04). Elle vit donc dans la présentation, pas dans ce type.
*/

/** Statut d'un appareil enrôlé (CL-1 `Appareil.statut`, MPD-1 `ck_appareil_statut`). */
export type StatutAppareil = 'actif' | 'revoque' | 'inactif'

/** Appareil enrôlé (CL-1 `Appareil`), enrichi du compte auquel il appartient. */
export type Appareil = {
  id: string
  /** Empreinte matérielle du terminal (MPD-1 `empreinte_materiel`). */
  empreinteMateriel: string
  /** Plateforme déclarée à l'enrôlement, par exemple « Android 14 ». */
  plateforme: string
  /** Version de l'application mobile installée. */
  versionApplication: string
  /** Dernière synchronisation réussie, ou `null` si l'appareil n'a jamais synchronisé. */
  derniereSynchronisation: string | null
  statut: StatutAppareil
  /** Compte propriétaire (MPD-1 `#utilisateur_id_utilisateur`). */
  idUtilisateur: string
  /** Identifiant de connexion du propriétaire, pour l'affichage. */
  identifiantUtilisateur: string
  /** Nom complet du propriétaire, pour l'affichage. */
  nomUtilisateur: string
}
