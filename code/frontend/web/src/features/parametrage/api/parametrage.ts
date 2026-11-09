/*
  Appels réseau du module parametrage, sur le client axios partagé.

  Deux référentiels distincts partagent cet écran :
  - les paramètres de chantier (EF-REF-07), couples clé/valeur typés ;
  - les règles de validation (EF-REF-08), conditions portant sur un événement.
*/

import { http } from '@/lib/api/http'
import type { ParametreChantierDto, RegleValidationDto } from '@/features/parametrage/api/dto'
import {
  corpsParametre,
  corpsRegle,
  mapperParametre,
  mapperRegle,
} from '@/features/parametrage/api/mapping'
import type {
  ParametreChantier,
  RegleValidation,
  SaisieParametre,
  SaisieRegle,
} from '@/features/parametrage/types/domaine'

/* ----------------------------- Paramètres -------------------------------- */

/** Paramètres du chantier (EF-REF-07). */
export async function listerParametres(): Promise<ParametreChantier[]> {
  const reponse = await http.get<ParametreChantierDto[]>('/parametrage/parametres')
  return reponse.data.map(mapperParametre)
}

/** Crée un paramètre de chantier (EF-REF-07). */
export async function creerParametre(saisie: SaisieParametre): Promise<void> {
  await http.post('/parametrage/parametres', corpsParametre(saisie))
}

/** Modifie un paramètre de chantier existant (EF-REF-07). */
export async function modifierParametre(id: string, saisie: SaisieParametre): Promise<void> {
  await http.put(`/parametrage/parametres/${id}`, corpsParametre(saisie))
}

/* -------------------------- Règles de validation -------------------------- */

/** Règles de validation (EF-REF-08). */
export async function listerRegles(): Promise<RegleValidation[]> {
  const reponse = await http.get<RegleValidationDto[]>('/parametrage/regles')
  return reponse.data.map(mapperRegle)
}

/** Crée une règle de validation (EF-REF-08). */
export async function creerRegle(saisie: SaisieRegle): Promise<void> {
  await http.post('/parametrage/regles', corpsRegle(saisie))
}

/** Modifie une règle de validation existante (EF-REF-08). */
export async function modifierRegle(id: string, saisie: SaisieRegle): Promise<void> {
  await http.put(`/parametrage/regles/${id}`, corpsRegle(saisie))
}
