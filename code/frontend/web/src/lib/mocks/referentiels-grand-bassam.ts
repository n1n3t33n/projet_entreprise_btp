/*
  Données de démonstration du module référentiels — vue « référentiel » du
  jeu de données commun de Grand-Bassam.

  Corrigé à l'étape 8 : ce fichier ne porte plus son propre univers
  (« Résidence les Palmiers », « Bâtiment A », 13 articles inventés), qui
  contredisait les modules stock et avancement. Comme le ferait le backend, les
  référentiels LISENT ET MODIFIENT les mêmes données que les autres modules :
  - catalogue, familles, unités et magasin pilote : `donnees-grand-bassam` ;
  - zones, types et logements : `avancement-grand-bassam`.
  Une modification faite ici se voit donc dans le stock et l'avancement.

  Seuls les attributs que les deux autres jeux ne portent pas vivent ici
  (surface de référence d'un type de logement, type d'une zone, statut
  administratif d'un logement, date de livraison prévue, activité d'un
  magasin, informations générales du chantier).

  La hiérarchie des familles du module stock (`code_parent`) n'existe pas au
  MPD-3 : le référentiel expose donc les familles feuilles, celles qui portent
  réellement des articles (écart signalé, voir README des modules).
*/

import type {
  ArticleDto,
  CategorieDto,
  ChantierArbreDto,
  ChantierDto,
  LogementDto,
  MagasinDto,
  TypeLogementDto,
  UniteMesureDto,
  ZoneDto,
} from '@/features/referentiels/api/dto'
import type { ArticleDto as ArticleStockDto } from '@/features/stock/api/dto'
import {
  ARTICLES as ARTICLES_STOCK,
  FAMILLES,
  MAGASIN_PILOTE,
  UNITES as UNITES_STOCK,
  unite,
} from '@/lib/mocks/donnees-grand-bassam'
import {
  ajouterLogement,
  logements as LOGEMENTS_AVANCEMENT,
  TYPES_LOGEMENT as TYPES_LOGEMENT_AVANCEMENT,
  ZONES as ZONES_AVANCEMENT,
} from '@/lib/mocks/avancement-grand-bassam'

/* ----------------------------- Génération d'id ---------------------------- */

let compteur = 0

function nouvelId(prefixe: string): string {
  compteur += 1
  return `${prefixe}-R${String(compteur).padStart(3, '0')}`
}

/* ------------------------------- Chantier --------------------------------- */

const CHANTIER: ChantierDto = {
  id_chantier: MAGASIN_PILOTE.id_chantier,
  code: MAGASIN_PILOTE.id_chantier,
  nom: MAGASIN_PILOTE.libelle_chantier,
  programme: 'Programme Grand-Bassam — villas et duplex',
  date_debut: '2026-09-01',
  statut: 'ACTIF',
}

/* -------------------- Attributs propres au référentiel -------------------- */

/** Surface de référence par type de logement (m²), absente du jeu avancement. */
const SURFACE_PAR_TYPE: Record<string, number> = { VILLA3: 95, VILLA4: 120, DUPLEX: 140 }

/** Type de chaque zone (MPD-2 `type_zone`) ; les îlots du pilote sont des tranches. */
const TYPE_ZONE_PAR_ID = new Map<string, string>()

/** Statut administratif et date de livraison prévue de chaque logement. */
const STATUT_LOGEMENT_PAR_ID = new Map<string, string>()
const LIVRAISON_PAR_ID = new Map<string, string | null>()

/** Activité des magasins, et magasins créés au-delà du magasin pilote. */
const ACTIVITE_MAGASIN = new Map<string, boolean>([[MAGASIN_PILOTE.id_magasin, true]])
const MAGASINS_SUPPLEMENTAIRES: { id: string; code: string; nom: string; idChantier: string }[] = []

/** Livraison prévue par défaut : fin de trimestre selon l'îlot. */
function livraisonParDefaut(idZone: string): string {
  if (idZone.endsWith('A')) return '2027-03-31'
  if (idZone.endsWith('B')) return '2027-06-30'
  return '2027-09-30'
}

/* ------------------------------- Conversions ------------------------------ */

function versArticleReferentiel(article: ArticleStockDto): ArticleDto {
  return {
    id_article: article.id_article,
    code: article.code,
    designation: article.designation,
    origine: article.origine,
    code_barre: article.code_barre,
    actif: article.actif,
    categorie_article_code_categorie: article.code_categorie,
    unite_mesure_code_unite: article.unite_base.code_unite,
  }
}

function versZoneReferentiel(zone: (typeof ZONES_AVANCEMENT)[number]): ZoneDto {
  return {
    id_zone: zone.id_zone,
    code: zone.code,
    nom: zone.nom,
    type_zone: TYPE_ZONE_PAR_ID.get(zone.id_zone) ?? 'TRANCHE',
    chantier_id_chantier: zone.id_chantier,
  }
}

function versLogementReferentiel(logement: (typeof LOGEMENTS_AVANCEMENT)[number]): LogementDto {
  return {
    id_logement: logement.idLogement,
    numero: logement.numero,
    statut: STATUT_LOGEMENT_PAR_ID.get(logement.idLogement) ?? 'ACTIF',
    date_livraison_prevue: LIVRAISON_PAR_ID.has(logement.idLogement)
      ? (LIVRAISON_PAR_ID.get(logement.idLogement) ?? null)
      : livraisonParDefaut(logement.idZone),
    zone_id_zone: logement.idZone,
    type_logement_code_type: logement.codeType,
  }
}

/* -------------------------------- Lectures -------------------------------- */

/** Familles feuilles : celles qui portent des articles (MPD-3 : catégories plates). */
export function listerCategories(): CategorieDto[] {
  const parents = new Set(FAMILLES.map((famille) => famille.code_parent).filter(Boolean))
  return FAMILLES.filter((famille) => !parents.has(famille.code_categorie)).map((famille) => ({
    code_categorie: famille.code_categorie,
    libelle: famille.libelle,
  }))
}

export function listerUnites(): UniteMesureDto[] {
  return Object.values(UNITES_STOCK).map((u) => ({
    code_unite: u.code_unite,
    libelle: u.libelle,
    type_unite: u.type_unite.toUpperCase(),
  }))
}

export function listerArticles(): ArticleDto[] {
  return ARTICLES_STOCK.map(versArticleReferentiel)
}

export function listerChantiers(): ChantierDto[] {
  return [CHANTIER]
}

export function listerTypesLogement(): TypeLogementDto[] {
  return Object.entries(TYPES_LOGEMENT_AVANCEMENT).map(([code, libelle]) => ({
    code_type: code,
    libelle,
    surface_reference: (SURFACE_PAR_TYPE[code] ?? 0).toFixed(3),
    actif: true,
  }))
}

export function listerMagasins(): MagasinDto[] {
  const pilote: MagasinDto = {
    id_magasin: MAGASIN_PILOTE.id_magasin,
    code: MAGASIN_PILOTE.code,
    nom: MAGASIN_PILOTE.libelle,
    actif: ACTIVITE_MAGASIN.get(MAGASIN_PILOTE.id_magasin) ?? true,
    chantier_id_chantier: MAGASIN_PILOTE.id_chantier,
    libelle_chantier: CHANTIER.nom,
  }
  const autres = MAGASINS_SUPPLEMENTAIRES.map((magasin) => ({
    id_magasin: magasin.id,
    code: magasin.code,
    nom: magasin.nom,
    actif: ACTIVITE_MAGASIN.get(magasin.id) ?? true,
    chantier_id_chantier: magasin.idChantier,
    libelle_chantier: magasin.idChantier === CHANTIER.id_chantier ? CHANTIER.nom : '',
  }))
  return [pilote, ...autres]
}

export function construireArborescence(idChantier: string): ChantierArbreDto | undefined {
  if (idChantier !== CHANTIER.id_chantier) {
    return undefined
  }
  const zones = ZONES_AVANCEMENT.filter((zone) => zone.id_chantier === idChantier).map((zone) => ({
    zone: versZoneReferentiel(zone),
    logements: LOGEMENTS_AVANCEMENT.filter((l) => l.idZone === zone.id_zone).map(
      versLogementReferentiel,
    ),
  }))
  return { chantier: CHANTIER, zones }
}

/* -------------------------------- Écritures ------------------------------- */

function texte(valeur: unknown): string {
  return typeof valeur === 'string' ? valeur : ''
}

function booleen(valeur: unknown, defaut: boolean): boolean {
  return typeof valeur === 'boolean' ? valeur : defaut
}

function texteOuNul(valeur: unknown): string | null {
  return typeof valeur === 'string' && valeur.length > 0 ? valeur : null
}

export function creerArticleMock(corps: Record<string, unknown>): ArticleDto {
  const article: ArticleStockDto = {
    id_article: nouvelId('ART'),
    code: texte(corps.code),
    designation: texte(corps.designation),
    origine: texte(corps.origine),
    code_barre: texteOuNul(corps.code_barre),
    actif: booleen(corps.actif, true),
    unite_base: unite(texte(corps.unite_mesure_code_unite)),
    code_categorie: texte(corps.categorie_article_code_categorie),
  }
  // Ajouté au catalogue commun : il apparaît aussitôt dans le stock (à zéro).
  ARTICLES_STOCK.push(article)
  return versArticleReferentiel(article)
}

export function modifierArticleMock(
  id: string,
  corps: Record<string, unknown>,
): ArticleDto | undefined {
  const article = ARTICLES_STOCK.find((a) => a.id_article === id)
  if (!article) {
    return undefined
  }
  article.code = texte(corps.code)
  article.designation = texte(corps.designation)
  article.origine = texte(corps.origine)
  article.code_barre = texteOuNul(corps.code_barre)
  article.actif = booleen(corps.actif, article.actif)
  article.code_categorie = texte(corps.categorie_article_code_categorie)
  article.unite_base = unite(texte(corps.unite_mesure_code_unite))
  return versArticleReferentiel(article)
}

export function creerMagasinMock(corps: Record<string, unknown>): MagasinDto | undefined {
  const id = nouvelId('MAG')
  MAGASINS_SUPPLEMENTAIRES.push({
    id,
    code: texte(corps.code),
    nom: texte(corps.nom),
    idChantier: texte(corps.chantier_id_chantier),
  })
  ACTIVITE_MAGASIN.set(id, booleen(corps.actif, true))
  return listerMagasins().find((m) => m.id_magasin === id)
}

export function modifierMagasinMock(
  id: string,
  corps: Record<string, unknown>,
): MagasinDto | undefined {
  if (id === MAGASIN_PILOTE.id_magasin) {
    MAGASIN_PILOTE.code = texte(corps.code)
    MAGASIN_PILOTE.libelle = texte(corps.nom)
  } else {
    const magasin = MAGASINS_SUPPLEMENTAIRES.find((m) => m.id === id)
    if (!magasin) {
      return undefined
    }
    magasin.code = texte(corps.code)
    magasin.nom = texte(corps.nom)
    magasin.idChantier = texte(corps.chantier_id_chantier)
  }
  ACTIVITE_MAGASIN.set(id, booleen(corps.actif, true))
  return listerMagasins().find((m) => m.id_magasin === id)
}

export function modifierChantierMock(
  id: string,
  corps: Record<string, unknown>,
): ChantierDto | undefined {
  if (id !== CHANTIER.id_chantier) {
    return undefined
  }
  CHANTIER.code = texte(corps.code)
  CHANTIER.nom = texte(corps.nom)
  CHANTIER.programme = texte(corps.programme)
  CHANTIER.date_debut = texte(corps.date_debut)
  CHANTIER.statut = texte(corps.statut)
  // Le nom du chantier est aussi celui affiché par le module stock.
  MAGASIN_PILOTE.libelle_chantier = CHANTIER.nom
  return CHANTIER
}

export function creerZoneMock(corps: Record<string, unknown>): ZoneDto {
  const zone = {
    id_zone: nouvelId('ZON'),
    code: texte(corps.code),
    nom: texte(corps.nom),
    id_chantier: texte(corps.chantier_id_chantier),
  }
  ZONES_AVANCEMENT.push(zone)
  TYPE_ZONE_PAR_ID.set(zone.id_zone, texte(corps.type_zone))
  return versZoneReferentiel(zone)
}

export function modifierZoneMock(id: string, corps: Record<string, unknown>): ZoneDto | undefined {
  const zone = ZONES_AVANCEMENT.find((z) => z.id_zone === id)
  if (!zone) {
    return undefined
  }
  zone.code = texte(corps.code)
  zone.nom = texte(corps.nom)
  TYPE_ZONE_PAR_ID.set(id, texte(corps.type_zone))
  return versZoneReferentiel(zone)
}

export function creerLogementMock(corps: Record<string, unknown>): LogementDto {
  const idLogement = nouvelId('LOG')
  ajouterLogement({
    idLogement,
    numero: texte(corps.numero),
    idZone: texte(corps.zone_id_zone),
    codeType: texte(corps.type_logement_code_type),
    statut: 'A_VENIR',
  })
  STATUT_LOGEMENT_PAR_ID.set(idLogement, texte(corps.statut))
  LIVRAISON_PAR_ID.set(idLogement, texteOuNul(corps.date_livraison_prevue))
  const cree = LOGEMENTS_AVANCEMENT.find((l) => l.idLogement === idLogement)
  return versLogementReferentiel(cree!)
}

export function modifierLogementMock(
  id: string,
  corps: Record<string, unknown>,
): LogementDto | undefined {
  const logement = LOGEMENTS_AVANCEMENT.find((l) => l.idLogement === id)
  if (!logement) {
    return undefined
  }
  logement.numero = texte(corps.numero)
  logement.idZone = texte(corps.zone_id_zone)
  logement.codeType = texte(corps.type_logement_code_type)
  STATUT_LOGEMENT_PAR_ID.set(id, texte(corps.statut))
  LIVRAISON_PAR_ID.set(id, texteOuNul(corps.date_livraison_prevue))
  return versLogementReferentiel(logement)
}
