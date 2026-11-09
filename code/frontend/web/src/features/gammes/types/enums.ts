/*
  Énumérations du domaine gammes, en `camelCase`/minuscules, indépendantes du
  transport. La correspondance avec les littéraux serveur (`UPPER_SNAKE`) est
  faite dans `api/mapping`.
*/

/**
 * Statut d'une version de gamme (voir `StatutGammeDb`). Valeurs déduites des
 * opérations publier()/archiver() de CL-3b, le MPD ne figeant pas la liste.
 */
export type StatutGamme = 'brouillon' | 'active' | 'archivee'
