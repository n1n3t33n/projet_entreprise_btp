/*
  Modèles de vue et charges utiles d'écriture du module avancement.

  Formes consommées par les écrans : une ligne de logement avec ses
  pourcentages, une ligne d'étape enrichie pour le tableau et la validation, et
  la synthèse chantier des indicateurs. Dépendent du domaine, jamais l'inverse.
*/

import type { StatutEtape, StatutLogement } from '@/features/avancement/types/enums'
import type { DecisionControle } from '@/features/avancement/types/enums'

/** Ligne du tableau de suivi : un logement et son avancement. */
export type LigneLogement = {
  idLogement: string
  numero: string
  libelleZone: string
  libelleType: string
  statut: StatutLogement
  pourcentageDeclare: number
  pourcentageValide: number
  nombreEtapes: number
  nombreValidees: number
  nombreBloquees: number
  nombreEnRetard: number
}

/** Ligne d'étape enrichie, pour le détail d'un logement et la file de validation. */
export type LigneEtape = {
  idEtape: string
  idLogement: string
  numeroLogement: string
  libelleEtape: string
  codeCorpsEtat: string
  libelleCorpsEtat: string
  couleurCorpsEtat: string
  ordre: number
  statut: StatutEtape
  datePrevue: string | null
  dateFinDeclaree: string | null
  dateValidation: string | null
  poidsEffectif: number
  controleRequis: boolean
  /** Vrai si la date prévue est dépassée et l'étape non terminée (EF-AVA-09). */
  enRetard: boolean
  idAuteurDeclaration: string | null
  nomAuteurDeclaration: string | null
}

/** Synthèse d'avancement du chantier, pour les indicateurs de l'en-tête. */
export type SyntheseAvancement = {
  pourcentageDeclare: number
  pourcentageValide: number
  nombreLogements: number
  nombreEtapesAValider: number
  nombreEtapesBloquees: number
  nombreEtapesEnRetard: number
}

/** Décision de validation d'une étape à contrôle (EF-AVA-06). */
export type DecisionValidationEtape = {
  idEtape: string
  decision: DecisionControle
  /** Obligatoire pour un rejet. */
  motif: string | null
}

/** Déclaration de blocage d'une étape (EF-AVA-05). */
export type DeclarationBlocage = {
  idEtape: string
  codeMotif: string
  commentaire: string | null
}

/** Critères de filtrage du suivi par logement. */
export type FiltreAvancement = {
  recherche: string
  idZone: string | 'toutes'
}
