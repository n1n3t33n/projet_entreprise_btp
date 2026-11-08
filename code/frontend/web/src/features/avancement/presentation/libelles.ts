/*
  Libellés et tonalités d'interface du module avancement. Centralise la
  traduction des valeurs métier ; aucun code interne n'est affiché (charte § 8).
*/

import type { TonStatut } from '@/components/ui'
import type { StatutEtape, StatutLogement } from '@/features/avancement/types'

/** Libellé affiché du statut d'une étape. */
export const LIBELLE_STATUT_ETAPE: Record<StatutEtape, string> = {
  a_faire: 'À faire',
  en_cours: 'En cours',
  terminee_declaree: 'Terminée (déclarée)',
  validee: 'Validée',
  bloquee: 'Bloquée',
}

/** Tonalité de pilule associée au statut d'une étape. */
export const TON_STATUT_ETAPE: Record<StatutEtape, TonStatut> = {
  a_faire: 'neutre',
  en_cours: 'information',
  terminee_declaree: 'alerte',
  validee: 'succes',
  bloquee: 'danger',
}

/** Libellé affiché du statut d'un logement. */
export const LIBELLE_STATUT_LOGEMENT: Record<StatutLogement, string> = {
  a_venir: 'À venir',
  en_cours: 'En cours',
  livre: 'Livré',
}

/** Tonalité de pilule associée au statut d'un logement. */
export const TON_STATUT_LOGEMENT: Record<StatutLogement, TonStatut> = {
  a_venir: 'neutre',
  en_cours: 'information',
  livre: 'succes',
}
