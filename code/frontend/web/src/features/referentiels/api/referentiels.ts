/*
  Appels réseau du module référentiels, sur le client axios partagé
  (`lib/api/http`). Chaque fonction renvoie des types du domaine : la forme
  serveur (dto) ne franchit pas cette couche. L'adaptateur de simulation
  (`lib/mocks`) se branche sur le même client.

  Les listes enrichies (articles, arborescence) chargent en parallèle les
  référentiels dont elles ont besoin pour résoudre leurs libellés, puis les
  croisent via `mapping`. Un écran n'a donc jamais à recomposer un libellé
  lui-même.
*/

import { http } from '@/lib/api/http'
import type {
  Categorie,
  Chantier,
  TypeLogement,
  UniteMesure,
} from '@/features/referentiels/types/domaine'
import type {
  ArticleVue,
  ChantierArbre,
  MagasinVue,
  SaisieArticle,
  SaisieChantier,
  SaisieLogement,
  SaisieMagasin,
  SaisieZone,
} from '@/features/referentiels/types/vues'
import type {
  ArticleDto,
  CategorieDto,
  ChantierArbreDto,
  ChantierDto,
  LogementDto,
  MagasinDto,
  TypeLogementDto,
  UniteMesureDto,
  ZoneDto,
} from '@/features/referentiels/api/dto'
import {
  corpsArticle,
  corpsChantier,
  corpsLogement,
  corpsMagasin,
  corpsZone,
  enrichirArticle,
  mapperArborescence,
  mapperArticle,
  mapperCategorie,
  mapperChantier,
  mapperLogement,
  mapperTypeLogement,
  mapperUnite,
  mapperZone,
} from '@/features/referentiels/api/mapping'
import type { Logement, Zone } from '@/features/referentiels/types/domaine'

/* ------------------------------- Catalogue -------------------------------- */

/** Catégories d'articles (EF-REF-03). */
export async function listerCategories(): Promise<Categorie[]> {
  const reponse = await http.get<CategorieDto[]>('/referentiels/categories')
  return reponse.data.map(mapperCategorie)
}

/** Unités de mesure (EF-REF-04). */
export async function listerUnites(): Promise<UniteMesure[]> {
  const reponse = await http.get<UniteMesureDto[]>('/referentiels/unites')
  return reponse.data.map(mapperUnite)
}

/**
 * Articles du catalogue, enrichis des libellés de catégorie et d'unité
 * (EF-REF-03). Charge en parallèle les trois référentiels puis les croise.
 */
export async function listerArticles(): Promise<ArticleVue[]> {
  const [articles, categories, unites] = await Promise.all([
    http.get<ArticleDto[]>('/referentiels/articles'),
    listerCategories(),
    listerUnites(),
  ])

  const libCategories = new Map(categories.map((c) => [c.code, c.libelle]))
  const libUnites = new Map(unites.map((u) => [u.code, u.libelle]))

  return articles.data
    .map(mapperArticle)
    .map((article) => enrichirArticle(article, libCategories, libUnites))
}

/** Crée un article (EF-REF-03). */
export async function creerArticle(saisie: SaisieArticle): Promise<void> {
  await http.post('/referentiels/articles', corpsArticle(saisie))
}

/** Modifie un article existant (EF-REF-03). */
export async function modifierArticle(id: string, saisie: SaisieArticle): Promise<void> {
  await http.put(`/referentiels/articles/${id}`, corpsArticle(saisie))
}

/* -------------------------------- Magasins -------------------------------- */

/** Magasins, enrichis du nom de leur chantier (EF-REF-02). */
export async function listerMagasins(): Promise<MagasinVue[]> {
  const reponse = await http.get<MagasinDto[]>('/referentiels/magasins')
  return reponse.data.map((dto) => ({
    id: dto.id_magasin,
    code: dto.code,
    nom: dto.nom,
    actif: dto.actif,
    idChantier: dto.chantier_id_chantier,
    libelleChantier: dto.libelle_chantier,
  }))
}

/** Crée un magasin (EF-REF-02). */
export async function creerMagasin(saisie: SaisieMagasin): Promise<void> {
  await http.post('/referentiels/magasins', corpsMagasin(saisie))
}

/** Modifie un magasin existant (EF-REF-02). */
export async function modifierMagasin(id: string, saisie: SaisieMagasin): Promise<void> {
  await http.put(`/referentiels/magasins/${id}`, corpsMagasin(saisie))
}

/* --------------------------- Chantiers & zones ---------------------------- */

/** Chantiers (EF-REF-01). */
export async function listerChantiers(): Promise<Chantier[]> {
  const reponse = await http.get<ChantierDto[]>('/referentiels/chantiers')
  return reponse.data.map(mapperChantier)
}

/** Types de logement (référentiel de la structure). */
export async function listerTypesLogement(): Promise<TypeLogement[]> {
  const reponse = await http.get<TypeLogementDto[]>('/referentiels/types-logement')
  return reponse.data.map(mapperTypeLogement)
}

/**
 * Arbre d'un chantier — zones et logements — enrichi des types de logement
 * (EF-REF-01). Charge l'arbre et les types en parallèle.
 */
export async function chargerArborescence(idChantier: string): Promise<ChantierArbre> {
  const [arbre, types] = await Promise.all([
    http.get<ChantierArbreDto>(`/referentiels/chantiers/${idChantier}/arborescence`),
    listerTypesLogement(),
  ])

  const parType = new Map(types.map((type) => [type.code, type]))
  return mapperArborescence(arbre.data, parType)
}

/** Modifie les informations d'un chantier (EF-REF-01). */
export async function modifierChantier(id: string, saisie: SaisieChantier): Promise<void> {
  await http.put(`/referentiels/chantiers/${id}`, corpsChantier(saisie))
}

/** Crée une zone rattachée à un chantier (EF-REF-01). */
export async function creerZone(saisie: SaisieZone): Promise<Zone> {
  const reponse = await http.post<ZoneDto>('/referentiels/zones', corpsZone(saisie))
  return mapperZone(reponse.data)
}

/** Modifie une zone existante (EF-REF-01). */
export async function modifierZone(id: string, saisie: SaisieZone): Promise<Zone> {
  const reponse = await http.put<ZoneDto>(`/referentiels/zones/${id}`, corpsZone(saisie))
  return mapperZone(reponse.data)
}

/** Crée un logement rattaché à une zone (EF-REF-01). */
export async function creerLogement(saisie: SaisieLogement): Promise<Logement> {
  const reponse = await http.post<LogementDto>('/referentiels/logements', corpsLogement(saisie))
  return mapperLogement(reponse.data)
}

/** Modifie un logement existant (EF-REF-01). */
export async function modifierLogement(id: string, saisie: SaisieLogement): Promise<Logement> {
  const reponse = await http.put<LogementDto>(
    `/referentiels/logements/${id}`,
    corpsLogement(saisie),
  )
  return mapperLogement(reponse.data)
}
