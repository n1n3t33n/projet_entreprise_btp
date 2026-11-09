/*
  Types de domaine du module gammes, en `camelCase`, indépendants du transport.
  Les écrans ne connaissent que ceux-ci.

  Source : CL-3b (Gamme, EtapeModele, CorpsEtat) et MPD-3.
*/

import type { StatutGamme } from '@/features/gammes/types/enums'

export type { StatutGamme } from '@/features/gammes/types/enums'

/** Corps d'état : métier auquel se rattache une étape (CL-3b `CorpsEtat`). */
export type CorpsEtat = {
  code: string
  libelle: string
  ordre: number
  couleur: string
}

/**
 * Version de gamme opératoire (CL-3b `Gamme`), rattachée à un type de logement.
 * `poidsTotal` et `nombreEtapes` sont calculés par le serveur à partir des
 * étapes-modèles composées.
 */
export type Gamme = {
  id: string
  version: number
  libelle: string
  statut: StatutGamme
  dateActivation: string | null
  codeTypeLogement: string
  libelleTypeLogement: string
  nombreEtapes: number
  poidsTotal: number
}

/** Étape-modèle composant une gamme (CL-3b `EtapeModele`). */
export type EtapeModele = {
  id: string
  code: string
  libelle: string
  ordre: number
  poids: number
  controleRequis: boolean
  codeCorpsEtat: string
  libelleCorpsEtat: string
  couleurCorpsEtat: string
  idGamme: string
}

/** Détail d'une gamme : ses attributs et ses étapes triées. */
export type GammeDetail = {
  gamme: Gamme
  etapes: EtapeModele[]
}

/** Saisie de création ou de modification d'un corps d'état. */
export type SaisieCorpsEtat = {
  code: string
  libelle: string
  ordre: number
  couleur: string
}

/** Saisie d'une étape-modèle dans l'éditeur d'une gamme brouillon. */
export type SaisieEtapeModele = {
  id: string
  code: string
  libelle: string
  ordre: number
  poids: number
  controleRequis: boolean
  codeCorpsEtat: string
}
