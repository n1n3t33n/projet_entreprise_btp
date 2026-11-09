/*
  Données de démonstration du paramétrage : paramètres de chantier (EF-REF-07)
  et règles de validation (EF-REF-08). État en mémoire, modifié sur place par
  l'écran, le temps de la session.

  Modélisation : MPD-2 parametre_chantier, MPD-3 regle_validation, CL-2
  ParametreChantier. Les valeurs sont celles d'un chantier plausible de
  Grand-Bassam ; elles ne sortent pas du cadre du modèle.
*/

import type { ParametreChantierDto, RegleValidationDto } from '@/features/parametrage/api/dto'

let compteurParametre = 100
let compteurRegle = 100

let parametres: ParametreChantierDto[] = [
  {
    id_parametre: 'P-001',
    cle: 'delai_synchro_alerte_h',
    valeur: '24',
    type_valeur: 'ENTIER',
    libelle: "Seuil d'alerte de synchronisation (heures)",
  },
  {
    id_parametre: 'P-002',
    cle: 'poids_total_cible',
    valeur: '100',
    type_valeur: 'ENTIER',
    libelle: "Poids total attendu d'une gamme",
  },
  {
    id_parametre: 'P-003',
    cle: 'autoriser_stock_negatif',
    valeur: 'true',
    type_valeur: 'BOOLEEN',
    libelle: 'Autoriser un stock négatif (signalé comme anomalie)',
  },
  {
    id_parametre: 'P-004',
    cle: 'devise',
    valeur: 'XOF',
    type_valeur: 'TEXTE',
    libelle: 'Devise du chantier',
  },
  {
    id_parametre: 'P-005',
    cle: 'tva_pourcent',
    valeur: '18.00',
    type_valeur: 'DECIMAL',
    libelle: 'Taux de TVA (%)',
  },
]

let regles: RegleValidationDto[] = [
  {
    id_regle: 'R-001',
    type_evenement: 'VALIDATION_ETAPE',
    champ_teste: 'delai_validation',
    operateur: 'INFERIEUR_EGAL',
    valeur_seuil: null,
    delai_heures: 72,
  },
  {
    id_regle: 'R-002',
    type_evenement: 'ECART_INVENTAIRE',
    champ_teste: 'ecart_pourcent',
    operateur: 'SUPERIEUR_EGAL',
    valeur_seuil: '5.000',
    delai_heures: null,
  },
  {
    id_regle: 'R-003',
    type_evenement: 'MOUVEMENT_STOCK',
    champ_teste: 'montant',
    operateur: 'SUPERIEUR_EGAL',
    valeur_seuil: '500000.000',
    delai_heures: null,
  },
]

function texte(valeur: unknown, defaut = ''): string {
  return typeof valeur === 'string' ? valeur : defaut
}

function typeValeur(valeur: unknown): ParametreChantierDto['type_valeur'] {
  return valeur === 'ENTIER' || valeur === 'DECIMAL' || valeur === 'BOOLEEN' || valeur === 'TEXTE'
    ? valeur
    : 'TEXTE'
}

/* ------------------------------ Paramètres -------------------------------- */

export function listerParametresDto(): ParametreChantierDto[] {
  return [...parametres]
}

export function creerParametreDepuis(corps: Record<string, unknown>): ParametreChantierDto {
  compteurParametre += 1
  const parametre: ParametreChantierDto = {
    id_parametre: `P-${compteurParametre}`,
    cle: texte(corps.cle),
    valeur: texte(corps.valeur),
    type_valeur: typeValeur(corps.type_valeur),
    libelle: typeof corps.libelle === 'string' ? corps.libelle : null,
  }
  parametres = [...parametres, parametre]
  return parametre
}

export function modifierParametreDepuis(
  id: string,
  corps: Record<string, unknown>,
): ParametreChantierDto | undefined {
  let maj: ParametreChantierDto | undefined
  parametres = parametres.map((parametre) => {
    if (parametre.id_parametre !== id) return parametre
    maj = {
      ...parametre,
      valeur: texte(corps.valeur, parametre.valeur),
      type_valeur: typeValeur(corps.type_valeur),
      libelle: typeof corps.libelle === 'string' ? corps.libelle : null,
    }
    return maj
  })
  return maj
}

/* -------------------------- Règles de validation -------------------------- */

export function listerReglesDto(): RegleValidationDto[] {
  return [...regles]
}

function seuil(valeur: unknown): string | null {
  if (typeof valeur === 'string' && valeur.length > 0) return valeur
  if (typeof valeur === 'number') return valeur.toFixed(3)
  return null
}

function delai(valeur: unknown): number | null {
  if (typeof valeur === 'number' && Number.isFinite(valeur)) return valeur
  return null
}

export function creerRegleDepuis(corps: Record<string, unknown>): RegleValidationDto {
  compteurRegle += 1
  const regle: RegleValidationDto = {
    id_regle: `R-${compteurRegle}`,
    type_evenement: texte(corps.type_evenement, 'VALIDATION_ETAPE'),
    champ_teste: texte(corps.champ_teste),
    operateur: texte(corps.operateur, 'INFERIEUR_EGAL'),
    valeur_seuil: seuil(corps.valeur_seuil),
    delai_heures: delai(corps.delai_heures),
  }
  regles = [...regles, regle]
  return regle
}

export function modifierRegleDepuis(
  id: string,
  corps: Record<string, unknown>,
): RegleValidationDto | undefined {
  let maj: RegleValidationDto | undefined
  regles = regles.map((regle) => {
    if (regle.id_regle !== id) return regle
    maj = {
      ...regle,
      type_evenement: texte(corps.type_evenement, regle.type_evenement),
      champ_teste: texte(corps.champ_teste, regle.champ_teste),
      operateur: texte(corps.operateur, regle.operateur),
      valeur_seuil: seuil(corps.valeur_seuil),
      delai_heures: delai(corps.delai_heures),
    }
    return maj
  })
  return maj
}
