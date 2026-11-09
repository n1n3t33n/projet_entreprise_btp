/*
  Appels réseau du module gammes, sur le client axios partagé.

  Règles de gestion portées par ces routes (EF-REF-05, EF-REF-09) :
  - les étapes d'une gamme ne s'enregistrent que si elle est en brouillon ;
  - publier une version la rend active et archive la précédente version active
    du même type de logement ;
  - créer une version produit un brouillon copié de la version active.
  Ces règles sont appliquées côté serveur (ici, l'adaptateur de simulation) : le
  client les reflète dans l'interface mais ne s'y substitue pas.
*/

import { http } from '@/lib/api/http'
import type { CorpsEtatDto, EtapeModeleDto, GammeDto } from '@/features/gammes/api/dto'
import {
  corpsCorpsEtat,
  corpsEtape,
  mapperCorpsEtat,
  mapperEtapeModele,
  mapperGamme,
} from '@/features/gammes/api/mapping'
import type {
  CorpsEtat,
  Gamme,
  GammeDetail,
  SaisieCorpsEtat,
  SaisieEtapeModele,
} from '@/features/gammes/types/domaine'

/* ------------------------------ Corps d'état ------------------------------ */

/** Corps d'état, triés par ordre (EF-REF-05). */
export async function listerCorpsEtat(): Promise<CorpsEtat[]> {
  const reponse = await http.get<CorpsEtatDto[]>('/gammes/corps-etat')
  return reponse.data.map(mapperCorpsEtat)
}

/** Crée un corps d'état (EF-REF-05). */
export async function creerCorpsEtat(saisie: SaisieCorpsEtat): Promise<void> {
  await http.post('/gammes/corps-etat', corpsCorpsEtat(saisie))
}

/** Modifie un corps d'état existant (EF-REF-05). */
export async function modifierCorpsEtat(code: string, saisie: SaisieCorpsEtat): Promise<void> {
  await http.put(`/gammes/corps-etat/${code}`, corpsCorpsEtat(saisie))
}

/* -------------------------------- Gammes ---------------------------------- */

/** Gammes, toutes versions et tous statuts, groupées par type de logement. */
export async function listerGammes(): Promise<Gamme[]> {
  const reponse = await http.get<GammeDto[]>('/gammes')
  return reponse.data.map(mapperGamme)
}

/** Détail d'une gamme : ses attributs et ses étapes triées (EF-REF-05). */
export async function chargerGamme(idGamme: string): Promise<GammeDetail> {
  const [gamme, etapes] = await Promise.all([
    http.get<GammeDto>(`/gammes/${idGamme}`),
    http.get<EtapeModeleDto[]>(`/gammes/${idGamme}/etapes`),
  ])
  return {
    gamme: mapperGamme(gamme.data),
    etapes: etapes.data.map(mapperEtapeModele),
  }
}

/** Crée une version brouillon copiée d'une gamme existante (EF-REF-09). */
export async function creerVersion(idGammeSource: string): Promise<Gamme> {
  const reponse = await http.post<GammeDto>(`/gammes/${idGammeSource}/versions`, {})
  return mapperGamme(reponse.data)
}

/** Remplace les étapes d'une gamme brouillon (EF-REF-05). */
export async function enregistrerEtapes(
  idGamme: string,
  etapes: SaisieEtapeModele[],
): Promise<void> {
  await http.put(`/gammes/${idGamme}/etapes`, { etapes: etapes.map(corpsEtape) })
}

/** Publie une gamme brouillon ; archive la version active précédente (EF-REF-09). */
export async function publierGamme(idGamme: string): Promise<Gamme> {
  const reponse = await http.post<GammeDto>(`/gammes/${idGamme}/publication`, {})
  return mapperGamme(reponse.data)
}

/** Archive une gamme active sans la remplacer (EF-REF-09). */
export async function archiverGamme(idGamme: string): Promise<Gamme> {
  const reponse = await http.post<GammeDto>(`/gammes/${idGamme}/archivage`, {})
  return mapperGamme(reponse.data)
}
