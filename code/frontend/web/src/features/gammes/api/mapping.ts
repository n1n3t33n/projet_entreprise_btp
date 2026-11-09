/*
  Passage du transport au domaine pour le module gammes, et inverse pour les
  corps de requête. Les conversions d'énumérations et de décimaux sont isolées
  ici : ni le domaine ni les écrans ne voient les littéraux serveur.
*/

import type {
  CorpsEtatCorps,
  CorpsEtatDto,
  EtapeModeleCorps,
  EtapeModeleDto,
  GammeDto,
  StatutGammeDb,
} from '@/features/gammes/api/dto'
import type {
  CorpsEtat,
  EtapeModele,
  Gamme,
  SaisieCorpsEtat,
  SaisieEtapeModele,
  StatutGamme,
} from '@/features/gammes/types/domaine'

const STATUTS: Record<StatutGammeDb, StatutGamme> = {
  BROUILLON: 'brouillon',
  ACTIVE: 'active',
  ARCHIVEE: 'archivee',
}

export function statutGammeDepuisDb(valeur: StatutGammeDb): StatutGamme {
  return STATUTS[valeur]
}

function nombre(valeur: string): number {
  const parse = Number.parseFloat(valeur)
  return Number.isFinite(parse) ? parse : 0
}

export function mapperCorpsEtat(dto: CorpsEtatDto): CorpsEtat {
  return {
    code: dto.code_corps_etat,
    libelle: dto.libelle,
    ordre: dto.ordre,
    couleur: dto.couleur,
  }
}

export function mapperGamme(dto: GammeDto): Gamme {
  return {
    id: dto.id_gamme,
    version: dto.version,
    libelle: dto.libelle,
    statut: statutGammeDepuisDb(dto.statut),
    dateActivation: dto.date_activation,
    codeTypeLogement: dto.type_logement_code_type,
    libelleTypeLogement: dto.libelle_type_logement,
    nombreEtapes: dto.nombre_etapes,
    poidsTotal: nombre(dto.poids_total),
  }
}

export function mapperEtapeModele(dto: EtapeModeleDto): EtapeModele {
  return {
    id: dto.id_etape_modele,
    code: dto.code,
    libelle: dto.libelle,
    ordre: dto.ordre,
    poids: nombre(dto.poids),
    controleRequis: dto.controle_requis,
    codeCorpsEtat: dto.corps_etat_code_corps_etat,
    libelleCorpsEtat: dto.libelle_corps_etat,
    couleurCorpsEtat: dto.couleur_corps_etat,
    idGamme: dto.gamme_id_gamme,
  }
}

export function corpsCorpsEtat(saisie: SaisieCorpsEtat): CorpsEtatCorps {
  return {
    code_corps_etat: saisie.code,
    libelle: saisie.libelle,
    ordre: saisie.ordre,
    couleur: saisie.couleur,
  }
}

export function corpsEtape(saisie: SaisieEtapeModele): EtapeModeleCorps {
  return {
    id_etape_modele: saisie.id,
    code: saisie.code,
    libelle: saisie.libelle,
    ordre: saisie.ordre,
    poids: saisie.poids,
    controle_requis: saisie.controleRequis,
    corps_etat_code_corps_etat: saisie.codeCorpsEtat,
  }
}
