/*
  Modèles de vue et charges utiles d'écriture.

  Ces types ne sont pas dans la modélisation : ce sont les formes que les écrans
  consomment (une ligne de tableau joignant article + stock + seuils) et les
  données qu'un formulaire envoie. Ils dépendent du domaine, jamais l'inverse.
*/

import type { NiveauSeuil } from '@/lib/seuils'

/**
 * Une ligne du tableau de stock d'un magasin : l'article, son état courant et
 * ses seuils, réunis pour l'affichage et la jauge.
 *
 * `seuilMini` et `seuilConfort` sont les propriétés attendues par
 * `ThresholdGauge` ; `seuilMinimal` et `seuilCritique` conservent le
 * vocabulaire du métier pour l'écran de configuration des seuils.
 */
export type LigneStock = {
  idArticle: string
  idMagasin: string
  idSeuil: string
  code: string
  designation: string
  codeFamille: string
  libelleFamille: string
  uniteCode: string
  uniteLibelle: string
  quantite: number
  niveau: NiveauSeuil
  /** Borne basse de la jauge (= seuil critique du modèle). */
  seuilMini: number
  /** Borne haute de la jauge (= seuil minimal du modèle). */
  seuilConfort: number
  seuilMinimal: number
  seuilCritique: number
  actif: boolean
  codeBarre: string | null
}

/** Critères de filtrage de la liste de stock. */
export type FiltreStock = {
  recherche: string
  niveau: NiveauSeuil | 'tous'
  codeFamille: string | 'toutes'
}

/** Charge utile commune à toute saisie de mouvement. */
type SaisieMouvementBase = {
  idMagasin: string
  idArticle: string
  codeTypeMouvement: string
  /** Quantité saisie dans l'unité `codeUnite`. */
  quantite: number
  codeUnite: string
}

/** Saisie d'une entrée de stock — réception (EF-STK-02). */
export type SaisieEntree = SaisieMouvementBase & {
  /** Référence de bon de livraison ou de conteneur (texte libre). */
  referenceExterne: string | null
}

/** Saisie d'une sortie de stock vers un logement (EF-STK-01). */
export type SaisieSortie = SaisieMouvementBase & {
  /** Logement de destination. */
  idLogement: string
  corpsEtat: string | null
  beneficiaire: string | null
  /** Obligatoire pour les types à motif (retour, perte, casse). */
  motif: string | null
}

/** Nœud d'arborescence magasins / familles pour l'écran dédié. */
export type NoeudStock = {
  id: string
  libelle: string
  type: 'chantier' | 'magasin' | 'famille'
  nombreArticles?: number
  enfants: NoeudStock[]
}
