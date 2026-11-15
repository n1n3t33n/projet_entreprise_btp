/*
  Libellés d'interface du module gammes : statuts de gamme et leur tonalité.
*/

import type { TonStatut } from '@/components/ui'
import type { StatutGamme } from '@/features/gammes/types'
import { tr } from '@/i18n/tr'

export const LIBELLE_STATUT_GAMME: Record<StatutGamme, string> = {
  brouillon: tr('Brouillon'),
  active: tr('Active'),
  archivee: tr('Archivée'),
}

export const TON_STATUT_GAMME: Record<StatutGamme, TonStatut> = {
  brouillon: 'alerte',
  active: 'succes',
  archivee: 'neutre',
}
