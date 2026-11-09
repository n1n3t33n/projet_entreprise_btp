/*
  Types de domaine du module pilotage, en `camelCase`, indépendants du
  transport. Les pages ne connaissent que ceux-ci.

  Source : CL-5 (avancement et notifications) pour l'avancement agrégé et
  l'événement d'exécution ; RG-A5, RG-A6, RG-A8 pour les règles de calcul et
  d'alerte ; RG-S5 et MPD-4 pour la vue stock.
*/

import type { StatutValidationMouvement } from '@/features/stock/types'
import type { StatutEtape } from '@/features/avancement/types'
import type { NiveauSeuil } from '@/lib/seuils'

export type { StatutEtape } from '@/features/avancement/types'

/** Niveau de regroupement d'un agrégat (CL-5 `Portee`). */
export type PorteeAgregat = 'chantier' | 'zone' | 'logement' | 'corpsEtat'

/**
 * Avancement agrégé (CL-5 `AvancementAgrege`).
 *
 * RG-A6 : pourcentage = somme des poids des étapes terminées / somme des
 * poids, calculé par corps d'état, logement, zone et chantier, et affiché en
 * deux versions : déclaré et validé. L'écart entre les deux est la charge de
 * contrôle restante ; il se lit avec `ecartDeclareValide`.
 */
export type AvancementAgrege = {
  portee: PorteeAgregat
  idCible: string
  libelleCible: string
  libelleSecondaire: string | null
  couleur: string | null
  pourcentageDeclare: number
  pourcentageValide: number
  nombreEtapes: number
  nombreValidees: number
  nombreBloquees: number
  nombreEnRetard: number
  dateCalcul: string
}

/** Écart entre déclaré et validé (CL-5 `ecartDeclareValide()`). */
export function ecartDeclareValide(agregat: AvancementAgrege): number {
  return agregat.pourcentageDeclare - agregat.pourcentageValide
}

/**
 * Étape à signaler au pilotage (RG-A8) : date prévue dépassée sans être
 * terminée, ou étape bloquée remontée au chef de chantier.
 */
export type AlerteEtape = {
  idEtape: string
  idLogement: string
  numeroLogement: string
  libelleZone: string
  libelleEtape: string
  libelleCorpsEtat: string
  couleurCorpsEtat: string
  statut: StatutEtape
  datePrevue: string | null
  joursDeRetard: number
  codeMotifBlocage: string | null
  libelleMotifBlocage: string | null
  commentaire: string | null
}

/**
 * Ligne du journal d'exécution (EF-DSH-03, CL-5 `EvenementExecution`).
 *
 * RG-A5 : chaque changement de statut est un événement immuable portant qui,
 * quand (appareil et serveur), pour le compte de qui, statut avant et après,
 * motif. Rien n'est modifié ni supprimé : une erreur se corrige par un nouvel
 * événement. Le journal est donc une lecture seule, par construction.
 */
export type EvenementJournal = {
  uuid: string
  idEtape: string
  libelleEtape: string
  idLogement: string
  numeroLogement: string
  libelleZone: string
  codeCorpsEtat: string
  libelleCorpsEtat: string
  statutAvant: StatutEtape | null
  statutApres: StatutEtape
  horodatageAppareil: string
  horodatageServeur: string
  idAuteur: string
  nomAuteur: string
  estDelegation: boolean
  codeMotifBlocage: string | null
  libelleMotifBlocage: string | null
  commentaire: string | null
}

/** Filtres du journal, transmis au serveur en paramètres de requête. */
export type FiltresJournal = {
  idAuteur: string | null
  idZone: string | null
  statutApres: StatutEtape | null
  /** Date au format `AAAA-MM-JJ` incluse, ou `null` pour ne pas borner. */
  depuis: string | null
  jusqua: string | null
}

export const FILTRES_JOURNAL_VIDES: FiltresJournal = {
  idAuteur: null,
  idZone: null,
  statutApres: null,
  depuis: null,
  jusqua: null,
}

/** Synthèse du stock pour le tableau de bord (EF-DSH-04). */
export type SyntheseStock = {
  nombreArticles: number
  nombreCritique: number
  nombreVigilance: number
  nombreNegatif: number
}

/** Mouvement récent, affiché en lecture seule sur le tableau de bord. */
export type MouvementRecent = {
  uuid: string
  idArticle: string
  codeArticle: string
  libelleArticle: string
  codeUnite: string
  niveauAlerteArticle: NiveauSeuil
  codeTypeMouvement: string
  sens: number
  quantiteSaisie: number
  dateOperation: string
  horodatageServeur: string | null
  statutValidation: StatutValidationMouvement
  nomAuteur: string
  idLogement: string | null
  motif: string | null
}

export type IntervenantJournal = {
  idUtilisateur: string
  nom: string
}
