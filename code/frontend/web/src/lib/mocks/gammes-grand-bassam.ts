/*
  Données de démonstration des gammes opératoires et des corps d'état.

  Ce fichier est la SOURCE UNIQUE des corps d'état et des étapes-modèles. Jusqu'à
  l'étape 10, ces données étaient codées en dur dans `avancement-grand-bassam.ts` ;
  elles deviennent ici un référentiel géré, modifiable par le responsable
  technique (EF-REF-05), exactement comme la matrice des droits est devenue une
  donnée à l'étape 9. Le module d'avancement consomme désormais ces données
  (`etapesModeleDemo`, `corpsEtatDemo`) au lieu de les détenir.

  Modélisation (CL-3b, MPD-3) :
  - CorpsEtat { codeCorpsEtat, libelle, ordre, couleur }.
  - Gamme { idGamme, version, libelle, statut, dateActivation } rattachée à un
    TypeLogement ; opérations publier(), archiver(), poidsTotal().
  - EtapeModele { idEtapeModele, code, libelle, ordre, poids, controleRequis }
    composée dans une gamme et relevant d'un corps d'état.

  Cycle de vie d'une gamme (EF-REF-09). Le MPD ne fige pas les littéraux de
  `Gamme.statut` (la contrainte CHECK liste un ensemble générique terminé par
  « … ») ; les trois états retenus se déduisent des opérations publier() et
  archiver() et de l'attribut `version` :
  - BROUILLON : version en préparation, dont les étapes sont modifiables.
  - ACTIVE : version publiée, servant aux nouvelles instanciations. Une seule
    gamme active par type de logement.
  - ARCHIVEE : version remplacée par une plus récente. Conservée, car les
    logements déjà instanciés en gardent la trace.

  Une étape-modèle n'est modifiable que sur une gamme BROUILLON : une fois
  publiée, la gamme sert de contrat aux logements instanciés et ne change plus
  (même logique d'immuabilité que le journal d'exécution). Pour faire évoluer
  une gamme active, on en crée une nouvelle version (brouillon), qu'on publie.
*/

import type {
  CorpsEtatDto,
  EtapeModeleDto,
  GammeDto,
  StatutGammeDb,
} from '@/features/gammes/api/dto'

/** Forme attendue par le module d'avancement pour instancier ses étapes. */
export type EtapeModeleSeed = {
  id: string
  libelle: string
  ordre: number
  poids: number
  controleRequis: boolean
  corps: string
}

/** Libellés des types de logement connus du référentiel des gammes (CL-2). */
export const LIBELLES_TYPE_LOGEMENT: Record<string, string> = {
  VILLA3: 'Villa 3 pièces',
  VILLA4: 'Villa 4 pièces',
  DUPLEX: 'Duplex',
}

/* ------------------------------ Corps d'état ------------------------------ */

type CorpsEtatRecord = {
  codeCorpsEtat: string
  libelle: string
  ordre: number
  couleur: string
}

let corpsEtat: CorpsEtatRecord[] = [
  { codeCorpsEtat: 'GO', libelle: 'Gros œuvre', ordre: 1, couleur: '#6c8ebf' },
  { codeCorpsEtat: 'MAC', libelle: 'Maçonnerie', ordre: 2, couleur: '#b8954a' },
  { codeCorpsEtat: 'ELEC', libelle: 'Électricité', ordre: 3, couleur: '#9673a6' },
  { codeCorpsEtat: 'PLOMB', libelle: 'Plomberie', ordre: 4, couleur: '#3f8f7a' },
  { codeCorpsEtat: 'FIN', libelle: 'Finitions', ordre: 5, couleur: '#b85450' },
]

/* ------------------------- Modèle d'étapes canonique ----------------------- */

/*
  Dix étapes types, poids total 100. C'est le contenu exact qui était codé en
  dur dans le module d'avancement ; il est conservé à l'identique (mêmes codes
  EM-01…EM-10, mêmes corps d'état) pour que l'instanciation des logements et les
  identifiants d'événements déjà en place restent inchangés.
*/
const MODELE_CANONIQUE: EtapeModeleSeed[] = [
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

/**
 * Étapes-modèles servies au module d'avancement. Volontairement découplées de
 * l'état mutable des gammes ci-dessous : les logements de démonstration ont été
 * « instanciés » à partir de cette gamme, et publier une nouvelle version à
 * l'écran ne doit pas réécrire rétroactivement leurs étapes.
 */
export function etapesModeleDemo(): EtapeModeleSeed[] {
  return MODELE_CANONIQUE.map((etape) => ({ ...etape }))
}

/** Corps d'état servis au module d'avancement, dans sa forme attendue. */
export function corpsEtatDemo(): Record<string, { libelle: string; couleur: string }> {
  return Object.fromEntries(
    corpsEtat.map((corps) => [
      corps.codeCorpsEtat,
      { libelle: corps.libelle, couleur: corps.couleur },
    ]),
  )
}

/* ------------------------------- Gammes ----------------------------------- */

type GammeRecord = {
  idGamme: string
  version: number
  libelle: string
  statut: StatutGammeDb
  dateActivation: string | null
  codeTypeLogement: string
}

type EtapeModeleRecord = {
  idEtapeModele: string
  code: string
  libelle: string
  ordre: number
  poids: number
  controleRequis: boolean
  codeCorpsEtat: string
  idGamme: string
}

const MAINTENANT = new Date('2026-11-08T08:00:00.000Z')

/** Fabrique les étapes d'une gamme à partir du modèle canonique. */
function etapesDepuisModele(idGamme: string, prefixe: string): EtapeModeleRecord[] {
  return MODELE_CANONIQUE.map((etape) => ({
    idEtapeModele: `${prefixe}-${etape.id}`,
    code: etape.id,
    libelle: etape.libelle,
    ordre: etape.ordre,
    poids: etape.poids,
    controleRequis: etape.controleRequis,
    codeCorpsEtat: etape.corps,
    idGamme,
  }))
}

let gammes: GammeRecord[] = [
  {
    idGamme: 'G-V3-1',
    version: 1,
    libelle: 'Villa 3 pièces — gamme standard',
    statut: 'ACTIVE',
    dateActivation: '2026-09-01',
    codeTypeLogement: 'VILLA3',
  },
  {
    idGamme: 'G-V4-1',
    version: 1,
    libelle: 'Villa 4 pièces — gamme standard',
    statut: 'ACTIVE',
    dateActivation: '2026-09-01',
    codeTypeLogement: 'VILLA4',
  },
  {
    idGamme: 'G-DX-1',
    version: 1,
    libelle: 'Duplex — gamme standard',
    statut: 'ACTIVE',
    dateActivation: '2026-09-01',
    codeTypeLogement: 'DUPLEX',
  },
  {
    // Brouillon destiné à illustrer la publication d'une nouvelle version.
    idGamme: 'G-V3-2',
    version: 2,
    libelle: 'Villa 3 pièces — révision isolation',
    statut: 'BROUILLON',
    dateActivation: null,
    codeTypeLogement: 'VILLA3',
  },
]

let etapesModele: EtapeModeleRecord[] = [
  ...etapesDepuisModele('G-V3-1', 'V3'),
  ...etapesDepuisModele('G-V4-1', 'V4'),
  ...etapesDepuisModele('G-DX-1', 'DX'),
  // Le brouillon part d'une copie du modèle, enrichie d'une étape d'isolation :
  // c'est la différence que la publication rendra active.
  ...etapesDepuisModele('G-V3-2', 'V32'),
]
etapesModele.push({
  idEtapeModele: 'V32-EM-11',
  code: 'EM-11',
  libelle: 'Isolation thermique',
  ordre: 6,
  poids: 6,
  controleRequis: true,
  codeCorpsEtat: 'MAC',
  idGamme: 'G-V3-2',
})

let compteurGamme = 100

/* ------------------------- Accès lecture (routeur) ------------------------ */

export function listerCorpsEtatDto(): CorpsEtatDto[] {
  return [...corpsEtat]
    .sort((a, b) => a.ordre - b.ordre)
    .map((corps) => ({
      code_corps_etat: corps.codeCorpsEtat,
      libelle: corps.libelle,
      ordre: corps.ordre,
      couleur: corps.couleur,
    }))
}

function poidsTotal(idGamme: string): number {
  return etapesModele
    .filter((etape) => etape.idGamme === idGamme)
    .reduce((somme, etape) => somme + etape.poids, 0)
}

export function listerGammesDto(): GammeDto[] {
  return [...gammes]
    .sort((a, b) => {
      const parType = a.codeTypeLogement.localeCompare(b.codeTypeLogement)
      return parType !== 0 ? parType : b.version - a.version
    })
    .map((gamme) => ({
      id_gamme: gamme.idGamme,
      version: gamme.version,
      libelle: gamme.libelle,
      statut: gamme.statut,
      date_activation: gamme.dateActivation,
      type_logement_code_type: gamme.codeTypeLogement,
      libelle_type_logement:
        LIBELLES_TYPE_LOGEMENT[gamme.codeTypeLogement] ?? gamme.codeTypeLogement,
      nombre_etapes: etapesModele.filter((etape) => etape.idGamme === gamme.idGamme).length,
      poids_total: poidsTotal(gamme.idGamme).toFixed(3),
    }))
}

function etapesDto(idGamme: string): EtapeModeleDto[] {
  const libelleCorps = new Map(corpsEtat.map((corps) => [corps.codeCorpsEtat, corps.libelle]))
  const couleurCorps = new Map(corpsEtat.map((corps) => [corps.codeCorpsEtat, corps.couleur]))
  return etapesModele
    .filter((etape) => etape.idGamme === idGamme)
    .sort((a, b) => a.ordre - b.ordre)
    .map((etape) => ({
      id_etape_modele: etape.idEtapeModele,
      code: etape.code,
      libelle: etape.libelle,
      ordre: etape.ordre,
      poids: etape.poids.toFixed(3),
      controle_requis: etape.controleRequis,
      corps_etat_code_corps_etat: etape.codeCorpsEtat,
      libelle_corps_etat: libelleCorps.get(etape.codeCorpsEtat) ?? etape.codeCorpsEtat,
      couleur_corps_etat: couleurCorps.get(etape.codeCorpsEtat) ?? '#6c8ebf',
      gamme_id_gamme: etape.idGamme,
    }))
}

/** Détail d'une gamme : ses attributs et ses étapes triées. */
export function chargerGammeDto(
  idGamme: string,
): { gamme: GammeDto; etapes: EtapeModeleDto[] } | undefined {
  const gamme = listerGammesDto().find((candidate) => candidate.id_gamme === idGamme)
  if (!gamme) return undefined
  return { gamme, etapes: etapesDto(idGamme) }
}

/* ------------------------- Accès écriture (routeur) ----------------------- */

function normaliser(valeur: unknown): string {
  return typeof valeur === 'string' ? valeur.trim() : ''
}

export function creerCorpsEtatDepuis(corps: Record<string, unknown>): CorpsEtatDto {
  const code = normaliser(corps.code_corps_etat).toUpperCase()
  const record: CorpsEtatRecord = {
    codeCorpsEtat: code,
    libelle: normaliser(corps.libelle),
    ordre: typeof corps.ordre === 'number' ? corps.ordre : corpsEtat.length + 1,
    couleur: normaliser(corps.couleur) || '#6c8ebf',
  }
  corpsEtat = [...corpsEtat.filter((c) => c.codeCorpsEtat !== code), record]
  return {
    code_corps_etat: record.codeCorpsEtat,
    libelle: record.libelle,
    ordre: record.ordre,
    couleur: record.couleur,
  }
}

export function modifierCorpsEtatDepuis(
  code: string,
  corps: Record<string, unknown>,
): CorpsEtatDto {
  corpsEtat = corpsEtat.map((c) =>
    c.codeCorpsEtat === code
      ? {
          ...c,
          libelle: normaliser(corps.libelle) || c.libelle,
          ordre: typeof corps.ordre === 'number' ? corps.ordre : c.ordre,
          couleur: normaliser(corps.couleur) || c.couleur,
        }
      : c,
  )
  const maj = corpsEtat.find((c) => c.codeCorpsEtat === code)!
  return {
    code_corps_etat: maj.codeCorpsEtat,
    libelle: maj.libelle,
    ordre: maj.ordre,
    couleur: maj.couleur,
  }
}

/**
 * Crée une nouvelle version BROUILLON à partir de la version active d'un type
 * de logement (ou d'une gamme existante). Copie ses étapes pour qu'elles soient
 * éditables sans toucher à la version en service.
 */
export function creerVersionDepuis(idGammeSource: string): GammeDto | { erreur: string } {
  const source = gammes.find((g) => g.idGamme === idGammeSource)
  if (!source) return { erreur: 'Gamme introuvable.' }

  const dejaBrouillon = gammes.find(
    (g) => g.codeTypeLogement === source.codeTypeLogement && g.statut === 'BROUILLON',
  )
  if (dejaBrouillon) {
    return { erreur: 'Une version brouillon existe déjà pour ce type de logement.' }
  }

  const versionMax = Math.max(
    ...gammes.filter((g) => g.codeTypeLogement === source.codeTypeLogement).map((g) => g.version),
  )
  compteurGamme += 1
  const idGamme = `G-${compteurGamme}`
  const nouvelle: GammeRecord = {
    idGamme,
    version: versionMax + 1,
    libelle: `${LIBELLES_TYPE_LOGEMENT[source.codeTypeLogement] ?? source.codeTypeLogement} — version ${versionMax + 1}`,
    statut: 'BROUILLON',
    dateActivation: null,
    codeTypeLogement: source.codeTypeLogement,
  }
  gammes = [...gammes, nouvelle]

  const copies: EtapeModeleRecord[] = etapesModele
    .filter((etape) => etape.idGamme === idGammeSource)
    .map((etape, index) => ({
      ...etape,
      idEtapeModele: `${idGamme}-E${index + 1}`,
      idGamme,
    }))
  etapesModele = [...etapesModele, ...copies]

  return listerGammesDto().find((g) => g.id_gamme === idGamme)!
}

/**
 * Publie une gamme BROUILLON : elle devient ACTIVE, l'ancienne version active du
 * même type de logement est archivée (EF-REF-09). Refusé si la gamme n'est pas
 * un brouillon ou si elle n'a aucune étape.
 */
export function publierGammeDepuis(idGamme: string): GammeDto | { erreur: string } {
  const gamme = gammes.find((g) => g.idGamme === idGamme)
  if (!gamme) return { erreur: 'Gamme introuvable.' }
  if (gamme.statut !== 'BROUILLON') {
    return { erreur: 'Seule une gamme en brouillon peut être publiée.' }
  }
  if (etapesModele.filter((etape) => etape.idGamme === idGamme).length === 0) {
    return { erreur: 'Une gamme sans étape ne peut pas être publiée.' }
  }

  const dateJour = MAINTENANT.toISOString().slice(0, 10)
  gammes = gammes.map((g) => {
    if (g.idGamme === idGamme) return { ...g, statut: 'ACTIVE', dateActivation: dateJour }
    if (g.codeTypeLogement === gamme.codeTypeLogement && g.statut === 'ACTIVE') {
      return { ...g, statut: 'ARCHIVEE' }
    }
    return g
  })
  return listerGammesDto().find((g) => g.id_gamme === idGamme)!
}

/** Archive une gamme ACTIVE sans la remplacer (retrait du service). */
export function archiverGammeDepuis(idGamme: string): GammeDto | { erreur: string } {
  const gamme = gammes.find((g) => g.idGamme === idGamme)
  if (!gamme) return { erreur: 'Gamme introuvable.' }
  if (gamme.statut !== 'ACTIVE') {
    return { erreur: 'Seule une gamme active peut être archivée.' }
  }
  gammes = gammes.map((g) => (g.idGamme === idGamme ? { ...g, statut: 'ARCHIVEE' } : g))
  return listerGammesDto().find((g) => g.id_gamme === idGamme)!
}

/**
 * Remplace les étapes d'une gamme BROUILLON. Refusé sur une gamme publiée ou
 * archivée : la gamme est alors un contrat figé.
 */
export function enregistrerEtapesDepuis(
  idGamme: string,
  corps: Record<string, unknown>,
): EtapeModeleDto[] | { erreur: string } {
  const gamme = gammes.find((g) => g.idGamme === idGamme)
  if (!gamme) return { erreur: 'Gamme introuvable.' }
  if (gamme.statut !== 'BROUILLON') {
    return { erreur: 'Les étapes ne sont modifiables que sur une gamme en brouillon.' }
  }

  const recues = Array.isArray(corps.etapes) ? corps.etapes : []
  const nouvelles: EtapeModeleRecord[] = recues
    .map((brut, index) => {
      if (!brut || typeof brut !== 'object') return null
      const entree = brut as Record<string, unknown>
      const codeCorps = normaliser(entree.corps_etat_code_corps_etat)
      if (!corpsEtat.some((c) => c.codeCorpsEtat === codeCorps)) return null
      return {
        idEtapeModele: normaliser(entree.id_etape_modele) || `${idGamme}-E${index + 1}`,
        code: normaliser(entree.code) || `EM-${index + 1}`,
        libelle: normaliser(entree.libelle),
        ordre: typeof entree.ordre === 'number' ? entree.ordre : index + 1,
        poids: typeof entree.poids === 'number' ? entree.poids : Number(entree.poids) || 0,
        controleRequis: entree.controle_requis === true,
        codeCorpsEtat: codeCorps,
        idGamme,
      }
    })
    .filter((etape): etape is EtapeModeleRecord => etape !== null)

  etapesModele = [...etapesModele.filter((etape) => etape.idGamme !== idGamme), ...nouvelles]
  return etapesDto(idGamme)
}
