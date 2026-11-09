/*
  Types de domaine du module parametrage, en `camelCase`.

  Source : CL-2 `ParametreChantier`, MPD-2, MPD-3 `regle_validation`.
*/

import type { OperateurRegle, TypeEvenement, TypeValeur } from '@/features/parametrage/types/enums'

export type { OperateurRegle, TypeEvenement, TypeValeur } from '@/features/parametrage/types/enums'

/** Paramètre de chantier typé (EF-REF-07). */
export type ParametreChantier = {
  id: string
  cle: string
  valeur: string
  typeValeur: TypeValeur
  libelle: string | null
}

/** Règle de validation (EF-REF-08). */
export type RegleValidation = {
  id: string
  typeEvenement: TypeEvenement
  champTeste: string
  operateur: OperateurRegle
  valeurSeuil: number | null
  delaiHeures: number | null
}

export type SaisieParametre = {
  cle: string
  valeur: string
  typeValeur: TypeValeur
  libelle: string | null
}

export type SaisieRegle = {
  typeEvenement: TypeEvenement
  champTeste: string
  operateur: OperateurRegle
  valeurSeuil: number | null
  delaiHeures: number | null
}
