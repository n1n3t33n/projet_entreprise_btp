/*
  Formes servies par l'API Django REST, calquées sur le schéma physique
  (MPD-2, MPD-3) : noms en `snake_case`, clés étrangères suffixées par leur
  table, énumérés en `UPPER_SNAKE`, quantités `numeric(14,3)` transportées en
  chaîne.

  Ces types ne sortent jamais de la couche `api` : `mapping.ts` les convertit
  en types du domaine. C'est le seul endroit qui connaît le schéma de la base.
*/

/* ------------------------------- Catalogue -------------------------------- */

export type CategorieDto = {
  code_categorie: string
  libelle: string
}

export type UniteMesureDto = {
  code_unite: string
  libelle: string
  /** `UPPER_SNAKE` : MASSE, VOLUME, LONGUEUR, UNITE, SURFACE. */
  type_unite: string
}

export type ArticleDto = {
  id_article: string
  code: string
  designation: string
  /** `UPPER_SNAKE` : ACHAT, PRODUCTION_INTERNE, RECUPERATION. */
  origine: string
  code_barre: string | null
  actif: boolean
  categorie_article_code_categorie: string
  unite_mesure_code_unite: string
}

/* -------------------------- Structure du chantier ------------------------- */

export type MagasinDto = {
  id_magasin: string
  code: string
  nom: string
  actif: boolean
  chantier_id_chantier: string
  /** Libellé du chantier, joint par le serveur pour éviter un second appel. */
  libelle_chantier: string
}

export type ChantierDto = {
  id_chantier: string
  code: string
  nom: string
  programme: string
  /** Date calendaire ISO (`YYYY-MM-DD`). */
  date_debut: string
  /** `UPPER_SNAKE` : ACTIF, INACTIF. */
  statut: string
}

export type ZoneDto = {
  id_zone: string
  code: string
  nom: string
  /** `UPPER_SNAKE` : BATIMENT, NIVEAU, TRANCHE. */
  type_zone: string
  chantier_id_chantier: string
}

export type TypeLogementDto = {
  code_type: string
  libelle: string
  /** `numeric(14,3)` transporté en chaîne. */
  surface_reference: string
  actif: boolean
}

export type LogementDto = {
  id_logement: string
  numero: string
  /** `UPPER_SNAKE` : ACTIF, INACTIF. */
  statut: string
  date_livraison_prevue: string | null
  zone_id_zone: string
  type_logement_code_type: string
}

/**
 * Arborescence d'un chantier servie par `GET
 * /referentiels/chantiers/{id}/arborescence` : le chantier, ses zones et les
 * logements de chaque zone, en une seule réponse.
 */
export type ChantierArbreDto = {
  chantier: ChantierDto
  zones: {
    zone: ZoneDto
    logements: LogementDto[]
  }[]
}
