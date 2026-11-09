/*
  Contrats de transport du module gammes, tels que le serveur les expose.

  Convention du projet : `snake_case`, énumérations en `UPPER_SNAKE`, décimaux
  (`numeric(14,3)` du MPD) transportés en chaîne et convertis à la frontière de
  l'application. Rien de ce fichier ne sort du dossier `api`.

  Correspondances (CL-3b, MPD-3) :
  - `CorpsEtatDto` ← corps_etat { code_corps_etat, libelle, ordre, couleur }.
  - `GammeDto` ← gamme { id_gamme, version, libelle, statut, date_activation,
    type_logement_code_type }, enrichi du libellé du type de logement, du nombre
    d'étapes et du poids total (calculés côté serveur).
  - `EtapeModeleDto` ← etape_modele { id_etape_modele, code, libelle, ordre,
    poids, controle_requis, gamme_id_gamme, corps_etat_code_corps_etat }.
*/

/**
 * Statut d'une version de gamme. Le MPD ne fige pas ces littéraux (la contrainte
 * CHECK liste un ensemble générique terminé par « … ») ; ces trois valeurs se
 * déduisent des opérations publier()/archiver() et de l'attribut `version`.
 */
export type StatutGammeDb = 'BROUILLON' | 'ACTIVE' | 'ARCHIVEE'

export type CorpsEtatDto = {
  code_corps_etat: string
  libelle: string
  ordre: number
  couleur: string
}

export type GammeDto = {
  id_gamme: string
  version: number
  libelle: string
  statut: StatutGammeDb
  date_activation: string | null
  type_logement_code_type: string
  libelle_type_logement: string
  nombre_etapes: number
  poids_total: string
}

export type EtapeModeleDto = {
  id_etape_modele: string
  code: string
  libelle: string
  ordre: number
  poids: string
  controle_requis: boolean
  corps_etat_code_corps_etat: string
  libelle_corps_etat: string
  couleur_corps_etat: string
  gamme_id_gamme: string
}

/** Corps de création ou de modification d'un corps d'état. */
export type CorpsEtatCorps = {
  code_corps_etat: string
  libelle: string
  ordre: number
  couleur: string
}

/** Corps d'une étape-modèle transmise lors de l'enregistrement d'une gamme. */
export type EtapeModeleCorps = {
  id_etape_modele: string
  code: string
  libelle: string
  ordre: number
  poids: number
  controle_requis: boolean
  corps_etat_code_corps_etat: string
}
