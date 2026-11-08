/**
 * Niveau de remplissage d'un stock par rapport à ses seuils.
 *
 * Quatre niveaux, du plus bas au plus confortable.
 *
 * Une quantité inférieure ou égale à zéro est classée « vide » : ces quatre
 * niveaux correspondent à `stock_courant.niveau_alerte` du MPD-4, qui ne
 * distingue pas le stock négatif. Un stock négatif EST possible (cahier des
 * charges : « un stock négatif est autorisé et signalé comme anomalie à
 * corriger ») ; il est porté par un type d'alerte distinct, `STOCK_NEGATIF`
 * (MPD-4 `ck_alerte_type_alerte`), et signalé par `estStockNegatif` plutôt que
 * par un cinquième niveau qui n'existe pas en base.
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
 * Vrai si la quantité est négative : anomalie à corriger, non bloquante.
 *
 * Signalée explicitement à l'écran, comme l'exige la charte (« représentation
 * explicite du stock négatif »). Elle se superpose au niveau « vide » : un
 * stock à zéro et un stock négatif ne doivent pas se ressembler.
 */
export function estStockNegatif(valeur: number): boolean {
  return valeur < 0
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
