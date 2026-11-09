/*
  Libellés et règles d'affichage du domaine « appareils ».

  Deux choses vivent ici, parce qu'elles sont de la présentation et non du
  modèle :
  - la traduction du statut d'appareil en libellé et en tonalité de pastille ;
  - la lecture de la FRAÎCHEUR de synchronisation (RG-Y7) : un appareil dont la
    dernière synchronisation remonte à plus d'un seuil est signalé. Cette
    lecture alimente la supervision des appareils (EF-ADM-03) ET le tableau de
    bord « dernière synchronisation par appareil » laissé en attente à
    EF-DSH-04.

  Le seuil de 24 h est le littéral de RG-Y7. Conformément à la règle produit
  « aucune valeur de réglage en dur » (le seuil de confort, la fréquence des
  alertes… sont paramétrables), ce seuil a vocation à devenir un paramètre du
  chantier (module paramétrage, EF-REF-07) ; il est pour l'instant exposé comme
  une constante nommée, point unique à déplacer vers le paramétrage le jour où
  la clé correspondante existera.
*/

import type { TonStatut } from '@/components/ui'
import type { StatutAppareil } from '@/features/admin/types/appareils'

export const LIBELLE_STATUT_APPAREIL: Record<StatutAppareil, string> = {
  actif: 'Actif',
  revoque: 'Révoqué',
  inactif: 'Inactif',
}

export const TON_STATUT_APPAREIL: Record<StatutAppareil, TonStatut> = {
  actif: 'succes',
  revoque: 'danger',
  inactif: 'neutre',
}

/** Seuil de fraîcheur de synchronisation (RG-Y7), en heures. Futur paramètre (EF-REF-07). */
export const SEUIL_SYNCHRO_HEURES = 24

/** Fraîcheur de la dernière synchronisation d'un appareil, au regard de RG-Y7. */
export type FraicheurSynchro = 'jamais' | 'a_jour' | 'en_retard'

/**
 * Qualifie la dernière synchronisation par rapport au seuil RG-Y7.
 *
 * `reference` est l'heure courante (injectée, pour que la lecture soit
 * testable et cohérente avec l'horloge de référence du reste de l'application).
 */
export function fraicheurSynchro(
  derniereSynchronisation: string | null,
  reference: Date = new Date(),
): FraicheurSynchro {
  if (!derniereSynchronisation) {
    return 'jamais'
  }
  const instant = new Date(derniereSynchronisation)
  if (Number.isNaN(instant.getTime())) {
    return 'jamais'
  }
  const heures = (reference.getTime() - instant.getTime()) / 3_600_000
  return heures > SEUIL_SYNCHRO_HEURES ? 'en_retard' : 'a_jour'
}

export const LIBELLE_FRAICHEUR: Record<FraicheurSynchro, string> = {
  jamais: 'Jamais synchronisé',
  a_jour: 'À jour',
  en_retard: `Plus de ${SEUIL_SYNCHRO_HEURES} h`,
}

export const TON_FRAICHEUR: Record<FraicheurSynchro, TonStatut> = {
  jamais: 'neutre',
  a_jour: 'succes',
  en_retard: 'alerte',
}
