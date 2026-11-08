/*
  Conversion des formes servies par l'API (dto, schéma physique) vers les types
  du domaine utilisés par les écrans, et conversion inverse des énumérés pour
  les charges utiles de création et de modification.

  Les énumérés `UPPER_SNAKE` de la base deviennent des valeurs minuscules du
  domaine, et réciproquement. Une valeur inconnue est repliée sur une valeur par
  défaut sûre plutôt que de faire échouer tout un écran : le cas est rare
  (donnée hors contrat) et ne doit pas masquer le reste de la liste.
*/

import type {
  Article,
  Categorie,
  Chantier,
  Logement,
  TypeLogement,
  UniteMesure,
  Zone,
} from '@/features/referentiels/types/domaine'
import type {
  OrigineArticle,
  StatutChantier,
  StatutLogement,
  TypeUnite,
  TypeZone,
} from '@/features/referentiels/types/enums'
import type {
  ArticleVue,
  ChantierArbre,
  LogementVue,
  MagasinVue,
  SaisieArticle,
  SaisieChantier,
  SaisieLogement,
  SaisieMagasin,
  SaisieZone,
  ZoneArbre,
} from '@/features/referentiels/types/vues'
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

/* --------------------------- Énumérés : base → app ------------------------ */

const ORIGINE_DEPUIS_DB: Record<string, OrigineArticle> = {
  ACHAT: 'achat',
  PRODUCTION_INTERNE: 'production_interne',
  RECUPERATION: 'recuperation',
}

export function origineDepuisDb(valeur: string): OrigineArticle {
  return ORIGINE_DEPUIS_DB[valeur] ?? 'achat'
}

const TYPE_UNITE_DEPUIS_DB: Record<string, TypeUnite> = {
  UNITE: 'unite',
  MASSE: 'masse',
  VOLUME: 'volume',
  LONGUEUR: 'longueur',
  SURFACE: 'surface',
}

export function typeUniteDepuisDb(valeur: string): TypeUnite {
  return TYPE_UNITE_DEPUIS_DB[valeur] ?? 'unite'
}

const TYPE_ZONE_DEPUIS_DB: Record<string, TypeZone> = {
  BATIMENT: 'batiment',
  NIVEAU: 'niveau',
  TRANCHE: 'tranche',
}

export function typeZoneDepuisDb(valeur: string): TypeZone {
  return TYPE_ZONE_DEPUIS_DB[valeur] ?? 'batiment'
}

function statutActiviteDepuisDb(valeur: string): 'actif' | 'inactif' {
  return valeur === 'INACTIF' ? 'inactif' : 'actif'
}

export function statutChantierDepuisDb(valeur: string): StatutChantier {
  return statutActiviteDepuisDb(valeur)
}

export function statutLogementDepuisDb(valeur: string): StatutLogement {
  return statutActiviteDepuisDb(valeur)
}

/* --------------------------- Énumérés : app → base ------------------------ */

const ORIGINE_VERS_DB: Record<OrigineArticle, string> = {
  achat: 'ACHAT',
  production_interne: 'PRODUCTION_INTERNE',
  recuperation: 'RECUPERATION',
}

export function origineVersDb(valeur: OrigineArticle): string {
  return ORIGINE_VERS_DB[valeur]
}

const TYPE_ZONE_VERS_DB: Record<TypeZone, string> = {
  batiment: 'BATIMENT',
  niveau: 'NIVEAU',
  tranche: 'TRANCHE',
}

export function typeZoneVersDb(valeur: TypeZone): string {
  return TYPE_ZONE_VERS_DB[valeur]
}

function statutActiviteVersDb(valeur: 'actif' | 'inactif'): string {
  return valeur === 'inactif' ? 'INACTIF' : 'ACTIF'
}

/**
 * Convertit un `numeric(14,3)` transporté en chaîne en nombre. Le transport en
 * chaîne évite la dérive de virgule flottante ; la conversion n'intervient
 * qu'ici, au bord de l'application.
 */
export function nombreDepuisChaine(valeur: string): number {
  const nombre = Number.parseFloat(valeur)
  return Number.isFinite(nombre) ? nombre : 0
}

/** Formate une surface pour l'envoi : chaîne à trois décimales (numeric(14,3)). */
export function surfaceVersChaine(valeur: number): string {
  return valeur.toFixed(3)
}

/* ------------------------- Entités : base → domaine ----------------------- */

export function mapperCategorie(dto: CategorieDto): Categorie {
  return { code: dto.code_categorie, libelle: dto.libelle }
}

export function mapperUnite(dto: UniteMesureDto): UniteMesure {
  return {
    code: dto.code_unite,
    libelle: dto.libelle,
    typeUnite: typeUniteDepuisDb(dto.type_unite),
  }
}

export function mapperArticle(dto: ArticleDto): Article {
  return {
    id: dto.id_article,
    code: dto.code,
    designation: dto.designation,
    origine: origineDepuisDb(dto.origine),
    codeBarre: dto.code_barre,
    actif: dto.actif,
    codeCategorie: dto.categorie_article_code_categorie,
    codeUnite: dto.unite_mesure_code_unite,
  }
}

export function mapperMagasin(dto: MagasinDto): MagasinVue {
  return {
    id: dto.id_magasin,
    code: dto.code,
    nom: dto.nom,
    actif: dto.actif,
    idChantier: dto.chantier_id_chantier,
    libelleChantier: dto.libelle_chantier,
  }
}

export function mapperChantier(dto: ChantierDto): Chantier {
  return {
    id: dto.id_chantier,
    code: dto.code,
    nom: dto.nom,
    programme: dto.programme,
    dateDebut: dto.date_debut,
    statut: statutChantierDepuisDb(dto.statut),
  }
}

export function mapperZone(dto: ZoneDto): Zone {
  return {
    id: dto.id_zone,
    code: dto.code,
    nom: dto.nom,
    typeZone: typeZoneDepuisDb(dto.type_zone),
    idChantier: dto.chantier_id_chantier,
  }
}

export function mapperTypeLogement(dto: TypeLogementDto): TypeLogement {
  return {
    code: dto.code_type,
    libelle: dto.libelle,
    surfaceReference: nombreDepuisChaine(dto.surface_reference),
    actif: dto.actif,
  }
}

export function mapperLogement(dto: LogementDto): Logement {
  return {
    id: dto.id_logement,
    numero: dto.numero,
    statut: statutLogementDepuisDb(dto.statut),
    dateLivraisonPrevue: dto.date_livraison_prevue,
    idZone: dto.zone_id_zone,
    codeTypeLogement: dto.type_logement_code_type,
  }
}

/* --------------------------- Vues enrichies ------------------------------- */

/** Associe à chaque article les libellés de sa catégorie et de son unité. */
export function enrichirArticle(
  article: Article,
  categories: Map<string, string>,
  unites: Map<string, string>,
): ArticleVue {
  return {
    ...article,
    libelleCategorie: categories.get(article.codeCategorie) ?? article.codeCategorie,
    libelleUnite: unites.get(article.codeUnite) ?? article.codeUnite,
  }
}

/** Associe à chaque logement le libellé et la surface de son type. */
export function enrichirLogement(
  logement: Logement,
  typesLogement: Map<string, TypeLogement>,
): LogementVue {
  const type = typesLogement.get(logement.codeTypeLogement)
  return {
    ...logement,
    libelleType: type?.libelle ?? logement.codeTypeLogement,
    surfaceReference: type?.surfaceReference ?? 0,
  }
}

/** Construit l'arbre d'un chantier à partir de la réponse jointe et des types. */
export function mapperArborescence(
  dto: ChantierArbreDto,
  typesLogement: Map<string, TypeLogement>,
): ChantierArbre {
  const zones: ZoneArbre[] = dto.zones.map((entree) => ({
    zone: mapperZone(entree.zone),
    logements: entree.logements
      .map(mapperLogement)
      .map((logement) => enrichirLogement(logement, typesLogement)),
  }))

  return { chantier: mapperChantier(dto.chantier), zones }
}

/* ---------------------- Saisies : domaine → charge utile ------------------ */

export function corpsArticle(saisie: SaisieArticle): Record<string, unknown> {
  return {
    code: saisie.code,
    designation: saisie.designation,
    origine: origineVersDb(saisie.origine),
    code_barre: saisie.codeBarre,
    actif: saisie.actif,
    categorie_article_code_categorie: saisie.codeCategorie,
    unite_mesure_code_unite: saisie.codeUnite,
  }
}

export function corpsMagasin(saisie: SaisieMagasin): Record<string, unknown> {
  return {
    code: saisie.code,
    nom: saisie.nom,
    actif: saisie.actif,
    chantier_id_chantier: saisie.idChantier,
  }
}

export function corpsChantier(saisie: SaisieChantier): Record<string, unknown> {
  return {
    code: saisie.code,
    nom: saisie.nom,
    programme: saisie.programme,
    date_debut: saisie.dateDebut,
    statut: statutActiviteVersDb(saisie.statut),
  }
}

export function corpsZone(saisie: SaisieZone): Record<string, unknown> {
  return {
    code: saisie.code,
    nom: saisie.nom,
    type_zone: typeZoneVersDb(saisie.typeZone),
    chantier_id_chantier: saisie.idChantier,
  }
}

export function corpsLogement(saisie: SaisieLogement): Record<string, unknown> {
  return {
    numero: saisie.numero,
    statut: statutActiviteVersDb(saisie.statut),
    date_livraison_prevue: saisie.dateLivraisonPrevue,
    zone_id_zone: saisie.idZone,
    type_logement_code_type: saisie.codeTypeLogement,
  }
}
