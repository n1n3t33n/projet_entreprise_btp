/*
  Énumérations du domaine « Avancement des travaux et notifications ».

  Valeurs dérivées de la modélisation : états-transitions ET-1 (cycle d'une
  étape), classes CL-5, MERISE MPD-5. Les listes CHECK du MPD étant génériques,
  les valeurs métier réelles viennent d'ET-1 et des libellés du MPD
  (`A_FAIRE, EN_COURS, TERMINEE_DECLAREE, VALIDEE, BLOQUEE`). On manipule des
  valeurs en minuscules ; la correspondance avec la base est faite dans
  `api/mapping`. Aucun code interne n'est affiché (charte § 8).
*/

/**
 * Statut d'une étape de travaux (ET-1).
 *
 * `terminee_declaree` = terminée déclarée mais pas encore validée. Une étape à
 * contrôle doit être validée (→ `validee`) ou rejetée (→ `en_cours`) ; sans
 * contrôle requis, la validation est implicite (hypothèse H-M3).
 */
export type StatutEtape =
  | 'a_faire'
  | 'en_cours'
  | 'terminee_declaree'
  | 'validee'
  | 'bloquee'

/** Portée d'un avancement agrégé (MPD-5 `avancement_agrege.portee`). */
export type Portee = 'chantier' | 'zone' | 'logement'

/** Statut d'un logement (CL-2, statut générique restreint au pilote). */
export type StatutLogement = 'a_venir' | 'en_cours' | 'livre'

/** Périodicité d'une fiche de route (MPD-5 `fiche_route.type_cycle`). */
export type TypeCycleFiche = 'jour' | 'semaine' | 'quinzaine'

/** Canal d'une notification (MPD-5 `canal`). */
export type CanalNotification = 'application' | 'push' | 'courriel'

/** Décision d'un contrôle d'étape, portée par un formulaire de validation. */
export type DecisionControle = 'valider' | 'rejeter'
