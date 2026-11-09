/*
  Conversion des formes serveur (dto) vers les types du domaine avancement.
*/

import type {
  EvenementExecution,
  LigneEtape,
  LigneLogement,
  MotifBlocage,
  StatutEtape,
  StatutLogement,
  SyntheseAvancement,
  Zone,
} from '@/features/avancement/types'
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

const STATUT_ETAPE_DEPUIS_DB: Record<StatutEtapeDb, StatutEtape> = {
  A_FAIRE: 'a_faire',
  EN_COURS: 'en_cours',
  TERMINEE_DECLAREE: 'terminee_declaree',
  VALIDEE: 'validee',
  BLOQUEE: 'bloquee',
}

export function statutEtapeDepuisDb(valeur: StatutEtapeDb): StatutEtape {
  return STATUT_ETAPE_DEPUIS_DB[valeur]
}

const STATUT_LOGEMENT_DEPUIS_DB: Record<StatutLogementDb, StatutLogement> = {
  A_VENIR: 'a_venir',
  EN_COURS: 'en_cours',
  LIVRE: 'livre',
}

/** `numeric(14,3)` transporté en chaîne → nombre, au bord de l'application. */
export function nombreDepuisChaine(valeur: string): number {
  const nombre = Number.parseFloat(valeur)
  return Number.isFinite(nombre) ? nombre : 0
}

export function mapperZone(dto: ZoneDto): Zone {
  return { idZone: dto.id_zone, code: dto.code, nom: dto.nom, idChantier: dto.id_chantier }
}

export function mapperLigneLogement(dto: LigneLogementDto): LigneLogement {
  return {
    idLogement: dto.id_logement,
    numero: dto.numero,
    libelleZone: dto.libelle_zone,
    libelleType: dto.libelle_type,
    statut: STATUT_LOGEMENT_DEPUIS_DB[dto.statut],
    pourcentageDeclare: nombreDepuisChaine(dto.pourcentage_declare),
    pourcentageValide: nombreDepuisChaine(dto.pourcentage_valide),
    nombreEtapes: dto.nombre_etapes,
    nombreValidees: dto.nombre_validees,
    nombreBloquees: dto.nombre_bloquees,
    nombreEnRetard: dto.nombre_en_retard,
  }
}

export function mapperLigneEtape(dto: LigneEtapeDto): LigneEtape {
  return {
    idEtape: dto.id_etape,
    idLogement: dto.id_logement,
    numeroLogement: dto.numero_logement,
    libelleEtape: dto.libelle_etape,
    codeCorpsEtat: dto.code_corps_etat,
    libelleCorpsEtat: dto.libelle_corps_etat,
    couleurCorpsEtat: dto.couleur_corps_etat,
    ordre: dto.ordre,
    statut: statutEtapeDepuisDb(dto.statut),
    datePrevue: dto.date_prevue,
    dateFinDeclaree: dto.date_fin_declaree,
    dateValidation: dto.date_validation,
    poidsEffectif: nombreDepuisChaine(dto.poids_effectif),
    controleRequis: dto.controle_requis,
    enRetard: dto.en_retard,
    idAuteurDeclaration: dto.id_auteur_declaration,
    nomAuteurDeclaration: dto.nom_auteur_declaration,
  }
}

export function mapperEvenement(dto: EvenementExecutionDto): EvenementExecution {
  return {
    uuid: dto.uuid,
    idEtape: dto.etape_travaux_id_etape,
    statutAvant: dto.statut_avant ? statutEtapeDepuisDb(dto.statut_avant) : null,
    statutApres: statutEtapeDepuisDb(dto.statut_apres),
    horodatageAppareil: dto.horodatage_appareil,
    horodatageServeur: dto.horodatage_serveur,
    commentaire: dto.commentaire,
    idAuteur: dto.utilisateur_id_utilisateur,
    nomAuteur: dto.nom_auteur,
    estDelegation: dto.est_delegation,
    codeMotifBlocage: dto.motif_blocage_code_motif,
  }
}

export function mapperMotifBlocage(dto: MotifBlocageDto): MotifBlocage {
  return {
    codeMotif: dto.code_motif,
    libelle: dto.libelle,
    requiertArticle: dto.requiert_article,
    actif: dto.actif,
  }
}

export function mapperSynthese(dto: SyntheseAvancementDto): SyntheseAvancement {
  return {
    pourcentageDeclare: nombreDepuisChaine(dto.pourcentage_declare),
    pourcentageValide: nombreDepuisChaine(dto.pourcentage_valide),
    nombreLogements: dto.nombre_logements,
    nombreEtapesAValider: dto.nombre_etapes_a_valider,
    nombreEtapesBloquees: dto.nombre_etapes_bloquees,
    nombreEtapesEnRetard: dto.nombre_etapes_en_retard,
  }
}
