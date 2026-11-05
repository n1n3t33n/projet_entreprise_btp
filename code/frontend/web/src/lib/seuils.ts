/**
 * Niveau de remplissage d'un stock par rapport à ses seuils.
 *
 * Quatre niveaux, du plus bas au plus confortable. Un stock ne peut pas être
 * négatif : une quantité inférieure ou égale à zéro est un stock vide.
 */
export type NiveauSeuil = 'vide' | 'critique' | 'mini' | 'plein'

export type ParametresSeuil = {
  /** Quantité actuellement en stock. */
  valeur: number
  /**
   * Seuil d'alerte. Atteindre cette quantité déclenche les rappels de
   * réapprovisionnement.
   */
  seuilMini: number
  /**
   * Quantité à partir de laquelle le stock est jugé confortable.
   *
   * Obligatoire et toujours fourni par l'appelant : aucune règle de calcul
   * n'est écrite ici. Un article porte son propre seuil, ou l'application le
   * résout depuis ses paramètres avec `resoudreSeuilConfort`.
   */
  seuilConfort: number
  /**
   * Quantité maximale stockable. Sert uniquement de référence de remplissage
   * à la jauge, jamais au classement du niveau : un magasin de grande
   * capacité resterait sinon indéfiniment sous le seuil de confort.
   */
  capacite?: number
}

/** Référence de remplissage : la capacité si elle est connue, sinon le seuil de confort. */
export function referenceRemplissage({ seuilConfort, capacite }: ParametresSeuil): number {
  return capacite ?? seuilConfort
}

/**
 * Déduit le niveau d'un stock de ses seuils.
 *
 * Séparée de la jauge pour pouvoir trier, filtrer ou déclencher une alerte
 * sans rien afficher.
 */
export function calculerNiveauSeuil({
  valeur,
  seuilMini,
  seuilConfort,
}: ParametresSeuil): NiveauSeuil {
  if (valeur <= 0) {
    return 'vide'
  }
  if (valeur < seuilMini) {
    return 'critique'
  }
  return valeur < seuilConfort ? 'mini' : 'plein'
}

/**
 * Degré d'urgence associé à un niveau.
 *
 * Sert de clé aux paramètres d'alerte : c'est l'urgence, et non le libellé
 * affiché, qui détermine la fréquence des rappels et leurs destinataires.
 */
export type UrgenceAlerte = 'aucune' | 'surveillance' | 'urgente' | 'immediate'

const URGENCE_PAR_NIVEAU: Record<NiveauSeuil, UrgenceAlerte> = {
  plein: 'aucune',
  mini: 'surveillance',
  critique: 'urgente',
  vide: 'immediate',
}

export function urgenceAlerte(niveau: NiveauSeuil): UrgenceAlerte {
  return URGENCE_PAR_NIVEAU[niveau]
}

/** Vrai dès que le seuil d'alerte est atteint, donc pour tout niveau sauf « plein ». */
export function declencheAlerte(niveau: NiveauSeuil): boolean {
  return urgenceAlerte(niveau) !== 'aucune'
}
