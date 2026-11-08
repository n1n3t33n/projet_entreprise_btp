/*
  Données de démonstration du magasin pilote de Grand-Bassam.

  Un seul magasin (le pilote est mono-magasin), une soixantaine de références
  BTP réparties en familles, avec des seuils et des quantités couvrant les
  quatre niveaux — dont une référence en stock négatif, pour illustrer
  l'anomalie signalée mais non bloquante de la charte.

  Ces données imitent la forme servie par l'API (dto, snake_case) : l'adaptateur
  les renvoie telles quelles, de sorte que passer aux vraies routes ne change
  rien en aval. L'état vit en mémoire le temps de la session : une saisie met à
  jour le stock et l'historique comme le ferait le serveur.
*/

import { calculerNiveauSeuil, type NiveauSeuil } from '@/lib/seuils'
import type { NoeudStock } from '@/features/stock/types'
import type {
  ArticleDto,
  FamilleDto,
  LigneStockDto,
  MagasinDto,
  MouvementStockDto,
  NiveauAlerteDb,
  TypeMouvementDto,
  UniteMesureDto,
} from '@/features/stock/api/dto'

export const ID_MAGASIN_PILOTE = 'MAG-GB-01'

export const MAGASIN_PILOTE: MagasinDto = {
  id_magasin: ID_MAGASIN_PILOTE,
  code: 'GB-CENTRAL',
  libelle: 'Magasin central',
  id_chantier: 'CH-GB',
  libelle_chantier: 'Chantier de Grand-Bassam',
}

export const FAMILLES: FamilleDto[] = [
  { code_categorie: 'GO', libelle: 'Gros œuvre', code_parent: null },
  { code_categorie: 'GO-CIM', libelle: 'Ciment & liants', code_parent: 'GO' },
  { code_categorie: 'GO-ACI', libelle: 'Aciers & treillis', code_parent: 'GO' },
  { code_categorie: 'GO-AGR', libelle: 'Agrégats', code_parent: 'GO' },
  { code_categorie: 'SO', libelle: 'Second œuvre', code_parent: null },
  { code_categorie: 'SO-MAC', libelle: 'Maçonnerie & cloisons', code_parent: 'SO' },
  { code_categorie: 'SO-MEN', libelle: 'Menuiserie', code_parent: 'SO' },
  { code_categorie: 'EL', libelle: 'Électricité', code_parent: null },
  { code_categorie: 'PL', libelle: 'Plomberie', code_parent: null },
  { code_categorie: 'FIN', libelle: 'Finitions', code_parent: null },
  { code_categorie: 'OUT', libelle: 'Outillage & EPI', code_parent: null },
]

const UNITES: Record<string, UniteMesureDto> = {
  U: { code_unite: 'U', libelle: 'unité', type_unite: 'unite' },
  SAC: { code_unite: 'SAC', libelle: 'sac', type_unite: 'masse' },
  KG: { code_unite: 'KG', libelle: 'kg', type_unite: 'masse' },
  T: { code_unite: 'T', libelle: 'tonne', type_unite: 'masse' },
  M3: { code_unite: 'M3', libelle: 'm³', type_unite: 'volume' },
  M2: { code_unite: 'M2', libelle: 'm²', type_unite: 'surface' },
  ML: { code_unite: 'ML', libelle: 'ml', type_unite: 'longueur' },
  L: { code_unite: 'L', libelle: 'litre', type_unite: 'volume' },
  BTE: { code_unite: 'BTE', libelle: 'boîte', type_unite: 'unite' },
  ROUL: { code_unite: 'ROUL', libelle: 'rouleau', type_unite: 'unite' },
}

function unite(code: string): UniteMesureDto {
  return UNITES[code] ?? UNITES.U!
}

export const TYPES_MOUVEMENT: TypeMouvementDto[] = [
  {
    code_type_mouvement: 'ENT_RECEPTION',
    libelle: 'Réception',
    sens: 1,
    motif_obligatoire: false,
    destination_obligatoire: false,
  },
  {
    code_type_mouvement: 'SOR_LOGEMENT',
    libelle: 'Sortie vers un logement',
    sens: -1,
    motif_obligatoire: false,
    destination_obligatoire: true,
  },
  {
    code_type_mouvement: 'RET_RETOUR',
    libelle: 'Retour au magasin',
    sens: 1,
    motif_obligatoire: true,
    destination_obligatoire: false,
  },
  {
    code_type_mouvement: 'SOR_PERTE',
    libelle: 'Perte ou casse',
    sens: -1,
    motif_obligatoire: true,
    destination_obligatoire: false,
  },
]

/** Catalogue de référence : désignation, famille (feuille), unité de base. */
const CATALOGUE: ReadonlyArray<{ designation: string; famille: string; unite: string }> = [
  { designation: 'Ciment CPJ 42.5 — sac 50 kg', famille: 'GO-CIM', unite: 'SAC' },
  { designation: 'Ciment CPA 32.5 — sac 50 kg', famille: 'GO-CIM', unite: 'SAC' },
  { designation: 'Chaux hydraulique — sac 25 kg', famille: 'GO-CIM', unite: 'SAC' },
  { designation: 'Plâtre de construction — sac 25 kg', famille: 'GO-CIM', unite: 'SAC' },
  { designation: 'Mortier colle — sac 25 kg', famille: 'GO-CIM', unite: 'SAC' },
  { designation: 'Fer à béton HA 8 mm', famille: 'GO-ACI', unite: 'ML' },
  { designation: 'Fer à béton HA 10 mm', famille: 'GO-ACI', unite: 'ML' },
  { designation: 'Fer à béton HA 12 mm', famille: 'GO-ACI', unite: 'ML' },
  { designation: 'Fer à béton HA 14 mm', famille: 'GO-ACI', unite: 'ML' },
  { designation: 'Treillis soudé ST25', famille: 'GO-ACI', unite: 'M2' },
  { designation: "Fil d'attache recuit", famille: 'GO-ACI', unite: 'KG' },
  { designation: 'Sable de rivière lavé', famille: 'GO-AGR', unite: 'M3' },
  { designation: 'Sable de carrière', famille: 'GO-AGR', unite: 'M3' },
  { designation: 'Gravier 5/15', famille: 'GO-AGR', unite: 'M3' },
  { designation: 'Gravier 15/25', famille: 'GO-AGR', unite: 'M3' },
  { designation: 'Latérite', famille: 'GO-AGR', unite: 'M3' },
  { designation: 'Parpaing creux 15', famille: 'SO-MAC', unite: 'U' },
  { designation: 'Parpaing creux 20', famille: 'SO-MAC', unite: 'U' },
  { designation: 'Brique pleine terre cuite', famille: 'SO-MAC', unite: 'U' },
  { designation: 'Plaque de plâtre BA13', famille: 'SO-MAC', unite: 'U' },
  { designation: 'Rail métallique 48', famille: 'SO-MAC', unite: 'ML' },
  { designation: 'Montant métallique 48', famille: 'SO-MAC', unite: 'ML' },
  { designation: 'Bloc-porte intérieur 83', famille: 'SO-MEN', unite: 'U' },
  { designation: 'Bloc-porte intérieur 73', famille: 'SO-MEN', unite: 'U' },
  { designation: "Fenêtre aluminium 120x100", famille: 'SO-MEN', unite: 'U' },
  { designation: 'Chevron sapin 63x75', famille: 'SO-MEN', unite: 'ML' },
  { designation: 'Contreplaqué 15 mm', famille: 'SO-MEN', unite: 'M2' },
  { designation: 'Câble U1000 R2V 3G2.5', famille: 'EL', unite: 'ML' },
  { designation: 'Câble U1000 R2V 3G1.5', famille: 'EL', unite: 'ML' },
  { designation: 'Gaine ICTA Ø20', famille: 'EL', unite: 'ML' },
  { designation: 'Interrupteur simple', famille: 'EL', unite: 'U' },
  { designation: 'Prise 2P+T 16 A', famille: 'EL', unite: 'U' },
  { designation: 'Disjoncteur 16 A', famille: 'EL', unite: 'U' },
  { designation: 'Disjoncteur 20 A', famille: 'EL', unite: 'U' },
  { designation: 'Tableau 2 rangées', famille: 'EL', unite: 'U' },
  { designation: 'Boîte de dérivation', famille: 'EL', unite: 'BTE' },
  { designation: 'Tube PVC évacuation Ø100', famille: 'PL', unite: 'ML' },
  { designation: 'Tube PVC évacuation Ø40', famille: 'PL', unite: 'ML' },
  { designation: 'Tube PER Ø16', famille: 'PL', unite: 'ML' },
  { designation: 'Coude PVC 100 — 87°', famille: 'PL', unite: 'U' },
  { designation: 'Siphon de sol', famille: 'PL', unite: 'U' },
  { designation: 'Robinet d’arrêt 1/2"', famille: 'PL', unite: 'U' },
  { designation: 'WC à poser complet', famille: 'PL', unite: 'U' },
  { designation: 'Lavabo céramique', famille: 'PL', unite: 'U' },
  { designation: 'Enduit de façade — sac 25 kg', famille: 'FIN', unite: 'SAC' },
  { designation: 'Peinture acrylique blanche', famille: 'FIN', unite: 'L' },
  { designation: 'Peinture glycéro', famille: 'FIN', unite: 'L' },
  { designation: 'Carrelage grès 60x60', famille: 'FIN', unite: 'M2' },
  { designation: 'Faïence murale 25x40', famille: 'FIN', unite: 'M2' },
  { designation: 'Colle à carrelage — sac 25 kg', famille: 'FIN', unite: 'SAC' },
  { designation: 'Joint de carrelage', famille: 'FIN', unite: 'KG' },
  { designation: 'Rouleau d’étanchéité', famille: 'FIN', unite: 'ROUL' },
  { designation: 'Brouette chantier 100 L', famille: 'OUT', unite: 'U' },
  { designation: 'Truelle langue de chat', famille: 'OUT', unite: 'U' },
  { designation: 'Niveau à bulle 60 cm', famille: 'OUT', unite: 'U' },
  { designation: 'Disque à tronçonner Ø230', famille: 'OUT', unite: 'U' },
  { designation: 'Casque de chantier', famille: 'OUT', unite: 'U' },
  { designation: 'Paire de gants de protection', famille: 'OUT', unite: 'U' },
  { designation: 'Gilet haute visibilité', famille: 'OUT', unite: 'U' },
  { designation: 'Chaussures de sécurité', famille: 'OUT', unite: 'U' },
]

/** Échelle de seuils indicative par unité, pour des données crédibles. */
const ECHELLE_SEUIL: Record<string, { minimal: number; critique: number }> = {
  SAC: { minimal: 80, critique: 30 },
  KG: { minimal: 150, critique: 50 },
  T: { minimal: 20, critique: 6 },
  M3: { minimal: 40, critique: 12 },
  M2: { minimal: 120, critique: 40 },
  ML: { minimal: 300, critique: 100 },
  L: { minimal: 60, critique: 20 },
  U: { minimal: 60, critique: 20 },
  BTE: { minimal: 25, critique: 8 },
  ROUL: { minimal: 18, critique: 5 },
}

function echelle(codeUnite: string): { minimal: number; critique: number } {
  return ECHELLE_SEUIL[codeUnite] ?? ECHELLE_SEUIL.U!
}

/** Quantité initiale choisie pour tomber dans un niveau donné (bande 0..6). */
function quantiteInitiale(minimal: number, critique: number, bande: number): number {
  switch (bande) {
    case 0:
      return 0 // vide
    case 6:
      return -Math.round(critique * 0.2) // anomalie : stock négatif
    case 1:
      return Math.round(critique * 0.5) // critique
    case 2:
      return Math.round(critique + (minimal - critique) * 0.4) // mini
    case 3:
      return Math.round(minimal + minimal * 0.6) // plein
    case 4:
      return Math.round(minimal * 2.2) // plein confortable
    default:
      return Math.round(minimal + minimal * 0.1) // plein, juste au-dessus
  }
}

type EnregistrementStock = {
  idSeuil: string
  seuilMinimal: number
  seuilCritique: number
  quantite: number
  dateCalcul: string
}

/** Articles construits une fois, figés pour la session. */
export const ARTICLES: ArticleDto[] = CATALOGUE.map((entree, index) => {
  const numero = String(index + 1).padStart(4, '0')
  return {
    id_article: `ART-${numero}`,
    code: `A${numero}`,
    designation: entree.designation,
    origine: index % 5 === 0 ? 'import' : 'local',
    code_barre: String(6_000_000_000_000 + index * 137),
    actif: true,
    unite_base: unite(entree.unite),
    code_categorie: entree.famille,
  }
})

const DATE_CALCUL = '2026-11-05T08:00:00.000Z'

/** État de stock par article, mutable le temps de la session. */
const stockParArticle = new Map<string, EnregistrementStock>(
  CATALOGUE.map((entree, index) => {
    const numero = String(index + 1).padStart(4, '0')
    const idArticle = `ART-${numero}`
    const { minimal, critique } = echelle(entree.unite)
    const bande = index % 7
    return [
      idArticle,
      {
        idSeuil: `SEU-${numero}`,
        seuilMinimal: minimal,
        seuilCritique: critique,
        quantite: quantiteInitiale(minimal, critique, bande),
        dateCalcul: DATE_CALCUL,
      },
    ]
  }),
)

/** Mouvements, du plus récent au plus ancien, alimentés par les saisies. */
const mouvements: MouvementStockDto[] = []
let compteurMouvement = 0

const NIVEAU_VERS_DB: Record<NiveauSeuil, NiveauAlerteDb> = {
  vide: 'VIDE',
  critique: 'CRITIQUE',
  mini: 'MINIMAL',
  plein: 'NORMAL',
}

/**
 * Niveau servi par le serveur, calculé avec la même règle que la jauge et la
 * correspondance croisée des seuils (seuilMini ← critique, seuilConfort ←
 * minimal).
 */
function niveauDb(enregistrement: EnregistrementStock): NiveauAlerteDb {
  const niveau = calculerNiveauSeuil({
    valeur: enregistrement.quantite,
    seuilMini: enregistrement.seuilCritique,
    seuilConfort: enregistrement.seuilMinimal,
  })
  return NIVEAU_VERS_DB[niveau]
}

function libelleFamille(codeFamille: string): string {
  return FAMILLES.find((famille) => famille.code_categorie === codeFamille)?.libelle ?? codeFamille
}

/** Lignes de stock du magasin (jointure article + seuil + état courant). */
export function construireLignesStock(): LigneStockDto[] {
  return ARTICLES.map((article) => {
    const etat = stockParArticle.get(article.id_article)
    const enregistrement: EnregistrementStock = etat ?? {
      idSeuil: `SEU-${article.id_article}`,
      seuilMinimal: 0,
      seuilCritique: 0,
      quantite: 0,
      dateCalcul: DATE_CALCUL,
    }
    return {
      article,
      libelle_famille: libelleFamille(article.code_categorie),
      seuil: {
        id_seuil: enregistrement.idSeuil,
        seuil_minimal: enregistrement.seuilMinimal.toFixed(3),
        seuil_critique: enregistrement.seuilCritique.toFixed(3),
        actif: true,
      },
      stock: {
        quantite: enregistrement.quantite.toFixed(3),
        date_calcul: enregistrement.dateCalcul,
        niveau_alerte: niveauDb(enregistrement),
      },
    }
  })
}

export function listerMouvementsArticle(idArticle: string): MouvementStockDto[] {
  return mouvements.filter((mouvement) => mouvement.article_id_article === idArticle)
}

export type EntreeMouvementMock = {
  article_id_article: string
  magasin_id_magasin: string
  type_mouvement_code_type_mouvement: string
  quantite_saisie: string
  logement_id_logement?: string | null
  reference_externe?: string | null
  motif?: string | null
}

/** Applique un mouvement : met à jour le stock et journalise. */
export function appliquerMouvement(entree: EntreeMouvementMock): MouvementStockDto {
  const type = TYPES_MOUVEMENT.find(
    (candidat) => candidat.code_type_mouvement === entree.type_mouvement_code_type_mouvement,
  )
  const sens = type?.sens ?? 1
  const quantite = Number.parseFloat(entree.quantite_saisie) || 0
  const delta = sens >= 0 ? quantite : -quantite

  const etat = stockParArticle.get(entree.article_id_article)
  if (etat) {
    etat.quantite = etat.quantite + delta
    etat.dateCalcul = new Date().toISOString()
  }

  compteurMouvement += 1
  const horodatage = new Date().toISOString()
  const mouvement: MouvementStockDto = {
    uuid: `MVT-${String(compteurMouvement).padStart(5, '0')}`,
    article_id_article: entree.article_id_article,
    magasin_id_magasin: entree.magasin_id_magasin,
    logement_id_logement: entree.logement_id_logement ?? null,
    type_mouvement_code_type_mouvement: entree.type_mouvement_code_type_mouvement,
    sens,
    quantite_saisie: quantite.toFixed(3),
    quantite_base: quantite.toFixed(3),
    date_operation: horodatage,
    horodatage_serveur: horodatage,
    // Un mouvement arrive « enregistré » ; la mise en validation éventuelle est
    // décidée côté serveur par les règles de validation, hors de ce pilote.
    statut_validation: 'ENREGISTRE',
    reference_externe: entree.reference_externe ?? null,
    utilisateur_id_utilisateur: 'U-PILOTE',
    nom_auteur: 'Compte de démonstration',
    motif: entree.motif ?? null,
  }
  mouvements.unshift(mouvement)
  return mouvement
}

export function definirSeuilsMock(
  idArticle: string,
  seuilMinimal: number,
  seuilCritique: number,
): void {
  const etat = stockParArticle.get(idArticle)
  if (etat) {
    etat.seuilMinimal = seuilMinimal
    etat.seuilCritique = seuilCritique
    etat.dateCalcul = new Date().toISOString()
  }
}

/** Arborescence chantier → magasin + familles (hiérarchie des catégories). */
export function construireArborescence(): NoeudStock[] {
  const lignes = construireLignesStock()
  const compteParFamille = new Map<string, number>()
  for (const ligne of lignes) {
    const code = ligne.article.code_categorie
    compteParFamille.set(code, (compteParFamille.get(code) ?? 0) + 1)
  }

  function noeudFamille(famille: FamilleDto): NoeudStock {
    const enfants = FAMILLES.filter((f) => f.code_parent === famille.code_categorie).map(
      noeudFamille,
    )
    const propre = compteParFamille.get(famille.code_categorie) ?? 0
    const total = enfants.reduce((somme, enfant) => somme + (enfant.nombreArticles ?? 0), propre)
    return {
      id: `fam-${famille.code_categorie}`,
      libelle: famille.libelle,
      type: 'famille',
      nombreArticles: total,
      enfants,
    }
  }

  const famillesRacines = FAMILLES.filter((famille) => famille.code_parent === null).map(
    noeudFamille,
  )

  return [
    {
      id: `ch-${MAGASIN_PILOTE.id_chantier}`,
      libelle: MAGASIN_PILOTE.libelle_chantier,
      type: 'chantier',
      enfants: [
        {
          id: `mag-${MAGASIN_PILOTE.id_magasin}`,
          libelle: MAGASIN_PILOTE.libelle,
          type: 'magasin',
          nombreArticles: lignes.length,
          enfants: famillesRacines,
        },
      ],
    },
  ]
}
