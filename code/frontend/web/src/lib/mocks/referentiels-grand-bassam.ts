/*
  Données de démonstration du module référentiels — chantier pilote de
  Grand-Bassam. Les formes sont des `dto` (schéma physique) ; l'adaptateur les
  sert telles quelles, comme le ferait l'API Django.

  Les tableaux sont modifiés sur place par les créations et modifications, pour
  qu'une saisie faite à l'écran se voie immédiatement au rechargement de la
  liste. Cet état vit en mémoire, le temps de la session : il n'est pas partagé
  avec les jeux de données des modules stock et avancement (en production, un
  seul schéma les réunit).
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

/* ----------------------------- Génération d'id ---------------------------- */

let compteur = 0

/** Identifiant lisible et unique le temps de la session (ex. « art-7 »). */
function nouvelId(prefixe: string): string {
  compteur += 1
  return `${prefixe}-${compteur}`
}

/* ------------------------------- Catalogue -------------------------------- */

const CATEGORIES: CategorieDto[] = [
  { code_categorie: 'GO', libelle: 'Gros œuvre' },
  { code_categorie: 'SO', libelle: 'Second œuvre' },
  { code_categorie: 'PLOMB', libelle: 'Plomberie' },
  { code_categorie: 'ELEC', libelle: 'Électricité' },
  { code_categorie: 'FINITION', libelle: 'Finitions' },
]

const UNITES: UniteMesureDto[] = [
  { code_unite: 'U', libelle: 'Unité', type_unite: 'UNITE' },
  { code_unite: 'SAC', libelle: 'Sac', type_unite: 'UNITE' },
  { code_unite: 'KG', libelle: 'Kilogramme', type_unite: 'MASSE' },
  { code_unite: 'T', libelle: 'Tonne', type_unite: 'MASSE' },
  { code_unite: 'M3', libelle: 'Mètre cube', type_unite: 'VOLUME' },
  { code_unite: 'L', libelle: 'Litre', type_unite: 'VOLUME' },
  { code_unite: 'ML', libelle: 'Mètre linéaire', type_unite: 'LONGUEUR' },
  { code_unite: 'M2', libelle: 'Mètre carré', type_unite: 'SURFACE' },
]

const ARTICLES: ArticleDto[] = [
  art('CIM-42', 'Ciment CPJ 42,5 — sac 50 kg', 'ACHAT', '3012345000018', 'GO', 'SAC'),
  art('SAB-01', 'Sable lavé 0/5', 'ACHAT', null, 'GO', 'M3'),
  art('GRAV-01', 'Gravier 5/15', 'ACHAT', null, 'GO', 'M3'),
  art('FER-12', 'Fer à béton HA 12 mm', 'ACHAT', '3012345000025', 'GO', 'ML'),
  art('PARP-20', 'Parpaing creux 20', 'ACHAT', '3012345000032', 'GO', 'U'),
  art('CARR-60', 'Carrelage grès 60×60', 'ACHAT', '3012345000049', 'FINITION', 'M2'),
  art('PEINT-ACR', 'Peinture acrylique blanche', 'ACHAT', null, 'FINITION', 'L'),
  art('TUBE-PVC', 'Tube PVC Ø100', 'ACHAT', null, 'PLOMB', 'ML'),
  art('COUDE-PVC', 'Coude PVC Ø100 87°', 'ACHAT', '3012345000063', 'PLOMB', 'U'),
  art('CABLE-25', 'Câble U-1000 R2V 3G2,5', 'ACHAT', null, 'ELEC', 'ML'),
  art('DISJ-16', 'Disjoncteur 16 A', 'ACHAT', '3012345000087', 'ELEC', 'U'),
  art('MENUIS-INT', 'Bloc-porte intérieur (atelier)', 'PRODUCTION_INTERNE', null, 'SO', 'U'),
  { ...art('MORT-REC', 'Mortier reconditionné', 'RECUPERATION', null, 'SO', 'SAC'), actif: false },
]

/** Fabrique un article actif avec un identifiant généré. */
function art(
  code: string,
  designation: string,
  origine: string,
  codeBarre: string | null,
  categorie: string,
  unite: string,
): ArticleDto {
  return {
    id_article: nouvelId('art'),
    code,
    designation,
    origine,
    code_barre: codeBarre,
    actif: true,
    categorie_article_code_categorie: categorie,
    unite_mesure_code_unite: unite,
  }
}

/* -------------------------- Structure du chantier ------------------------- */

const CHANTIERS: ChantierDto[] = [
  {
    id_chantier: 'ch-gb',
    code: 'CH-GB',
    nom: 'Résidence les Palmiers',
    programme: 'Grand-Bassam — Tranche 1',
    date_debut: '2025-01-15',
    statut: 'ACTIF',
  },
]

const ZONES: ZoneDto[] = [
  { id_zone: 'zn-a', code: 'BAT-A', nom: 'Bâtiment A', type_zone: 'BATIMENT', chantier_id_chantier: 'ch-gb' },
  { id_zone: 'zn-b', code: 'BAT-B', nom: 'Bâtiment B', type_zone: 'BATIMENT', chantier_id_chantier: 'ch-gb' },
  { id_zone: 'zn-t2', code: 'TR-2', nom: 'Tranche 2', type_zone: 'TRANCHE', chantier_id_chantier: 'ch-gb' },
]

const TYPES_LOGEMENT: TypeLogementDto[] = [
  { code_type: 'T2', libelle: 'Logement T2', surface_reference: '45.000', actif: true },
  { code_type: 'T3', libelle: 'Logement T3', surface_reference: '68.000', actif: true },
  { code_type: 'T4', libelle: 'Logement T4', surface_reference: '85.000', actif: true },
  { code_type: 'VIL', libelle: 'Villa', surface_reference: '120.000', actif: true },
]

const LOGEMENTS: LogementDto[] = [
  log('A-101', 'zn-a', 'T2', '2026-03-31'),
  log('A-102', 'zn-a', 'T3', '2026-03-31'),
  log('A-103', 'zn-a', 'T3', '2026-06-30'),
  log('B-201', 'zn-b', 'T4', '2026-09-30'),
  log('B-202', 'zn-b', 'T4', '2026-09-30'),
  log('B-203', 'zn-b', 'VIL', null),
]

/** Fabrique un logement actif avec un identifiant généré. */
function log(
  numero: string,
  idZone: string,
  codeType: string,
  livraison: string | null,
): LogementDto {
  return {
    id_logement: nouvelId('log'),
    numero,
    statut: 'ACTIF',
    date_livraison_prevue: livraison,
    zone_id_zone: idZone,
    type_logement_code_type: codeType,
  }
}

/* -------------------------------- Magasins -------------------------------- */

const MAGASINS: MagasinDto[] = [
  {
    id_magasin: 'mag-gb',
    code: 'MAG-GB',
    nom: 'Magasin central',
    actif: true,
    chantier_id_chantier: 'ch-gb',
    libelle_chantier: '',
  },
  {
    id_magasin: 'mag-a2',
    code: 'MAG-A2',
    nom: 'Dépôt Bâtiment A',
    actif: false,
    chantier_id_chantier: 'ch-gb',
    libelle_chantier: '',
  },
]

/* ------------------------------ Lectures ---------------------------------- */

export function listerCategories(): CategorieDto[] {
  return CATEGORIES
}

export function listerUnites(): UniteMesureDto[] {
  return UNITES
}

export function listerArticles(): ArticleDto[] {
  return ARTICLES
}

export function listerChantiers(): ChantierDto[] {
  return CHANTIERS
}

export function listerTypesLogement(): TypeLogementDto[] {
  return TYPES_LOGEMENT
}

/** Magasins avec le nom de leur chantier résolu au moment de l'appel. */
export function listerMagasins(): MagasinDto[] {
  return MAGASINS.map((magasin) => ({
    ...magasin,
    libelle_chantier:
      CHANTIERS.find((c) => c.id_chantier === magasin.chantier_id_chantier)?.nom ?? '',
  }))
}

/** Arbre d'un chantier : ses zones, et les logements de chaque zone. */
export function construireArborescence(idChantier: string): ChantierArbreDto | undefined {
  const chantier = CHANTIERS.find((c) => c.id_chantier === idChantier)
  if (!chantier) {
    return undefined
  }

  const zones = ZONES.filter((zone) => zone.chantier_id_chantier === idChantier).map((zone) => ({
    zone,
    logements: LOGEMENTS.filter((logement) => logement.zone_id_zone === zone.id_zone),
  }))

  return { chantier, zones }
}

/* ------------------------------ Écritures --------------------------------- */

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
  const article: ArticleDto = {
    id_article: nouvelId('art'),
    code: texte(corps.code),
    designation: texte(corps.designation),
    origine: texte(corps.origine),
    code_barre: texteOuNul(corps.code_barre),
    actif: booleen(corps.actif, true),
    categorie_article_code_categorie: texte(corps.categorie_article_code_categorie),
    unite_mesure_code_unite: texte(corps.unite_mesure_code_unite),
  }
  ARTICLES.push(article)
  return article
}

export function modifierArticleMock(id: string, corps: Record<string, unknown>): ArticleDto | undefined {
  const article = ARTICLES.find((a) => a.id_article === id)
  if (!article) {
    return undefined
  }
  article.code = texte(corps.code)
  article.designation = texte(corps.designation)
  article.origine = texte(corps.origine)
  article.code_barre = texteOuNul(corps.code_barre)
  article.actif = booleen(corps.actif, article.actif)
  article.categorie_article_code_categorie = texte(corps.categorie_article_code_categorie)
  article.unite_mesure_code_unite = texte(corps.unite_mesure_code_unite)
  return article
}

export function creerMagasinMock(corps: Record<string, unknown>): MagasinDto {
  const magasin: MagasinDto = {
    id_magasin: nouvelId('mag'),
    code: texte(corps.code),
    nom: texte(corps.nom),
    actif: booleen(corps.actif, true),
    chantier_id_chantier: texte(corps.chantier_id_chantier),
    libelle_chantier: '',
  }
  MAGASINS.push(magasin)
  return magasin
}

export function modifierMagasinMock(id: string, corps: Record<string, unknown>): MagasinDto | undefined {
  const magasin = MAGASINS.find((m) => m.id_magasin === id)
  if (!magasin) {
    return undefined
  }
  magasin.code = texte(corps.code)
  magasin.nom = texte(corps.nom)
  magasin.actif = booleen(corps.actif, magasin.actif)
  magasin.chantier_id_chantier = texte(corps.chantier_id_chantier)
  return magasin
}

export function modifierChantierMock(id: string, corps: Record<string, unknown>): ChantierDto | undefined {
  const chantier = CHANTIERS.find((c) => c.id_chantier === id)
  if (!chantier) {
    return undefined
  }
  chantier.code = texte(corps.code)
  chantier.nom = texte(corps.nom)
  chantier.programme = texte(corps.programme)
  chantier.date_debut = texte(corps.date_debut)
  chantier.statut = texte(corps.statut)
  return chantier
}

export function creerZoneMock(corps: Record<string, unknown>): ZoneDto {
  const zone: ZoneDto = {
    id_zone: nouvelId('zn'),
    code: texte(corps.code),
    nom: texte(corps.nom),
    type_zone: texte(corps.type_zone),
    chantier_id_chantier: texte(corps.chantier_id_chantier),
  }
  ZONES.push(zone)
  return zone
}

export function modifierZoneMock(id: string, corps: Record<string, unknown>): ZoneDto | undefined {
  const zone = ZONES.find((z) => z.id_zone === id)
  if (!zone) {
    return undefined
  }
  zone.code = texte(corps.code)
  zone.nom = texte(corps.nom)
  zone.type_zone = texte(corps.type_zone)
  zone.chantier_id_chantier = texte(corps.chantier_id_chantier)
  return zone
}

export function creerLogementMock(corps: Record<string, unknown>): LogementDto {
  const logement: LogementDto = {
    id_logement: nouvelId('log'),
    numero: texte(corps.numero),
    statut: texte(corps.statut),
    date_livraison_prevue: texteOuNul(corps.date_livraison_prevue),
    zone_id_zone: texte(corps.zone_id_zone),
    type_logement_code_type: texte(corps.type_logement_code_type),
  }
  LOGEMENTS.push(logement)
  return logement
}

export function modifierLogementMock(id: string, corps: Record<string, unknown>): LogementDto | undefined {
  const logement = LOGEMENTS.find((l) => l.id_logement === id)
  if (!logement) {
    return undefined
  }
  logement.numero = texte(corps.numero)
  logement.statut = texte(corps.statut)
  logement.date_livraison_prevue = texteOuNul(corps.date_livraison_prevue)
  logement.zone_id_zone = texte(corps.zone_id_zone)
  logement.type_logement_code_type = texte(corps.type_logement_code_type)
  return logement
}
