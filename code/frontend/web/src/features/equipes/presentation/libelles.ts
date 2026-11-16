/*
  Libellés dtr('affichage du module équipes. Le type de cycle d')une fiche de route
  est propre à ce module d'affectation ; il reprend le même énuméré que la fiche
  de route du domaine avancement (MPD-5 `fiche_route.type_cycle`).
*/

import type { TonStatut } from '@/components/ui'
import type { TypeCycleFiche } from '@/features/avancement/types/enums'
import type { FicheRouteAffectation } from '@/features/equipes/types/domaine'
import { tr } from '@/i18n/tr'

export const LIBELLE_CYCLE: Record<TypeCycleFiche, string> = {
  jour: tr('Journalier'),
  semaine: tr('Hebdomadaire'),
  quinzaine: tr('Quinzaine'),
}

export const LIBELLE_STATUT_FICHE: Record<FicheRouteAffectation['statut'], string> = {
  ouverte: tr('Ouverte'),
  cloturee: tr('Clôturée'),
}

export const TON_STATUT_FICHE: Record<FicheRouteAffectation['statut'], TonStatut> = {
  ouverte: 'information',
  cloturee: 'succes',
}
