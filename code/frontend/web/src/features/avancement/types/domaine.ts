/*
  Entités du domaine avancement, forme « propre » dérivée de la modélisation
  (CL-2, CL-3b, CL-5). Identifiants en camelCase ; poids et pourcentages en
  `number` (convertis depuis le `numeric(14,3)` servi en chaîne, pour écarter la
  dérive de virgule flottante au transport). Le schéma physique reste dans
  `api/dto` et `api/mapping`.
*/

import type {
  CanalNotification,
  Portee,
  StatutEtape,
  StatutLogement,
  TypeCycleFiche,
} from '@/features/avancement/types/enums'

/** Corps d'état (CL-3b) : lot de métier ordonné, avec une couleur d'affichage. */
export type CorpsEtat = {
  code: string
  libelle: string
  ordre: number
  couleur: string
}

/** Étape type d'une gamme (CL-3b `EtapeModele`). */
export type EtapeModele = {
  idEtapeModele: string
  code: string
  libelle: string
  ordre: number
  /** Poids relatif dans l'avancement du logement. */
  poids: number
  /** Vrai si l'étape exige une validation explicite (sinon validation implicite). */
  controleRequis: boolean
  codeCorpsEtat: string
}

/** Chantier (CL-2). */
export type Chantier = {
  idChantier: string
  code: string
  nom: string
}

/** Zone d'un chantier (CL-2). */
export type Zone = {
  idZone: string
  code: string
  nom: string
  idChantier: string
}

/** Logement d'une zone (CL-2). */
export type Logement = {
  idLogement: string
  numero: string
  statut: StatutLogement
  idZone: string
  codeTypeLogement: string
  dateLivraisonPrevue: string | null
}

/**
 * Étape de travaux instanciée sur un logement (CL-5 `EtapeTravaux`).
 *
 * Champs dénormalisés (libellé, corps d'état, contrôle requis, auteur de la
 * déclaration) repris depuis l'étape modèle et le journal, pour éviter aux
 * écrans de recouper plusieurs ressources. `idAuteurDeclaration` sert au
 * contrôle auteur ≠ validateur (RG-D11).
 */
export type EtapeTravaux = {
  idEtape: string
  idLogement: string
  idEtapeModele: string
  libelleEtape: string
  codeCorpsEtat: string
  ordre: number
  statut: StatutEtape
  datePrevue: string | null
  dateFinDeclaree: string | null
  dateValidation: string | null
  poidsEffectif: number
  controleRequis: boolean
  idAuteurDeclaration: string | null
  nomAuteurDeclaration: string | null
}

/**
 * Événement d'exécution d'une étape (CL-5, journal non modifiable, RG-S8).
 *
 * Trace chaque transition de statut (avant → après), horodatée et attribuée à
 * un auteur. `estDelegation` signale une déclaration faite pour le compte d'un
 * autre (EF-AVA-07).
 */
export type EvenementExecution = {
  uuid: string
  idEtape: string
  statutAvant: StatutEtape | null
  statutApres: StatutEtape
  horodatageServeur: string
  commentaire: string | null
  idAuteur: string
  nomAuteur: string
  estDelegation: boolean
  codeMotifBlocage: string | null
}

/** Motif de blocage (CL-3b `MotifBlocage`). */
export type MotifBlocage = {
  codeMotif: string
  libelle: string
  /** Vrai si le motif impose de désigner un article (ex. manque de matériel, RG-A10). */
  requiertArticle: boolean
  actif: boolean
}

/**
 * Avancement agrégé sur une portée (CL-5 `AvancementAgrege`).
 *
 * La modélisation note que cette entité n'a ni identifiant conceptuel ni lien
 * explicite vers la portée agrégée dans CL-0 (lacune signalée au MLD § 6.4) :
 * `idPortee` est donc optionnel, et les agrégats du pilote sont recalculés à
 * partir des étapes plutôt que lus tels quels.
 */
export type AvancementAgrege = {
  portee: Portee
  idPortee: string | null
  pourcentageDeclare: number
  pourcentageValide: number
  nombreEtapes: number
  dateCalcul: string
}

/* --- Entités de complétude du domaine, non consommées par les écrans de l'étape --- */

/** Fiche de route (CL-5) — cycle de travail d'un technicien. Portée mobile. */
export type FicheRoute = {
  idFiche: string
  typeCycle: TypeCycleFiche
  dateDebut: string
  dateFin: string | null
  statut: string
  dateCloture: string | null
}

/** Type de notification (CL-5). */
export type TypeNotification = {
  codeType: string
  libelle: string
  canalDefaut: CanalNotification
}

/** Notification émise (CL-5). */
export type Notification = {
  idNotification: string
  message: string
  canal: CanalNotification
  dateCreation: string
  dateLecture: string | null
}
