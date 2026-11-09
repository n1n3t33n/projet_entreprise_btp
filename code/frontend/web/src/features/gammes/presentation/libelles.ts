/*
  Libellés d'interface du module gammes : statuts de gamme et leur tonalité.
*/

import type { TonStatut } from '@/components/ui'
import type { StatutGamme } from '@/features/gammes/types'

export const LIBELLE_STATUT_GAMME: Record<StatutGamme, string> = {
  brouillon: 'Brouillon',
  active: 'Active',
  archivee: 'Archivée',
}

export const TON_STATUT_GAMME: Record<StatutGamme, TonStatut> = {
  brouillon: 'alerte',
  active: 'succes',
  archivee: 'neutre',
}
