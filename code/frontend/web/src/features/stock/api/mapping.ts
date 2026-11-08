/*
  Conversion des formes servies par l'API (dto, schéma physique) vers les types
  du domaine utilisés par les écrans.
*/

import type { NiveauSeuil } from '@/lib/seuils'
import type { SensMouvement, StatutValidationMouvement } from '@/features/stock/types'
import type { LigneStock, MouvementStock, TypeMouvement } from '@/features/stock/types'
import type {
  LigneStockDto,
  MouvementStockDto,
  NiveauAlerteDb,
  StatutValidationDb,
  TypeMouvementDto,
} from '@/features/stock/api/dto'

/**
 * Correspondance des seuils entre le modèle et la jauge — point d'attention.
 *
 * Le modèle et le cahier des charges (EF-STK-06) nomment les deux seuils
 * « seuil minimal » et « seuil critique » (avec critique < minimal). La
 * bibliothèque `lib/seuils` raisonne, elle, en « seuil d'alerte » bas
 * (`seuilMini`) et « seuil de confort » haut (`seuilConfort`) : `critique`
 * en-dessous de `seuilMini`, `mini` en-dessous de `seuilConfort`, `plein`
 * au-delà.
 *
 * La seule correspondance qui rende cohérents à la fois `calculerNiveauSeuil`,
 * le niveau calculé côté serveur et la règle des quatre niveaux est donc
 * **croisée** :
 *
 *   seuilMini   (jauge, borne basse) ← seuil_critique (modèle)
 *   seuilConfort(jauge, borne haute) ← seuil_minimal  (modèle)
 *
 * Le nom « minimal » du modèle devient donc la borne « confort » de la jauge.
 * La conversion est faite ici, une fois, jamais dans un composant.
 */
export function seuilsVersJauge(
  seuilMinimal: number,
  seuilCritique: number,
): {
  seuilMini: number
  seuilConfort: number
} {
  return { seuilMini: seuilCritique, seuilConfort: seuilMinimal }
}

const NIVEAU_DEPUIS_DB: Record<NiveauAlerteDb, NiveauSeuil> = {
  VIDE: 'vide',
  CRITIQUE: 'critique',
  MINIMAL: 'mini',
  NORMAL: 'plein',
}

export function niveauDepuisDb(valeur: NiveauAlerteDb): NiveauSeuil {
  return NIVEAU_DEPUIS_DB[valeur]
}

const STATUT_DEPUIS_DB: Record<StatutValidationDb, StatutValidationMouvement> = {
  ENREGISTRE: 'enregistre',
  A_VALIDER: 'a_valider',
  EN_ALERTE: 'en_alerte',
  VALIDE: 'valide',
  REJETE: 'rejete',
  ANNULE: 'annule',
}

export function statutValidationDepuisDb(valeur: StatutValidationDb): StatutValidationMouvement {
  return STATUT_DEPUIS_DB[valeur]
}

export function sensDepuisEntier(sens: number): SensMouvement {
  return sens >= 0 ? 'entree' : 'sortie'
}

/**
 * Convertit un `numeric(14,3)` transporté en chaîne en nombre.
 *
 * Le transport en chaîne évite la dérive de virgule flottante ; la conversion
 * en `number` n'intervient qu'ici, au bord de l'application, pour l'affichage
 * et la jauge.
 */
export function quantiteDepuisChaine(valeur: string): number {
  const nombre = Number.parseFloat(valeur)
  return Number.isFinite(nombre) ? nombre : 0
}

export function mapperLigneStock(dto: LigneStockDto, idMagasin: string): LigneStock {
  const seuilMinimal = quantiteDepuisChaine(dto.seuil.seuil_minimal)
  const seuilCritique = quantiteDepuisChaine(dto.seuil.seuil_critique)
  const { seuilMini, seuilConfort } = seuilsVersJauge(seuilMinimal, seuilCritique)

  return {
    idArticle: dto.article.id_article,
    idMagasin,
    idSeuil: dto.seuil.id_seuil,
    code: dto.article.code,
    designation: dto.article.designation,
    codeFamille: dto.article.code_categorie,
    libelleFamille: dto.libelle_famille,
    uniteCode: dto.article.unite_base.code_unite,
    uniteLibelle: dto.article.unite_base.libelle,
    quantite: quantiteDepuisChaine(dto.stock.quantite),
    niveau: niveauDepuisDb(dto.stock.niveau_alerte),
    seuilMini,
    seuilConfort,
    seuilMinimal,
    seuilCritique,
    actif: dto.article.actif,
    codeBarre: dto.article.code_barre,
  }
}

export function mapperMouvement(dto: MouvementStockDto): MouvementStock {
  return {
    uuid: dto.uuid,
    idArticle: dto.article_id_article,
    idMagasin: dto.magasin_id_magasin,
    idLogement: dto.logement_id_logement,
    codeTypeMouvement: dto.type_mouvement_code_type_mouvement,
    sens: sensDepuisEntier(dto.sens),
    quantiteSaisie: quantiteDepuisChaine(dto.quantite_saisie),
    quantiteBase: quantiteDepuisChaine(dto.quantite_base),
    dateOperation: dto.date_operation,
    horodatageServeur: dto.horodatage_serveur,
    statutValidation: statutValidationDepuisDb(dto.statut_validation),
    referenceExterne: dto.reference_externe,
    idAuteur: dto.utilisateur_id_utilisateur,
    nomAuteur: dto.nom_auteur,
    motif: dto.motif,
  }
}

export function mapperTypeMouvement(dto: TypeMouvementDto): TypeMouvement {
  return {
    code: dto.code_type_mouvement,
    libelle: dto.libelle,
    sens: sensDepuisEntier(dto.sens),
    motifObligatoire: dto.motif_obligatoire,
    destinationObligatoire: dto.destination_obligatoire,
  }
}
