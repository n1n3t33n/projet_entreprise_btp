/*
  Contrats de transport du module « équipes » (MPD-1 `equipe`, `membre_equipe` ;
  MPD-5 `fiche_route`, `ligne_fiche_route`). `snake_case`, énumérations en
  `UPPER_SNAKE`. Rien de ce fichier ne sort du dossier `api`.
*/

export type EquipeDto = {
  id_equipe: string
  code: string
  libelle: string
  actif: boolean
}

export type MembreEquipeDto = {
  utilisateur_id_utilisateur: string
  equipe_id_equipe: string
  /** Jointure de lecture : nom complet du membre. */
  nom_utilisateur: string
  /** Jointure de lecture : fonction du membre. */
  fonction: string
  est_chef_equipe: boolean
  date_debut: string
  date_fin: string | null
}

export type EtapeAffectableDto = {
  id_etape: string
  libelle_etape: string
  numero_logement: string
  libelle_zone: string
  code_corps_etat: string
  libelle_corps_etat: string
}

/** `UPPER_SNAKE` (MPD-5 `fiche_route.type_cycle`) : JOUR, SEMAINE, QUINZAINE. */
export type TypeCycleDb = 'JOUR' | 'SEMAINE' | 'QUINZAINE'

/** `UPPER_SNAKE` (MPD-5 `fiche_route.statut`). */
export type StatutFicheDb = 'OUVERTE' | 'CLOTUREE'

export type FicheRouteDto = {
  id_fiche: string
  utilisateur_id_utilisateur: string
  nom_utilisateur: string
  type_cycle: TypeCycleDb
  date_debut: string
  date_fin: string | null
  statut: StatutFicheDb
  /** Étapes inscrites sur la fiche (lignes de `ligne_fiche_route`). */
  ids_etapes: string[]
}
