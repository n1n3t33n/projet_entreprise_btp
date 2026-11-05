/**
 * Niveau de remplissage d'un stock par rapport à ses seuils.
 *
 * Quatre niveaux nominaux, plus `negatif` qui signale une anomalie de saisie :
 * un stock calculé négatif n'est pas un niveau bas, c'est une incohérence entre
 * les entrées et les sorties enregistrées.
 */
export type NiveauSeuil = 'negatif' | 'vide' | 'critique' | 'mini' | 'plein'

export type ParametresSeuil = {
  /** Quantité actuellement en stock. Peut être négative. */
  valeur: number
  /** Quantité en dessous de laquelle le réapprovisionnement est urgent. */
  seuilMini: number
  /** Quantité à partir de laquelle le stock est jugé confortable. */
  seuilConfort?: number
  /** Quantité maximale stockable, utilisée comme référence de remplissage. */
  capacite?: number
}

/**
 * Seuil de confort retenu : celui fourni, sinon le double du seuil minimum.
 *
 * La capacité n'est volontairement pas utilisée ici : elle sert à mesurer le
 * remplissage de la jauge, pas à juger du niveau. Un magasin dont la capacité
 * est large resterait sinon « mini » en permanence.
 *
 * Le doublement du seuil minimum est une convention d'interface, pas une règle
 * métier validée : elle est à confirmer auprès d'Italia Construction. En
 * attendant, `seuilConfort` permet de transmettre la valeur exacte.
 */
function seuilConfortEffectif({ seuilMini, seuilConfort }: ParametresSeuil): number {
  return seuilConfort ?? seuilMini * 2
}

/**
 * Référence de remplissage de la jauge : la capacité si elle est connue,
 * sinon le seuil de confort.
 */
export function referenceRemplissage(parametres: ParametresSeuil): number {
  return parametres.capacite ?? seuilConfortEffectif(parametres)
}

/**
 * Déduit le niveau d'un stock de ses seuils.
 *
 * Exportée séparément de la jauge pour pouvoir trier ou filtrer une liste
 * d'articles par niveau sans rien afficher.
 */
export function calculerNiveauSeuil(parametres: ParametresSeuil): NiveauSeuil {
  const { valeur, seuilMini } = parametres

  if (valeur < 0) {
    return 'negatif'
  }
  if (valeur === 0) {
    return 'vide'
  }
  if (valeur < seuilMini) {
    return 'critique'
  }

  return valeur < seuilConfortEffectif(parametres) ? 'mini' : 'plein'
}
