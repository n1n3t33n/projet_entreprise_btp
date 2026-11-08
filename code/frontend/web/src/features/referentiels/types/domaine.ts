/*
  Types du domaine « Référentiels et catalogue », en camelCase.

  Dérivés des diagrammes de classes qui font foi pour la structure :
  - CL-3a : `Article`, `CategorieArticle`, `UniteMesure` (catalogue).
  - CL-2  : `Chantier`, `Zone`, `TypeLogement`, `Logement` (structure).

  Les clés étrangères sont portées par le code ou l'identifiant de l'entité
  liée (`codeCategorie`, `idChantier`), jamais par l'objet lié : chaque écran
  recompose les libellés via les vues (`types/vues`). Les quantités réelles
  (`surfaceReference`, `numeric(14,3)` au MPD) sont des nombres ici, converties
  depuis la chaîne de transport au bord de l'application (`api/mapping`).
*/

import type {
  OrigineArticle,
  StatutChantier,
  StatutLogement,
  TypeUnite,
  TypeZone,
} from '@/features/referentiels/types/enums'

/**
 * Catégorie d'article (CL-3a `CategorieArticle`, MPD-3 `categorie_article`).
 *
 * ÉCART SIGNALÉ : CL-3a modélise une hiérarchie (`sousCategories()`), mais la
 * table `categorie_article` du MPD-3 ne porte aucune colonne parent. Le modèle
 * physique, qui fait foi pour l'implémentation, décrit donc des catégories
 * plates — ce module les traite ainsi.
 */
export type Categorie = {
  /** Code référentiel, clé primaire `varchar` (MPD-3). */
  code: string
  libelle: string
}

/** Unité de mesure (CL-3a `UniteMesure`, MPD-3 `unite_mesure`). */
export type UniteMesure = {
  /** Code référentiel, clé primaire `varchar`. */
  code: string
  libelle: string
  typeUnite: TypeUnite
}

/** Article du catalogue (CL-3a `Article`, MPD-3 `article`). */
export type Article = {
  id: string
  /** Code interne unique (MPD-3 `code UNIQUE`). */
  code: string
  designation: string
  origine: OrigineArticle
  /** Code-barres, unique quand présent (MPD-3 `code_barre UNIQUE`). */
  codeBarre: string | null
  actif: boolean
  codeCategorie: string
  codeUnite: string
}

/** Magasin de stockage (CL-2 / MPD-2 `magasin`). */
export type Magasin = {
  id: string
  /** Code interne unique (MPD-2 `code UNIQUE`). */
  code: string
  nom: string
  actif: boolean
  /** Chantier de rattachement (MPD-2 FK `chantier`). */
  idChantier: string
}

/** Chantier (CL-2 `Chantier`, MPD-2 `chantier`). */
export type Chantier = {
  id: string
  /** Code interne unique (MPD-2 `code UNIQUE`). */
  code: string
  nom: string
  programme: string
  /** Date de début, date calendaire (MPD-2 `date` ISO). */
  dateDebut: string
  statut: StatutChantier
}

/** Zone d'un chantier (CL-2 `Zone`, MPD-2 `zone`). */
export type Zone = {
  id: string
  /** Code interne unique (MPD-2 `code UNIQUE`). */
  code: string
  nom: string
  typeZone: TypeZone
  idChantier: string
}

/** Type de logement (CL-2 `TypeLogement`, MPD-2 `type_logement`). */
export type TypeLogement = {
  /** Code référentiel, clé primaire `varchar` (MPD-2 `code_type`). */
  code: string
  libelle: string
  /** Surface de référence en m² (MPD-2 `surface_reference numeric(14,3)`). */
  surfaceReference: number
  actif: boolean
}

/** Logement (CL-2 `Logement`, MPD-2 `logement`). */
export type Logement = {
  id: string
  numero: string
  statut: StatutLogement
  /** Date de livraison prévue, calendaire ou absente. */
  dateLivraisonPrevue: string | null
  idZone: string
  codeTypeLogement: string
}
