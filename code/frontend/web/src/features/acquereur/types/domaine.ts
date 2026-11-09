/*
  Types du domaine « espace acquéreur » (UC-5, EF-ACQ-01/02). Phase 2, LECTURE
  SEULE.

  L'acquéreur consulte l'avancement de SON logement (EF-ACQ-01) et la liste des
  étapes franchies qui lui ont été notifiées (EF-ACQ-02). Le périmètre est porté
  par le compte (EF-AUT-02 : le compte acquéreur du jeu d'essai a pour périmètre
  « Logement A01 ») : l'espace ne propose aucun sélecteur de logement et
  n'expose rien d'autre que ce logement. Aucune action n'écrit : le rôle
  acquéreur consulte sans jamais saisir (c'est le sens du mode lecture seule des
  champs, cf. `FormField`).

  La vue est volontairement SIMPLIFIÉE par rapport au pilotage : UC-5 parle d'un
  « avancement simplifié d'un logement ». On n'affiche ni la charge de contrôle,
  ni les motifs de blocage internes, ni le détail d'exécution — seulement
  l'avancement global et l'état lisible de chaque étape.
*/

import type { StatutEtape } from '@/features/avancement/types/enums'

/** Étape du logement, vue simplifiée pour l'acquéreur. */
export type EtapeAcquereur = {
  idEtape: string
  libelleEtape: string
  libelleCorpsEtat: string
  couleurCorpsEtat: string
  statut: StatutEtape
  /** Date de franchissement (validation), si l'étape est franchie. */
  dateFranchissement: string | null
}

/** Avancement du logement de l'acquéreur (EF-ACQ-01). */
export type AvancementLogement = {
  numeroLogement: string
  libelleZone: string
  libelleTypeLogement: string
  /** Pourcentage validé (part réellement franchie). */
  pourcentageValide: number
  /** Pourcentage déclaré (annoncé par le terrain, pas encore tout validé). */
  pourcentageDeclare: number
  dateLivraisonPrevue: string | null
  etapes: EtapeAcquereur[]
}

/** Notification d'étape franchie adressée à l'acquéreur (EF-ACQ-02). */
export type NotificationAcquereur = {
  id: string
  libelleEtape: string
  dateFranchissement: string
  lue: boolean
}
