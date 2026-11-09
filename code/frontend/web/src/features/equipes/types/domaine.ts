/*
  Types du domaine « équipes et affectation du travail » (EF-REF-06), dérivés
  de MPD-1 (`equipe`, `membre_equipe`), CL-1 (`Equipe`, `MembreEquipe`) et
  MPD-5 / CL-5 (`fiche_route`, `ligne_fiche_route`).

  POINT DE MODÉLISATION IMPORTANT, SIGNALÉ. La modélisation fournie ne contient
  AUCUN lien direct étape ↔ équipe : `etape_travaux` (MPD-5) ne référence que le
  logement et l'étape-modèle ; `equipe` / `membre_equipe` (MPD-1) n'ont aucune
  clé vers les étapes. Le seul rattachement du TRAVAIL à une personne passe par
  la `fiche_route`, qui appartient à UN utilisateur (`fiche_route.#utilisateur_
  id_utilisateur`, MPD-5) et regroupe des étapes via `ligne_fiche_route`.

  L'« affectation des étapes aux équipes » (EF-REF-06) est donc réalisée au
  niveau que le modèle permet : on affecte des étapes à un MEMBRE d'équipe (un
  technicien) au moyen d'une fiche de route. Affecter « à l'équipe » revient à
  affecter à l'un de ses membres. Un vrai lien étape↔équipe, s'il est voulu,
  devra d'abord être ajouté au MPD : il n'existe pas dans les fichiers fournis.
  Décision prise avec le porteur du projet.
*/

import type { TypeCycleFiche } from '@/features/avancement/types/enums'

/** Équipe de terrain (MPD-1 `equipe`, CL-1 `Equipe`). */
export type Equipe = {
  id: string
  code: string
  libelle: string
  actif: boolean
}

/**
 * Membre d'une équipe (MPD-1 `membre_equipe`, CL-1 `MembreEquipe`).
 *
 * Clé composite (utilisateur, équipe) dans le modèle ; on la reporte ici sous
 * forme de deux identifiants, enrichis du nom pour l'affichage.
 */
export type MembreEquipe = {
  idUtilisateur: string
  idEquipe: string
  nom: string
  fonction: string
  estChefEquipe: boolean
  dateDebut: string
  dateFin: string | null
}

/** Étape du chantier pouvant être inscrite sur une fiche de route (CL-5 `EtapeTravaux`). */
export type EtapeAffectable = {
  idEtape: string
  libelleEtape: string
  numeroLogement: string
  libelleZone: string
  codeCorpsEtat: string
  libelleCorpsEtat: string
}

/**
 * Fiche de route affectée à un membre (MPD-5 `fiche_route` + `ligne_fiche_route`).
 *
 * Elle appartient à un seul utilisateur et porte les étapes qui lui sont
 * confiées pour un cycle (jour, semaine, quinzaine).
 */
export type FicheRouteAffectation = {
  idFiche: string
  idUtilisateur: string
  nomUtilisateur: string
  typeCycle: TypeCycleFiche
  dateDebut: string
  dateFin: string | null
  statut: 'ouverte' | 'cloturee'
  /** Identifiants des étapes inscrites (lignes de la fiche). */
  idsEtapes: string[]
}

/** Saisie de création d'une fiche de route affectée à un membre. */
export type SaisieAffectation = {
  idUtilisateur: string
  typeCycle: TypeCycleFiche
  dateDebut: string
  dateFin: string | null
  idsEtapes: string[]
}
