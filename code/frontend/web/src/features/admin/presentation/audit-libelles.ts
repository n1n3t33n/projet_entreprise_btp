/*
  Libellés d'affichage du journal d'audit.

  La liste des actions connues sert à la fois à nommer l'action dans le tableau
  et à alimenter le filtre « type d'action ». Une action inconnue de cette table
  (ajoutée plus tard côté serveur) reste affichée telle quelle, en clair, plutôt
  que de faire échouer le rendu.
*/

import type { TonStatut } from '@/components/ui'
import { tr } from '@/i18n/tr'

/** Actions d'administration tracées (forme domaine, minuscule). */
export const LIBELLE_ACTION_AUDIT: Record<string, string> = {
  revocation_appareil: tr("Révocation d'appareil"),
  creation_compte: tr('Création de compte'),
  modification_compte: tr('Modification de compte'),
  modification_droits: tr('Modification des droits'),
  import_csv: tr('Import CSV'),
}

/** Tonalité de la pastille d'action : la révocation est signalée en danger. */
export const TON_ACTION_AUDIT: Record<string, TonStatut> = {
  revocation_appareil: 'danger',
  creation_compte: 'succes',
  modification_compte: 'information',
  modification_droits: 'information',
  import_csv: 'information',
}

/** Libellé d'une action, repli sur le code en clair si l'action est inconnue. */
export function libelleAction(action: string): string {
  return LIBELLE_ACTION_AUDIT[action] ?? action
}

/** Tonalité d'une action, neutre par défaut. */
export function tonAction(action: string): TonStatut {
  return TON_ACTION_AUDIT[action] ?? 'neutre'
}
