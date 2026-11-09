/*
  Passage du transport au domaine pour le module pilotage.

  Les conversions d'énumérations ne sont pas redéfinies ici : le pilotage lit
  des données dont les modules avancement et stock sont propriétaires, il
  réutilise donc leurs fonctions de correspondance. Cela garantit qu'un statut
  d'étape ou un niveau d'alerte a le même sens partout dans l'application.
*/

import { nombreDepuisChaine, statutEtapeDepuisDb } from '@/features/avancement/api/mapping'
import {
  niveauDepuisDb,
  quantiteDepuisChaine,
  statutValidationDepuisDb,
} from '@/features/stock/api/mapping'
import type {
  AlerteEtapeDto,
  AvancementAgregeDto,
  EvenementJournalDto,
  IntervenantJournalDto,
  MouvementRecentDto,
  PorteeAgregatDb,
  SyntheseStockDto,
} from '@/features/pilotage/api/dto'
import type {
  AlerteEtape,
  AvancementAgrege,
  EvenementJournal,
  IntervenantJournal,
  MouvementRecent,
  PorteeAgregat,
  SyntheseStock,
} from '@/features/pilotage/types/domaine'

const PORTEES: Record<PorteeAgregatDb, PorteeAgregat> = {
  CHANTIER: 'chantier',
  ZONE: 'zone',
  LOGEMENT: 'logement',
  CORPS_ETAT: 'corpsEtat',
}

export function porteeDepuisDb(valeur: PorteeAgregatDb): PorteeAgregat {
  return PORTEES[valeur]
}

export function mapperAgregat(dto: AvancementAgregeDto): AvancementAgrege {
  return {
    portee: porteeDepuisDb(dto.portee),
    idCible: dto.id_cible,
    libelleCible: dto.libelle_cible,
    libelleSecondaire: dto.libelle_secondaire,
    couleur: dto.couleur,
    pourcentageDeclare: nombreDepuisChaine(dto.pourcentage_declare),
    pourcentageValide: nombreDepuisChaine(dto.pourcentage_valide),
    nombreEtapes: dto.nombre_etapes,
    nombreValidees: dto.nombre_validees,
    nombreBloquees: dto.nombre_bloquees,
    nombreEnRetard: dto.nombre_en_retard,
    dateCalcul: dto.date_calcul,
  }
}

export function mapperAlerteEtape(dto: AlerteEtapeDto): AlerteEtape {
  return {
    idEtape: dto.id_etape,
    idLogement: dto.id_logement,
    numeroLogement: dto.numero_logement,
    libelleZone: dto.libelle_zone,
    libelleEtape: dto.libelle_etape,
    libelleCorpsEtat: dto.libelle_corps_etat,
    couleurCorpsEtat: dto.couleur_corps_etat,
    statut: statutEtapeDepuisDb(dto.statut),
    datePrevue: dto.date_prevue,
    joursDeRetard: dto.jours_de_retard,
    codeMotifBlocage: dto.code_motif_blocage,
    libelleMotifBlocage: dto.libelle_motif_blocage,
    commentaire: dto.commentaire,
  }
}

export function mapperEvenementJournal(dto: EvenementJournalDto): EvenementJournal {
  return {
    uuid: dto.uuid,
    idEtape: dto.id_etape,
    libelleEtape: dto.libelle_etape,
    idLogement: dto.id_logement,
    numeroLogement: dto.numero_logement,
    libelleZone: dto.libelle_zone,
    codeCorpsEtat: dto.code_corps_etat,
    libelleCorpsEtat: dto.libelle_corps_etat,
    statutAvant: dto.statut_avant ? statutEtapeDepuisDb(dto.statut_avant) : null,
    statutApres: statutEtapeDepuisDb(dto.statut_apres),
    horodatageAppareil: dto.horodatage_appareil,
    horodatageServeur: dto.horodatage_serveur,
    idAuteur: dto.id_auteur,
    nomAuteur: dto.nom_auteur,
    estDelegation: dto.est_delegation,
    codeMotifBlocage: dto.code_motif_blocage,
    libelleMotifBlocage: dto.libelle_motif_blocage,
    commentaire: dto.commentaire,
  }
}

export function mapperSyntheseStock(dto: SyntheseStockDto): SyntheseStock {
  return {
    nombreArticles: dto.nombre_articles,
    nombreCritique: dto.nombre_critique,
    nombreVigilance: dto.nombre_vigilance,
    nombreNegatif: dto.nombre_negatif,
  }
}

export function mapperMouvementRecent(dto: MouvementRecentDto): MouvementRecent {
  return {
    uuid: dto.uuid,
    idArticle: dto.article_id_article,
    codeArticle: dto.code_article,
    libelleArticle: dto.libelle_article,
    codeUnite: dto.code_unite,
    niveauAlerteArticle: niveauDepuisDb(dto.niveau_alerte_article),
    codeTypeMouvement: dto.type_mouvement_code_type_mouvement,
    sens: dto.sens,
    quantiteSaisie: quantiteDepuisChaine(dto.quantite_saisie),
    dateOperation: dto.date_operation,
    horodatageServeur: dto.horodatage_serveur,
    statutValidation: statutValidationDepuisDb(dto.statut_validation),
    nomAuteur: dto.nom_auteur,
    idLogement: dto.logement_id_logement,
    motif: dto.motif,
  }
}

export function mapperIntervenant(dto: IntervenantJournalDto): IntervenantJournal {
  return { idUtilisateur: dto.id_utilisateur, nom: dto.nom }
}
