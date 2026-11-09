/*
  Passage du transport au domaine pour le module parametrage, et inverse pour
  les corps de requête. Les conversions d'énumérations sont isolées ici.
*/

import type {
  ParametreChantierCorps,
  ParametreChantierDto,
  RegleValidationCorps,
  RegleValidationDto,
  TypeValeurDb,
} from '@/features/parametrage/api/dto'
import type {
  OperateurRegle,
  ParametreChantier,
  RegleValidation,
  SaisieParametre,
  SaisieRegle,
  TypeEvenement,
  TypeValeur,
} from '@/features/parametrage/types/domaine'

const TYPES_VALEUR: Record<TypeValeurDb, TypeValeur> = {
  ENTIER: 'entier',
  DECIMAL: 'decimal',
  BOOLEEN: 'booleen',
  TEXTE: 'texte',
}
const TYPES_VALEUR_DB: Record<TypeValeur, TypeValeurDb> = {
  entier: 'ENTIER',
  decimal: 'DECIMAL',
  booleen: 'BOOLEEN',
  texte: 'TEXTE',
}

// Les littéraux d'événement et d'opérateur sont des varchar libres côté MPD :
// on les transporte en `UPPER_SNAKE` par cohérence avec le reste du projet.
const EVENEMENTS_DB: Record<TypeEvenement, string> = {
  declaration_etape: 'DECLARATION_ETAPE',
  validation_etape: 'VALIDATION_ETAPE',
  ecart_inventaire: 'ECART_INVENTAIRE',
  mouvement_stock: 'MOUVEMENT_STOCK',
}
const OPERATEURS_DB: Record<OperateurRegle, string> = {
  inferieur_egal: 'INFERIEUR_EGAL',
  superieur_egal: 'SUPERIEUR_EGAL',
  egal: 'EGAL',
  inferieur: 'INFERIEUR',
  superieur: 'SUPERIEUR',
}

function inverser<T extends string>(table: Record<T, string>): Map<string, T> {
  return new Map(Object.entries(table).map(([cle, valeur]) => [valeur as string, cle as T]))
}
const EVENEMENTS = inverser(EVENEMENTS_DB)
const OPERATEURS = inverser(OPERATEURS_DB)

export function mapperParametre(dto: ParametreChantierDto): ParametreChantier {
  return {
    id: dto.id_parametre,
    cle: dto.cle,
    valeur: dto.valeur,
    typeValeur: TYPES_VALEUR[dto.type_valeur],
    libelle: dto.libelle,
  }
}

export function mapperRegle(dto: RegleValidationDto): RegleValidation {
  return {
    id: dto.id_regle,
    typeEvenement: EVENEMENTS.get(dto.type_evenement) ?? 'validation_etape',
    champTeste: dto.champ_teste,
    operateur: OPERATEURS.get(dto.operateur) ?? 'inferieur_egal',
    valeurSeuil: dto.valeur_seuil === null ? null : Number.parseFloat(dto.valeur_seuil),
    delaiHeures: dto.delai_heures,
  }
}

export function corpsParametre(saisie: SaisieParametre): ParametreChantierCorps {
  return {
    cle: saisie.cle,
    valeur: saisie.valeur,
    type_valeur: TYPES_VALEUR_DB[saisie.typeValeur],
    libelle: saisie.libelle,
  }
}

export function corpsRegle(saisie: SaisieRegle): RegleValidationCorps {
  return {
    type_evenement: EVENEMENTS_DB[saisie.typeEvenement],
    champ_teste: saisie.champTeste,
    operateur: OPERATEURS_DB[saisie.operateur],
    valeur_seuil: saisie.valeurSeuil === null ? null : saisie.valeurSeuil.toFixed(3),
    delai_heures: saisie.delaiHeures,
  }
}
