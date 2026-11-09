/*
  Appels réseau du module « équipes et affectation » (EF-REF-06), sur le client
  axios partagé.

  Lecture : équipes, membres d'une équipe, étapes affectables, fiches de route
  d'un membre. Écriture : créer une fiche de route affectée à un membre (ce qui
  revient à affecter des étapes à un technicien, seul rattachement du travail à
  une personne permis par le modèle — voir `types/domaine`).
*/

import { http } from '@/lib/api/http'
import type {
  EquipeDto,
  EtapeAffectableDto,
  FicheRouteDto,
  MembreEquipeDto,
  StatutFicheDb,
  TypeCycleDb,
} from '@/features/equipes/api/dto'
import type { TypeCycleFiche } from '@/features/avancement/types/enums'
import type {
  Equipe,
  EtapeAffectable,
  FicheRouteAffectation,
  MembreEquipe,
  SaisieAffectation,
} from '@/features/equipes/types/domaine'

const CYCLE_DEPUIS_DB: Record<TypeCycleDb, TypeCycleFiche> = {
  JOUR: 'jour',
  SEMAINE: 'semaine',
  QUINZAINE: 'quinzaine',
}

const CYCLE_VERS_DB: Record<TypeCycleFiche, TypeCycleDb> = {
  jour: 'JOUR',
  semaine: 'SEMAINE',
  quinzaine: 'QUINZAINE',
}

const STATUT_FICHE_DEPUIS_DB: Record<StatutFicheDb, FicheRouteAffectation['statut']> = {
  OUVERTE: 'ouverte',
  CLOTUREE: 'cloturee',
}

function mapperEquipe(dto: EquipeDto): Equipe {
  return { id: dto.id_equipe, code: dto.code, libelle: dto.libelle, actif: dto.actif }
}

function mapperMembre(dto: MembreEquipeDto): MembreEquipe {
  return {
    idUtilisateur: dto.utilisateur_id_utilisateur,
    idEquipe: dto.equipe_id_equipe,
    nom: dto.nom_utilisateur,
    fonction: dto.fonction,
    estChefEquipe: dto.est_chef_equipe,
    dateDebut: dto.date_debut,
    dateFin: dto.date_fin,
  }
}

function mapperEtape(dto: EtapeAffectableDto): EtapeAffectable {
  return {
    idEtape: dto.id_etape,
    libelleEtape: dto.libelle_etape,
    numeroLogement: dto.numero_logement,
    libelleZone: dto.libelle_zone,
    codeCorpsEtat: dto.code_corps_etat,
    libelleCorpsEtat: dto.libelle_corps_etat,
  }
}

function mapperFiche(dto: FicheRouteDto): FicheRouteAffectation {
  return {
    idFiche: dto.id_fiche,
    idUtilisateur: dto.utilisateur_id_utilisateur,
    nomUtilisateur: dto.nom_utilisateur,
    typeCycle: CYCLE_DEPUIS_DB[dto.type_cycle] ?? 'semaine',
    dateDebut: dto.date_debut,
    dateFin: dto.date_fin,
    statut: STATUT_FICHE_DEPUIS_DB[dto.statut] ?? 'ouverte',
    idsEtapes: dto.ids_etapes,
  }
}

/** Liste des équipes (MPD-1 `equipe`). */
export async function listerEquipes(): Promise<Equipe[]> {
  const reponse = await http.get<EquipeDto[]>('/equipes')
  return reponse.data.map(mapperEquipe)
}

/** Membres d'une équipe (MPD-1 `membre_equipe`). */
export async function listerMembres(idEquipe: string): Promise<MembreEquipe[]> {
  const reponse = await http.get<MembreEquipeDto[]>(`/equipes/${idEquipe}/membres`)
  return reponse.data.map(mapperMembre)
}

/** Étapes du chantier pouvant être inscrites sur une fiche de route. */
export async function listerEtapesAffectables(): Promise<EtapeAffectable[]> {
  const reponse = await http.get<EtapeAffectableDto[]>('/etapes-affectables')
  return reponse.data.map(mapperEtape)
}

/** Fiches de route d'un membre (MPD-5 `fiche_route` de cet utilisateur). */
export async function listerFichesMembre(idUtilisateur: string): Promise<FicheRouteAffectation[]> {
  const reponse = await http.get<FicheRouteDto[]>(`/membres/${idUtilisateur}/fiches`)
  return reponse.data.map(mapperFiche)
}

/**
 * Crée une fiche de route affectée à un membre (EF-REF-06).
 *
 * C'est l'acte d'affectation : les étapes choisies deviennent les lignes de la
 * fiche (`ligne_fiche_route`), rattachée à ce seul utilisateur (MPD-5).
 */
export async function creerAffectation(saisie: SaisieAffectation): Promise<FicheRouteAffectation> {
  const reponse = await http.post<FicheRouteDto>('/fiches-route', {
    utilisateur_id_utilisateur: saisie.idUtilisateur,
    type_cycle: CYCLE_VERS_DB[saisie.typeCycle],
    date_debut: saisie.dateDebut,
    date_fin: saisie.dateFin,
    ids_etapes: saisie.idsEtapes,
  })
  return mapperFiche(reponse.data)
}
