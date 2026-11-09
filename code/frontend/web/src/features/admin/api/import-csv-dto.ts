/*
  Contrats de transport de l'import CSV (EF-ADM-02). L'analyse et la validation
  sont faites par le SERVEUR : le client envoie le texte brut du fichier et la
  cible, et reçoit un rapport. Le navigateur n'interprète pas le CSV lui-même,
  pour que la règle de validation soit unique et vive côté serveur.
*/

import type { CibleImport } from '@/features/admin/types/import-csv'

export type LigneImportDto = {
  numero: number
  valeurs: string[]
  erreur: string | null
}

export type RapportImportDto = {
  cible: CibleImport
  colonnes: string[]
  lignes: LigneImportDto[]
  nombre_valides: number
  nombre_erreurs: number
}

export type ResultatImportDto = {
  cible: CibleImport
  nombre_importees: number
}
