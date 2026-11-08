/*
  Libellés et tonalités d'interface du module stock.

  Centralise la traduction des valeurs métier en texte affichable et en
  tonalité de pilule. Deux règles de la charte s'y appliquent : aucun code
  interne n'est montré (§ 8), et le vocabulaire distingue les trois sens du mot
  « alerte » (niveau de stock, statut de validation, relance). Les trois
  familles de valeurs vivent ici pour qu'un changement de formulation ne touche
  qu'un fichier.
*/

import type { NiveauSeuil } from '@/lib/seuils'
import type { TonStatut } from '@/components/ui'
import type { SensMouvement, StatutValidationMouvement } from '@/features/stock/types'

/** Libellé affiché d'un niveau de stock. */
export const LIBELLE_NIVEAU: Record<NiveauSeuil, string> = {
  vide: 'Vide',
  critique: 'Critique',
  mini: 'Mini',
  plein: 'Plein',
}

/** Tonalité de pilule associée à un niveau de stock. */
export const TON_NIVEAU: Record<NiveauSeuil, TonStatut> = {
  vide: 'danger',
  critique: 'alerte',
  mini: 'information',
  plein: 'succes',
}

/**
 * Libellé du statut de validation d'un mouvement.
 *
 * L'état « délai dépassé » correspond au statut resté sans décision au-delà du
 * délai ; le mot « alerte » est évité à l'écran pour ne pas le confondre avec
 * le niveau de stock.
 */
export const LIBELLE_STATUT_VALIDATION: Record<StatutValidationMouvement, string> = {
  enregistre: 'Enregistré',
  a_valider: 'À valider',
  en_alerte: 'À valider — délai dépassé',
  valide: 'Validé',
  rejete: 'Refusé',
  annule: 'Annulé',
}

/** Tonalité de pilule associée à un statut de validation. */
export const TON_STATUT_VALIDATION: Record<StatutValidationMouvement, TonStatut> = {
  enregistre: 'neutre',
  a_valider: 'information',
  en_alerte: 'alerte',
  valide: 'succes',
  rejete: 'danger',
  annule: 'neutre',
}

/** Libellé du sens d'un mouvement. */
export const LIBELLE_SENS: Record<SensMouvement, string> = {
  entree: 'Entrée',
  sortie: 'Sortie',
}
