/*
  Données de démonstration de l'avancement, chantier pilote de Grand-Bassam.

  Trois zones, douze logements, une gamme de dix étapes types de poids total
  100. Les statuts sont répartis sur tout le cycle (ET-1) pour couvrir les cas :
  étapes validées, en cours, à valider (terminées déclarées à contrôle),
  bloquées (avec motif) et en retard. Quelques étapes sont déclarées par
  l'utilisateur courant, pour illustrer le refus de validation par soi-même
  (RG-D11).

  Forme servie identique à l'API (dto). L'état vit en mémoire le temps de la
  session : valider ou bloquer une étape met à jour les agrégats comme le ferait
  le serveur. Les pourcentages sont recalculés à partir des étapes, la
  modélisation ne portant pas de lien stable vers la portée agrégée (§ 6.4).
*/

import { ID_UTILISATEUR_COURANT } from '@/features/avancement/config/capacites'
import type {
  EvenementExecutionDto,
  LigneEtapeDto,
  LigneLogementDto,
  MotifBlocageDto,
  StatutEtapeDb,
  StatutLogementDb,
  SyntheseAvancementDto,
  ZoneDto,
} from '@/features/avancement/api/dto'

const MAINTENANT = new Date('2026-11-08T08:00:00.000Z')

function ajouterJours(base: Date, jours: number): Date {
  const copie = new Date(base)
  copie.setUTCDate(copie.getUTCDate() + jours)
  return copie
}

function dateSeule(date: Date): string {
  return date.toISOString().slice(0, 10)
}

export const ZONES: ZoneDto[] = [
  { id_zone: 'ZON-A', code: 'A', nom: 'Îlot A', id_chantier: 'CH-GB' },
  { id_zone: 'ZON-B', code: 'B', nom: 'Îlot B', id_chantier: 'CH-GB' },
  { id_zone: 'ZON-C', code: 'C', nom: 'Îlot C', id_chantier: 'CH-GB' },
]

export const TYPES_LOGEMENT: Record<string, string> = {
  VILLA3: 'Villa 3 pièces',
  VILLA4: 'Villa 4 pièces',
  DUPLEX: 'Duplex',
}

const CORPS_ETAT: Record<string, { libelle: string; couleur: string }> = {
  GO: { libelle: 'Gros œuvre', couleur: '#6c8ebf' },
  MAC: { libelle: 'Maçonnerie', couleur: '#b8954a' },
  ELEC: { libelle: 'Électricité', couleur: '#9673a6' },
  PLOMB: { libelle: 'Plomberie', couleur: '#3f8f7a' },
  FIN: { libelle: 'Finitions', couleur: '#b85450' },
}

type EtapeModeleSeed = {
  id: string
  libelle: string
  ordre: number
  poids: number
  controleRequis: boolean
  corps: string
}

/** Gamme de référence : dix étapes types, poids total 100. */
const ETAPES_MODELE: EtapeModeleSeed[] = [
  { id: 'EM-01', libelle: 'Fondations', ordre: 1, poids: 15, controleRequis: true, corps: 'GO' },
  {
    id: 'EM-02',
    libelle: 'Élévation des murs',
    ordre: 2,
    poids: 15,
    controleRequis: true,
    corps: 'GO',
  },
  { id: 'EM-03', libelle: 'Cloisons', ordre: 3, poids: 10, controleRequis: false, corps: 'MAC' },
  {
    id: 'EM-04',
    libelle: 'Pose des gaines',
    ordre: 4,
    poids: 8,
    controleRequis: false,
    corps: 'ELEC',
  },
  {
    id: 'EM-05',
    libelle: 'Réseaux plomberie',
    ordre: 5,
    poids: 8,
    controleRequis: false,
    corps: 'PLOMB',
  },
  { id: 'EM-06', libelle: 'Enduits', ordre: 6, poids: 10, controleRequis: false, corps: 'MAC' },
  {
    id: 'EM-07',
    libelle: 'Appareillage électrique',
    ordre: 7,
    poids: 8,
    controleRequis: true,
    corps: 'ELEC',
  },
  {
    id: 'EM-08',
    libelle: 'Appareils sanitaires',
    ordre: 8,
    poids: 8,
    controleRequis: false,
    corps: 'PLOMB',
  },
  { id: 'EM-09', libelle: 'Peinture', ordre: 9, poids: 10, controleRequis: false, corps: 'FIN' },
  { id: 'EM-10', libelle: 'Carrelage', ordre: 10, poids: 8, controleRequis: true, corps: 'FIN' },
]

const POIDS_TOTAL = ETAPES_MODELE.reduce((somme, etape) => somme + etape.poids, 0)

export const MOTIFS_BLOCAGE: MotifBlocageDto[] = [
  {
    code_motif: 'MANQUE_MATERIEL',
    libelle: 'Manque de matériel',
    requiert_article: true,
    actif: true,
  },
  {
    code_motif: 'ATTENTE_CLIENT',
    libelle: 'Attente de décision client',
    requiert_article: false,
    actif: true,
  },
  { code_motif: 'INTEMPERIES', libelle: 'Intempéries', requiert_article: false, actif: true },
  {
    code_motif: 'DEFAUT_TECHNIQUE',
    libelle: 'Défaut technique à reprendre',
    requiert_article: false,
    actif: true,
  },
  {
    code_motif: 'ACCES_IMPOSSIBLE',
    libelle: 'Accès au logement impossible',
    requiert_article: false,
    actif: true,
  },
]

const TYPES_PAR_INDEX = ['VILLA3', 'VILLA4', 'DUPLEX']
const ZONES_IDS = ['ZON-A', 'ZON-B', 'ZON-C']
const TECHNICIENS = [
  { id: 'U-TEC-A', nom: 'Koffi N.' },
  { id: 'U-TEC-B', nom: 'Aya T.' },
  { id: 'U-TEC-C', nom: 'Mamadou D.' },
]

function technicien(index: number): { id: string; nom: string } {
  return TECHNICIENS[index % TECHNICIENS.length]!
}

type EtapeRecord = {
  idEtape: string
  idLogement: string
  idEtapeModele: string
  statut: StatutEtapeDb
  datePrevue: string | null
  dateFinDeclaree: string | null
  dateValidation: string | null
  idAuteurDeclaration: string | null
  nomAuteurDeclaration: string | null
}

export type LogementRecord = {
  idLogement: string
  numero: string
  idZone: string
  codeType: string
  statut: StatutLogementDb
}

export const logements: LogementRecord[] = []
const etapesParLogement = new Map<string, EtapeRecord[]>()
const evenements: EvenementExecutionDto[] = []
let compteurEvenement = 0

function ajouterEvenement(
  idEtape: string,
  avant: StatutEtapeDb | null,
  apres: StatutEtapeDb,
  horodatage: Date,
  auteur: { id: string; nom: string },
  options: { commentaire?: string | null; motif?: string | null; delegation?: boolean } = {},
): void {
  compteurEvenement += 1
  evenements.push({
    uuid: `EVX-${String(compteurEvenement).padStart(5, '0')}`,
    etape_travaux_id_etape: idEtape,
    statut_avant: avant,
    statut_apres: apres,
    horodatage_serveur: horodatage.toISOString(),
    commentaire: options.commentaire ?? null,
    utilisateur_id_utilisateur: auteur.id,
    nom_auteur: auteur.nom,
    est_delegation: options.delegation ?? false,
    motif_blocage_code_motif: options.motif ?? null,
  })
}

// Construction déterministe des douze logements et de leurs étapes.
for (let i = 0; i < 12; i += 1) {
  const numero = `${ZONES_IDS[i % 3]!.slice(-1)}${String(Math.floor(i / 3) + 1).padStart(2, '0')}`
  const idLogement = `LOG-${String(i + 1).padStart(2, '0')}`
  const codeType = TYPES_PAR_INDEX[i % 3]!
  const idZone = ZONES_IDS[i % 3]!

  const nbValide = (i * 7) % 11 // 0..10 étapes pleinement validées
  const retardShift = i % 4 === 0 ? 3 : 0
  const tech = technicien(i)
  const debut = ajouterJours(MAINTENANT, -(nbValide + 1) * 4)

  const records: EtapeRecord[] = ETAPES_MODELE.map((modele) => {
    const idEtape = `${idLogement}-${modele.id}`
    const datePrevue = dateSeule(ajouterJours(debut, (modele.ordre - 1) * 4 - retardShift * 4))
    const base: EtapeRecord = {
      idEtape,
      idLogement,
      idEtapeModele: modele.id,
      statut: 'A_FAIRE',
      datePrevue,
      dateFinDeclaree: null,
      dateValidation: null,
      idAuteurDeclaration: null,
      nomAuteurDeclaration: null,
    }

    const horodateBase = ajouterJours(debut, (modele.ordre - 1) * 4)
    ajouterEvenement(idEtape, null, 'A_FAIRE', horodateBase, { id: 'U-SYS', nom: 'Système' })

    if (modele.ordre <= nbValide) {
      // Étape pleinement avancée : déclarée puis validée (implicite si sans contrôle).
      base.statut = 'VALIDEE'
      const declarant = tech
      const dDecl = ajouterJours(horodateBase, 1)
      base.dateFinDeclaree = dateSeule(dDecl)
      base.idAuteurDeclaration = declarant.id
      base.nomAuteurDeclaration = declarant.nom
      ajouterEvenement(idEtape, 'A_FAIRE', 'EN_COURS', horodateBase, declarant)
      ajouterEvenement(idEtape, 'EN_COURS', 'TERMINEE_DECLAREE', dDecl, declarant)
      const dVal = ajouterJours(dDecl, 1)
      base.dateValidation = dVal.toISOString()
      ajouterEvenement(idEtape, 'TERMINEE_DECLAREE', 'VALIDEE', dVal, {
        id: 'U-CCH',
        nom: 'Chef de chantier',
      })
      return base
    }

    if (modele.ordre === nbValide + 1 && nbValide < ETAPES_MODELE.length) {
      // Étape « courante » : à valider, en cours ou bloquée selon le logement.
      const variante = i % 3
      ajouterEvenement(idEtape, 'A_FAIRE', 'EN_COURS', horodateBase, tech)
      if (variante === 0 && modele.controleRequis) {
        // Déclarée terminée, en attente de contrôle. Corrigé : seul le premier
        // logement est déclaré par l'utilisateur courant (illustration de
        // RG-D11, validation refusée) ; les autres le sont par un technicien et
        // restent validables. Avant, toutes les étapes à valider étaient
        // auto-déclarées : aucune validation n'était possible dans la démo.
        const declarant = i === 0 ? { id: ID_UTILISATEUR_COURANT, nom: 'Vous' } : tech
        const dDecl = ajouterJours(horodateBase, 1)
        base.statut = 'TERMINEE_DECLAREE'
        base.dateFinDeclaree = dateSeule(dDecl)
        base.idAuteurDeclaration = declarant.id
        base.nomAuteurDeclaration = declarant.nom
        ajouterEvenement(idEtape, 'EN_COURS', 'TERMINEE_DECLAREE', dDecl, declarant)
      } else if (variante === 2) {
        base.statut = 'BLOQUEE'
        ajouterEvenement(idEtape, 'EN_COURS', 'BLOQUEE', ajouterJours(horodateBase, 1), tech, {
          motif: 'MANQUE_MATERIEL',
          commentaire: 'En attente de livraison du ciment.',
        })
      } else {
        base.statut = 'EN_COURS'
      }
      return base
    }

    return base
  })

  const statutLogement: StatutLogementDb =
    nbValide >= ETAPES_MODELE.length ? 'LIVRE' : nbValide === 0 ? 'A_VENIR' : 'EN_COURS'

  logements.push({ idLogement, numero, idZone, codeType, statut: statutLogement })
  etapesParLogement.set(idLogement, records)
}

/**
 * Ajoute un logement créé depuis le référentiel de structure. Il n'a encore
 * aucune étape : les étapes naissent de l'application d'une gamme opératoire
 * (référentiel des gammes, étape ultérieure). Il apparaît donc à 0 % dans le
 * suivi d'avancement, ce qui est le comportement attendu.
 */
export function ajouterLogement(record: LogementRecord): void {
  logements.push(record)
  etapesParLogement.set(record.idLogement, [])
}

function modeleDe(idEtapeModele: string): EtapeModeleSeed {
  return ETAPES_MODELE.find((modele) => modele.id === idEtapeModele) ?? ETAPES_MODELE[0]!
}

function libelleZone(idZone: string): string {
  return ZONES.find((zone) => zone.id_zone === idZone)?.nom ?? idZone
}

function estEnRetard(record: EtapeRecord): boolean {
  if (!record.datePrevue) return false
  if (record.statut === 'VALIDEE' || record.statut === 'TERMINEE_DECLAREE') return false
  return new Date(record.datePrevue).getTime() < MAINTENANT.getTime()
}

function versLigneEtape(record: EtapeRecord): LigneEtapeDto {
  const modele = modeleDe(record.idEtapeModele)
  const corps = CORPS_ETAT[modele.corps] ?? { libelle: modele.corps, couleur: '#6c8ebf' }
  const logement = logements.find((l) => l.idLogement === record.idLogement)
  return {
    id_etape: record.idEtape,
    id_logement: record.idLogement,
    numero_logement: logement?.numero ?? record.idLogement,
    libelle_etape: modele.libelle,
    code_corps_etat: modele.corps,
    libelle_corps_etat: corps.libelle,
    couleur_corps_etat: corps.couleur,
    ordre: modele.ordre,
    statut: record.statut,
    date_prevue: record.datePrevue,
    date_fin_declaree: record.dateFinDeclaree,
    date_validation: record.dateValidation,
    poids_effectif: modele.poids.toFixed(3),
    controle_requis: modele.controleRequis,
    en_retard: estEnRetard(record),
    id_auteur_declaration: record.idAuteurDeclaration,
    nom_auteur_declaration: record.nomAuteurDeclaration,
  }
}

function poidsDeclare(record: EtapeRecord): number {
  const modele = modeleDe(record.idEtapeModele)
  return record.statut === 'TERMINEE_DECLAREE' || record.statut === 'VALIDEE' ? modele.poids : 0
}

function poidsValide(record: EtapeRecord): number {
  const modele = modeleDe(record.idEtapeModele)
  return record.statut === 'VALIDEE' ? modele.poids : 0
}

/**
 * Logements d'un chantier vus comme destinations de sortie de stock : la même
 * source que le suivi d'avancement et le référentiel de structure.
 */
export function listerLogementsDestination(idChantier: string): {
  id_logement: string
  numero: string
  libelle_zone: string
  libelle_type: string
}[] {
  const zonesDuChantier = new Set(
    ZONES.filter((zone) => zone.id_chantier === idChantier).map((zone) => zone.id_zone),
  )
  return logements
    .filter((logement) => zonesDuChantier.has(logement.idZone))
    .map((logement) => ({
      id_logement: logement.idLogement,
      numero: logement.numero,
      libelle_zone: libelleZone(logement.idZone),
      libelle_type: TYPES_LOGEMENT[logement.codeType] ?? logement.codeType,
    }))
}

export function construireLignesLogement(): LigneLogementDto[] {
  return logements.map((logement) => {
    const etapes = etapesParLogement.get(logement.idLogement) ?? []
    const declare = etapes.reduce((somme, e) => somme + poidsDeclare(e), 0)
    const valide = etapes.reduce((somme, e) => somme + poidsValide(e), 0)
    return {
      id_logement: logement.idLogement,
      numero: logement.numero,
      libelle_zone: libelleZone(logement.idZone),
      libelle_type: TYPES_LOGEMENT[logement.codeType] ?? logement.codeType,
      statut: logement.statut,
      pourcentage_declare: ((declare / POIDS_TOTAL) * 100).toFixed(3),
      pourcentage_valide: ((valide / POIDS_TOTAL) * 100).toFixed(3),
      nombre_etapes: etapes.length,
      nombre_validees: etapes.filter((e) => e.statut === 'VALIDEE').length,
      nombre_bloquees: etapes.filter((e) => e.statut === 'BLOQUEE').length,
      nombre_en_retard: etapes.filter((e) => estEnRetard(e)).length,
    }
  })
}

export function construireEtapesLogement(idLogement: string): LigneEtapeDto[] {
  const etapes = etapesParLogement.get(idLogement) ?? []
  return etapes.map(versLigneEtape).sort((a, b) => a.ordre - b.ordre)
}

function toutesLesEtapes(): EtapeRecord[] {
  return [...etapesParLogement.values()].flat()
}

export function construireEtapesAValider(): LigneEtapeDto[] {
  return toutesLesEtapes()
    .filter(
      (record) =>
        record.statut === 'TERMINEE_DECLAREE' && modeleDe(record.idEtapeModele).controleRequis,
    )
    .map(versLigneEtape)
}

export function construireSynthese(): SyntheseAvancementDto {
  const etapes = toutesLesEtapes()
  const totalPoidsChantier = logements.length * POIDS_TOTAL
  const declare = etapes.reduce((somme, e) => somme + poidsDeclare(e), 0)
  const valide = etapes.reduce((somme, e) => somme + poidsValide(e), 0)
  return {
    pourcentage_declare: ((declare / totalPoidsChantier) * 100).toFixed(3),
    pourcentage_valide: ((valide / totalPoidsChantier) * 100).toFixed(3),
    nombre_logements: logements.length,
    nombre_etapes_a_valider: construireEtapesAValider().length,
    nombre_etapes_bloquees: etapes.filter((e) => e.statut === 'BLOQUEE').length,
    nombre_etapes_en_retard: etapes.filter((e) => estEnRetard(e)).length,
  }
}

export function listerEvenementsEtape(idEtape: string): EvenementExecutionDto[] {
  return evenements
    .filter((evenement) => evenement.etape_travaux_id_etape === idEtape)
    .sort((a, b) => b.horodatage_serveur.localeCompare(a.horodatage_serveur))
}

function trouverEtape(idEtape: string): EtapeRecord | undefined {
  return toutesLesEtapes().find((record) => record.idEtape === idEtape)
}

/** Valide ou rejette une étape (EF-AVA-06) et journalise la transition. */
export function appliquerValidation(
  idEtape: string,
  decision: 'valider' | 'rejeter',
  motif: string | null,
): EvenementExecutionDto | null {
  const record = trouverEtape(idEtape)
  if (!record || record.statut !== 'TERMINEE_DECLAREE') {
    return null
  }
  const horodatage = new Date()
  const valideur = { id: ID_UTILISATEUR_COURANT, nom: 'Vous' }
  if (decision === 'valider') {
    record.statut = 'VALIDEE'
    record.dateValidation = horodatage.toISOString()
    ajouterEvenement(idEtape, 'TERMINEE_DECLAREE', 'VALIDEE', horodatage, valideur)
  } else {
    record.statut = 'EN_COURS'
    record.dateFinDeclaree = null
    record.idAuteurDeclaration = null
    record.nomAuteurDeclaration = null
    ajouterEvenement(idEtape, 'TERMINEE_DECLAREE', 'EN_COURS', horodatage, valideur, {
      commentaire: motif,
    })
  }
  return listerEvenementsEtape(idEtape)[0] ?? null
}

/** Déclare une étape bloquée (EF-AVA-05) et journalise la transition. */
export function appliquerBlocage(
  idEtape: string,
  codeMotif: string,
  commentaire: string | null,
): EvenementExecutionDto | null {
  const record = trouverEtape(idEtape)
  if (!record || (record.statut !== 'EN_COURS' && record.statut !== 'A_FAIRE')) {
    return null
  }
  const horodatage = new Date()
  const avant = record.statut
  record.statut = 'BLOQUEE'
  ajouterEvenement(
    idEtape,
    avant,
    'BLOQUEE',
    horodatage,
    { id: ID_UTILISATEUR_COURANT, nom: 'Vous' },
    {
      motif: codeMotif,
      commentaire,
    },
  )
  return listerEvenementsEtape(idEtape)[0] ?? null
}
