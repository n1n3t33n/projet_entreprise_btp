/*
  Libellés d'affichage des énumérations du module référentiels.

  Un seul endroit traduit les valeurs du domaine en texte français lisible et
  en tonalités de pastille : les écrans n'écrivent jamais ces libellés en dur,
  et aucun code interne n'apparaît (charte § 8).
*/

import type { TonStatut } from '@/components/ui'
import type {
  OrigineArticle,
  StatutChantier,
  StatutLogement,
  TypeUnite,
  TypeZone,
} from '@/features/referentiels/types'

const LIBELLE_ORIGINE: Record<OrigineArticle, string> = {
  achat: 'Achat',
  production_interne: 'Production interne',
  recuperation: 'Récupération',
}

export function libelleOrigine(valeur: OrigineArticle): string {
  return LIBELLE_ORIGINE[valeur]
}

/** Liste ordonnée des origines, pour alimenter un menu déroulant. */
export const ORIGINES: { valeur: OrigineArticle; libelle: string }[] = [
  { valeur: 'achat', libelle: LIBELLE_ORIGINE.achat },
  { valeur: 'production_interne', libelle: LIBELLE_ORIGINE.production_interne },
  { valeur: 'recuperation', libelle: LIBELLE_ORIGINE.recuperation },
]

const LIBELLE_TYPE_UNITE: Record<TypeUnite, string> = {
  unite: 'Unité',
  masse: 'Masse',
  volume: 'Volume',
  longueur: 'Longueur',
  surface: 'Surface',
}

export function libelleTypeUnite(valeur: TypeUnite): string {
  return LIBELLE_TYPE_UNITE[valeur]
}

const LIBELLE_TYPE_ZONE: Record<TypeZone, string> = {
  batiment: 'Bâtiment',
  niveau: 'Niveau',
  tranche: 'Tranche',
}

export function libelleTypeZone(valeur: TypeZone): string {
  return LIBELLE_TYPE_ZONE[valeur]
}

/** Liste ordonnée des types de zone, pour alimenter un menu déroulant. */
export const TYPES_ZONE: { valeur: TypeZone; libelle: string }[] = [
  { valeur: 'batiment', libelle: LIBELLE_TYPE_ZONE.batiment },
  { valeur: 'niveau', libelle: LIBELLE_TYPE_ZONE.niveau },
  { valeur: 'tranche', libelle: LIBELLE_TYPE_ZONE.tranche },
]

const LIBELLE_STATUT: Record<StatutChantier, string> = {
  actif: 'Actif',
  inactif: 'Inactif',
}

export function libelleStatut(valeur: StatutChantier | StatutLogement): string {
  return LIBELLE_STATUT[valeur]
}

/** Tonalité de pastille d'un statut : vert si actif, neutre sinon. */
export function tonStatut(valeur: StatutChantier | StatutLogement): TonStatut {
  return valeur === 'actif' ? 'succes' : 'neutre'
}

/** Tonalité de pastille d'un indicateur « actif / inactif » booléen. */
export function tonActif(actif: boolean): TonStatut {
  return actif ? 'succes' : 'neutre'
}
