/*
  Libellés d'interface du module pilotage.

  Les statuts d'étape ne sont pas retraduits ici : le module avancement en est
  propriétaire et ses libellés sont réexportés tels quels. Deux écrans qui
  nomment différemment le même statut seraient une incohérence pour
  l'utilisateur, et une source d'erreur à la première évolution de l'énuméré.

  Ce fichier ne définit donc que ce qui est propre au pilotage : les noms des
  portées d'agrégation et des niveaux de regroupement affichés.
*/

import type { TonStatut } from '@/components/ui'
import type { NiveauSeuil } from '@/lib/seuils'
import type { PorteeAgregat } from '@/features/pilotage/types'

export { LIBELLE_STATUT_ETAPE, TON_STATUT_ETAPE } from '@/features/avancement/presentation/libelles'

/** Nom affiché de la portée d'un agrégat (CL-5 `Portee`). */
export const LIBELLE_PORTEE: Record<PorteeAgregat, string> = {
  chantier: 'Chantier',
  zone: 'Zone',
  logement: 'Logement',
  corpsEtat: "Corps d'état",
}

/** Nom affiché du groupement choisi dans le tableau de bord. */
export const LIBELLE_GROUPEMENT: Record<'zone' | 'corpsEtat' | 'logement', string> = {
  zone: 'Par zone',
  corpsEtat: "Par corps d'état",
  logement: 'Par logement',
}

/** Libellé du niveau d'alerte d'un article (reprend la sémantique de RG-S5). */
export const LIBELLE_NIVEAU_STOCK: Record<NiveauSeuil, string> = {
  vide: 'Épuisé',
  critique: 'Critique',
  mini: 'Sous le minimum',
  plein: 'Normal',
}

export const TON_NIVEAU_STOCK: Record<NiveauSeuil, TonStatut> = {
  vide: 'danger',
  critique: 'danger',
  mini: 'alerte',
  plein: 'succes',
}

/** Libellé du sens d'un mouvement, à partir de l'entier `sens` du modèle. */
export function libelleSens(sens: number): string {
  return sens > 0 ? 'Entrée' : 'Sortie'
}
