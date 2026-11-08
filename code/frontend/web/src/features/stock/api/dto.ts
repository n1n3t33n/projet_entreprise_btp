/*
  Formes servies par l'API Django REST, calquées sur le schéma physique
  (MPD-4) : noms en `snake_case`, clés étrangères suffixées par leur table,
  quantités `numeric(14,3)` transportées en chaîne, énumérés en `UPPER_SNAKE`.

  Ces types ne sortent jamais de la couche `api` : `mapping.ts` les convertit en
  types du domaine. C'est le seul endroit qui connaît le schéma de la base, ce
  qui permet de changer ce schéma sans toucher aux écrans.
*/

/** Niveau de stock stocké (`stock_courant.niveau_alerte`, `alerte.niveau`). */
export type NiveauAlerteDb = 'NORMAL' | 'MINIMAL' | 'CRITIQUE' | 'VIDE'

/** Statut de validation stocké (`mouvement_stock.statut_validation`). */
export type StatutValidationDb =
  | 'ENREGISTRE'
  | 'A_VALIDER'
  | 'EN_ALERTE'
  | 'VALIDE'
  | 'REJETE'
  | 'ANNULE'

export type UniteMesureDto = {
  code_unite: string
  libelle: string
  type_unite: string
}

export type FamilleDto = {
  code_categorie: string
  libelle: string
  code_parent: string | null
}

export type MagasinDto = {
  id_magasin: string
  code: string
  libelle: string
  id_chantier: string
  libelle_chantier: string
}

export type ArticleDto = {
  id_article: string
  code: string
  designation: string
  origine: string
  code_barre: string | null
  actif: boolean
  unite_base: UniteMesureDto
  code_categorie: string
}

export type TypeMouvementDto = {
  code_type_mouvement: string
  libelle: string
  /** Entier : > 0 pour une entrée, < 0 pour une sortie. */
  sens: number
  motif_obligatoire: boolean
  destination_obligatoire: boolean
}

/**
 * Ligne jointe servie par `GET /magasins/{id}/stock` : l'article, ses seuils
 * pour ce magasin et son état courant, en une seule réponse.
 */
export type LigneStockDto = {
  article: ArticleDto
  libelle_famille: string
  seuil: {
    id_seuil: string
    seuil_minimal: string
    seuil_critique: string
    actif: boolean
  }
  stock: {
    quantite: string
    date_calcul: string
    niveau_alerte: NiveauAlerteDb
  }
}

export type MouvementStockDto = {
  uuid: string
  article_id_article: string
  magasin_id_magasin: string
  logement_id_logement: string | null
  type_mouvement_code_type_mouvement: string
  sens: number
  quantite_saisie: string
  quantite_base: string
  date_operation: string
  horodatage_serveur: string | null
  statut_validation: StatutValidationDb
  reference_externe: string | null
  utilisateur_id_utilisateur: string
  nom_auteur: string
  motif: string | null
}
