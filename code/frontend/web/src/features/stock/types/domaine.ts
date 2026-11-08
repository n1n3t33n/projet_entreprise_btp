/*
  Entités du domaine stock, telles que les écrans les manipulent.

  Forme « propre » dérivée de la modélisation : identifiants en `camelCase`,
  quantités en `number` (converties depuis le `numeric(14,3)` servi en chaîne
  par l'API, pour écarter la dérive de virgule flottante au transport). La
  correspondance avec le schéma physique (snake_case, clés étrangères) est
  isolée dans `api/dto` et `api/mapping` : les composants ne voient jamais le
  schéma de la base.
*/

import type { NiveauSeuil } from '@/lib/seuils'
import type {
  DecisionValidation,
  OrigineArticle,
  SensMouvement,
  StatutAlerteSeuil,
  StatutInventaire,
  StatutLigneInventaire,
  StatutValidationMouvement,
  TypeAlerteSeuil,
  TypeUnite,
} from '@/features/stock/types/enums'

/** Unité de mesure d'un article (CL-3a). */
export type UniteMesure = {
  code: string
  libelle: string
  typeUnite: TypeUnite
}

/** Famille d'articles, hiérarchique (CL-3a `CategorieArticle`). */
export type FamilleArticle = {
  code: string
  libelle: string
  /** Code de la famille parente, `null` à la racine. */
  codeParent: string | null
}

/** Magasin d'un chantier (CL-2, référencé par le domaine stock). */
export type Magasin = {
  idMagasin: string
  code: string
  libelle: string
  /** Chantier de rattachement, pour l'arborescence. */
  idChantier: string
  libelleChantier: string
}

/** Article du catalogue (CL-3a). */
export type Article = {
  idArticle: string
  code: string
  designation: string
  origine: OrigineArticle
  codeBarre: string | null
  actif: boolean
  uniteBase: UniteMesure
  codeFamille: string
}

/**
 * Type de mouvement (CL-3a `TypeMouvement`).
 *
 * `sens` est déduit du champ entier du modèle. `motifObligatoire` impose un
 * motif (retour, perte, casse), `destinationObligatoire` impose une
 * destination logement (sortie vers un logement).
 */
export type TypeMouvement = {
  code: string
  libelle: string
  sens: SensMouvement
  motifObligatoire: boolean
  destinationObligatoire: boolean
}

/**
 * Seuils d'un article dans un magasin (CL-4 / MLD-4 : clé sur le couple
 * article + magasin).
 *
 * Vocabulaire du modèle et du cahier des charges (EF-STK-06). La conversion
 * vers les propriétés de la jauge (`seuilMini` / `seuilConfort`) est faite dans
 * `api/mapping` — voir l'avertissement qui y figure.
 */
export type SeuilStock = {
  idSeuil: string
  idArticle: string
  idMagasin: string
  seuilMinimal: number
  seuilCritique: number
  actif: boolean
}

/**
 * État courant d'un article dans un magasin (CL-4 `StockCourant`, identifié
 * relativement 1:1 par le seuil).
 */
export type StockCourant = {
  idSeuil: string
  idArticle: string
  idMagasin: string
  quantite: number
  dateCalcul: string
  /** Niveau déjà classé côté serveur (`niveau_alerte`), en vocabulaire d'interface. */
  niveau: NiveauSeuil
}

/** Alerte de seuil déclenchée par un stock bas (CL-4 `Alerte`). */
export type AlerteSeuil = {
  idAlerte: string
  idSeuil: string
  type: TypeAlerteSeuil
  niveau: NiveauSeuil
  message: string
  dateEmission: string
  statut: StatutAlerteSeuil
}

/**
 * Mouvement de stock (CL-4 `MouvementStock`).
 *
 * Journal non modifiable (RG-S8) : aucune mise à jour ni suppression ; une
 * correction passe par un contre-mouvement. Le vocabulaire d'interface dit
 * « horodaté » / « non modifiable », jamais « immuable » (charte § 8).
 */
export type MouvementStock = {
  uuid: string
  idArticle: string
  idMagasin: string
  idLogement: string | null
  codeTypeMouvement: string
  sens: SensMouvement
  quantiteSaisie: number
  quantiteBase: number
  dateOperation: string
  horodatageServeur: string | null
  statutValidation: StatutValidationMouvement
  referenceExterne: string | null
  /** Identifiant de l'auteur, nécessaire au contrôle auteur ≠ validateur (RG-D11). */
  idAuteur: string
  nomAuteur: string
  motif: string | null
}

/** Événement de validation d'un mouvement (CL-4, journal non modifiable). */
export type EvenementValidation = {
  uuid: string
  uuidMouvement: string
  decision: DecisionValidation
  motif: string | null
  horodatageServeur: string
  idAuteur: string
}

/** Inventaire d'un magasin (CL-4). Hors des cinq écrans de l'étape, modélisé pour la complétude. */
export type Inventaire = {
  idInventaire: string
  idMagasin: string
  dateDebut: string
  dateFin: string | null
  statut: StatutInventaire
}

/** Ligne d'un inventaire (CL-4). */
export type LigneInventaire = {
  idLigne: string
  idInventaire: string
  idArticle: string
  quantiteTheorique: number
  quantiteComptee: number
  ecart: number
  statut: StatutLigneInventaire
}
