/*
  Formes servies par l'API (schéma physique MPD-5) : snake_case, pourcentages et
  poids `numeric(14,3)` transportés en chaîne, énumérés en UPPER_SNAKE. Ne
  sortent pas de la couche api.
*/

export type StatutEtapeDb = 'A_FAIRE' | 'EN_COURS' | 'TERMINEE_DECLAREE' | 'VALIDEE' | 'BLOQUEE'

export type StatutLogementDb = 'A_VENIR' | 'EN_COURS' | 'LIVRE'

export type ZoneDto = {
  id_zone: string
  code: string
  nom: string
  id_chantier: string
}

export type LigneLogementDto = {
  id_logement: string
  numero: string
  libelle_zone: string
  libelle_type: string
  statut: StatutLogementDb
  pourcentage_declare: string
  pourcentage_valide: string
  nombre_etapes: number
  nombre_validees: number
  nombre_bloquees: number
  nombre_en_retard: number
}

export type LigneEtapeDto = {
  id_etape: string
  id_logement: string
  numero_logement: string
  libelle_etape: string
  code_corps_etat: string
  libelle_corps_etat: string
  couleur_corps_etat: string
  ordre: number
  statut: StatutEtapeDb
  date_prevue: string | null
  date_fin_declaree: string | null
  date_validation: string | null
  poids_effectif: string
  controle_requis: boolean
  en_retard: boolean
  id_auteur_declaration: string | null
  nom_auteur_declaration: string | null
}

export type EvenementExecutionDto = {
  uuid: string
  etape_travaux_id_etape: string
  statut_avant: StatutEtapeDb | null
  statut_apres: StatutEtapeDb
  /** Instant saisi sur le terminal mobile (CL-5 `horodatageAppareil`). */
  horodatage_appareil: string
  /** Instant d'enregistrement par le serveur (CL-5 `horodatageServeur`). */
  horodatage_serveur: string
  commentaire: string | null
  utilisateur_id_utilisateur: string
  nom_auteur: string
  est_delegation: boolean
  motif_blocage_code_motif: string | null
}

export type MotifBlocageDto = {
  code_motif: string
  libelle: string
  requiert_article: boolean
  actif: boolean
}

export type SyntheseAvancementDto = {
  pourcentage_declare: string
  pourcentage_valide: string
  nombre_logements: number
  nombre_etapes_a_valider: number
  nombre_etapes_bloquees: number
  nombre_etapes_en_retard: number
}
