/*
  Données de démonstration des équipes, des membres et des affectations
  (MPD-1 `equipe`, `membre_equipe` ; MPD-5 `fiche_route`, `ligne_fiche_route`).

  Deux équipes du chantier de Grand-Bassam, chacune avec un chef et des
  techniciens. Le responsable technique du jeu d'essai (USR-003, Koffi
  N'Guessan) est chef de la première équipe. Les techniciens de terrain n'ont
  pas de compte web dans le jeu d'essai (ce sont des utilisateurs mobiles) : ils
  sont identifiés par un id et un nom portés par `membre_equipe`, ce qui suffit
  à l'affectation.

  Les étapes affectables sont un petit échantillon d'étapes du chantier, de quoi
  exercer la composition d'une fiche de route. Les fiches créées vivent en
  mémoire le temps de la session, comme le reste des données simulées.
*/

import type {
  EquipeDto,
  EtapeAffectableDto,
  FicheRouteDto,
  MembreEquipeDto,
} from '@/features/equipes/api/dto'

const EQUIPES: EquipeDto[] = [
  { id_equipe: 'EQ-001', code: 'GO-A', libelle: 'Gros œuvre — équipe A', actif: true },
  { id_equipe: 'EQ-002', code: 'SO-B', libelle: 'Second œuvre — équipe B', actif: true },
]

const MEMBRES: MembreEquipeDto[] = [
  {
    utilisateur_id_utilisateur: 'USR-003',
    equipe_id_equipe: 'EQ-001',
    nom_utilisateur: "Koffi N'Guessan",
    fonction: 'Conducteur de travaux',
    est_chef_equipe: true,
    date_debut: '2026-09-05',
    date_fin: null,
  },
  {
    utilisateur_id_utilisateur: 'USR-T01',
    equipe_id_equipe: 'EQ-001',
    nom_utilisateur: 'Adama Koné',
    fonction: 'Maçon',
    est_chef_equipe: false,
    date_debut: '2026-09-10',
    date_fin: null,
  },
  {
    utilisateur_id_utilisateur: 'USR-T02',
    equipe_id_equipe: 'EQ-001',
    nom_utilisateur: 'Issa Ouattara',
    fonction: 'Ferrailleur',
    est_chef_equipe: false,
    date_debut: '2026-09-10',
    date_fin: null,
  },
  {
    utilisateur_id_utilisateur: 'USR-T03',
    equipe_id_equipe: 'EQ-002',
    nom_utilisateur: 'Fatou Sanogo',
    fonction: 'Cheffe de chantier',
    est_chef_equipe: true,
    date_debut: '2026-09-15',
    date_fin: null,
  },
  {
    utilisateur_id_utilisateur: 'USR-T04',
    equipe_id_equipe: 'EQ-002',
    nom_utilisateur: 'Bakary Cissé',
    fonction: 'Carreleur',
    est_chef_equipe: false,
    date_debut: '2026-09-20',
    date_fin: null,
  },
]

const ETAPES_AFFECTABLES: EtapeAffectableDto[] = [
  {
    id_etape: 'ET-A01-02',
    libelle_etape: 'Élévation des murs',
    numero_logement: 'A01',
    libelle_zone: 'Zone A',
    code_corps_etat: 'GO',
    libelle_corps_etat: 'Gros œuvre',
  },
  {
    id_etape: 'ET-A01-03',
    libelle_etape: 'Dalle de plancher',
    numero_logement: 'A01',
    libelle_zone: 'Zone A',
    code_corps_etat: 'GO',
    libelle_corps_etat: 'Gros œuvre',
  },
  {
    id_etape: 'ET-A02-05',
    libelle_etape: 'Cloisons intérieures',
    numero_logement: 'A02',
    libelle_zone: 'Zone A',
    code_corps_etat: 'SO',
    libelle_corps_etat: 'Second œuvre',
  },
  {
    id_etape: 'ET-B01-07',
    libelle_etape: 'Carrelage sol',
    numero_logement: 'B01',
    libelle_zone: 'Zone B',
    code_corps_etat: 'SO',
    libelle_corps_etat: 'Second œuvre',
  },
  {
    id_etape: 'ET-B01-08',
    libelle_etape: 'Peinture murs',
    numero_logement: 'B01',
    libelle_zone: 'Zone B',
    code_corps_etat: 'PE',
    libelle_corps_etat: 'Peinture',
  },
]

let fiches: FicheRouteDto[] = []
let compteurFiche = 0

export function listerEquipes(): EquipeDto[] {
  return EQUIPES
}

export function listerMembres(idEquipe: string): MembreEquipeDto[] {
  return MEMBRES.filter((membre) => membre.equipe_id_equipe === idEquipe)
}

export function membreExiste(idUtilisateur: string): MembreEquipeDto | undefined {
  return MEMBRES.find((membre) => membre.utilisateur_id_utilisateur === idUtilisateur)
}

export function listerEtapesAffectables(): EtapeAffectableDto[] {
  return ETAPES_AFFECTABLES
}

export function listerFichesMembre(idUtilisateur: string): FicheRouteDto[] {
  return fiches.filter((fiche) => fiche.utilisateur_id_utilisateur === idUtilisateur)
}

/** Crée une fiche de route affectée à un membre, à partir d'étapes connues. */
export function creerFicheMock(corps: Record<string, unknown>): FicheRouteDto | undefined {
  const idUtilisateur = typeof corps.utilisateur_id_utilisateur === 'string' ? corps.utilisateur_id_utilisateur : ''
  const membre = membreExiste(idUtilisateur)
  if (!membre) {
    return undefined
  }

  const idsDemandees = Array.isArray(corps.ids_etapes)
    ? corps.ids_etapes.filter((id): id is string => typeof id === 'string')
    : []
  // On ne retient que des étapes connues : une fiche ne peut pas porter une
  // étape qui n'existe pas au chantier.
  const connues = new Set(ETAPES_AFFECTABLES.map((etape) => etape.id_etape))
  const idsEtapes = idsDemandees.filter((id) => connues.has(id))

  const typeCycle =
    corps.type_cycle === 'JOUR' || corps.type_cycle === 'QUINZAINE' ? corps.type_cycle : 'SEMAINE'

  compteurFiche += 1
  const fiche: FicheRouteDto = {
    id_fiche: `FR-${String(compteurFiche).padStart(3, '0')}`,
    utilisateur_id_utilisateur: idUtilisateur,
    nom_utilisateur: membre.nom_utilisateur,
    type_cycle: typeCycle,
    date_debut: typeof corps.date_debut === 'string' ? corps.date_debut : new Date().toISOString().slice(0, 10),
    date_fin: typeof corps.date_fin === 'string' ? corps.date_fin : null,
    statut: 'OUVERTE',
    ids_etapes: idsEtapes,
  }
  fiches.push(fiche)
  return fiche
}

/** Réinitialise les fiches créées (tests uniquement). */
export function reinitialiserFiches(): void {
  fiches = []
  compteurFiche = 0
}
