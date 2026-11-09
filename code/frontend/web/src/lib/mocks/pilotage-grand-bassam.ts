/*
  Données simulées du module pilotage.

  Ce fichier ne détient aucune donnée propre : il agrège celles des modules
  avancement et stock. C'est voulu. Le tableau de bord et le journal sont des
  lectures d'un état dont d'autres modules sont les auteurs ; dupliquer ici des
  logements ou des mouvements ferait diverger les deux vues dès la première
  action de l'utilisateur. Toute déclaration d'étape faite dans l'écran de
  suivi se retrouve donc immédiatement dans le tableau de bord et dans le
  journal, parce que la source est la même.

  Règles appliquées :
  - RG-A6 : pourcentage = somme des poids des étapes terminées / somme des
    poids du périmètre considéré, en deux versions (déclaré, validé). La
    version déclarée compte les étapes déclarées terminées et les étapes
    validées ; la version validée ne compte que les étapes validées.
  - RG-A8 : une étape dont la date prévue est dépassée et qui n'est pas
    terminée est en retard ; une étape bloquée remonte au pilotage.
  - RG-A5 : les événements sont immuables et portent les deux horodatages.
  - RG-S5 et MPD-4 : deux seuils par article et magasin, et stock négatif
    traité comme une anomalie distincte.
*/

import type {
  AlerteEtapeDto,
  AvancementAgregeDto,
  EvenementJournalDto,
  IntervenantJournalDto,
  MouvementRecentDto,
  SyntheseStockDto,
} from '@/features/pilotage/api/dto'
import type { LigneEtapeDto } from '@/features/avancement/api/dto'
import {
  construireEtapesLogement,
  DATE_REFERENCE,
  logements,
  MOTIFS_BLOCAGE,
  TYPES_LOGEMENT,
  ZONES,
  listerEvenementsEtape,
} from '@/lib/mocks/avancement-grand-bassam'
import {
  ARTICLES,
  construireLignesStock,
  listerMouvementsRecents,
} from '@/lib/mocks/donnees-grand-bassam'

const MS_PAR_JOUR = 24 * 60 * 60 * 1000

function nombre(valeur: string): number {
  const parse = Number.parseFloat(valeur)
  return Number.isFinite(parse) ? parse : 0
}

function libelleZone(idZone: string): string {
  return ZONES.find((zone) => zone.id_zone === idZone)?.nom ?? idZone
}

/** Toutes les étapes du chantier, avec le logement auquel elles appartiennent. */
function toutesLesEtapes(): LigneEtapeDto[] {
  return logements.flatMap((logement) => construireEtapesLogement(logement.idLogement))
}

function estDeclaree(etape: LigneEtapeDto): boolean {
  return etape.statut === 'TERMINEE_DECLAREE' || etape.statut === 'VALIDEE'
}

function estValidee(etape: LigneEtapeDto): boolean {
  return etape.statut === 'VALIDEE'
}

/**
 * Cœur du calcul RG-A6, appliqué à un lot d'étapes quelconque. Les quatre
 * portées (chantier, zone, logement, corps d'état) ne se distinguent que par
 * le lot d'étapes qu'on lui passe : la règle de calcul, elle, est unique.
 */
function agreger(
  portee: AvancementAgregeDto['portee'],
  idCible: string,
  libelleCible: string,
  libelleSecondaire: string | null,
  couleur: string | null,
  etapes: LigneEtapeDto[],
): AvancementAgregeDto {
  const poidsTotal = etapes.reduce((somme, etape) => somme + nombre(etape.poids_effectif), 0)
  const poidsDeclare = etapes
    .filter(estDeclaree)
    .reduce((somme, etape) => somme + nombre(etape.poids_effectif), 0)
  const poidsValide = etapes
    .filter(estValidee)
    .reduce((somme, etape) => somme + nombre(etape.poids_effectif), 0)

  // Un périmètre sans étape vaut 0 % et non « division par zéro » : c'est le
  // cas d'un logement créé dont la gamme n'est pas encore affectée.
  const part = (poids: number): string =>
    poidsTotal === 0 ? '0.000' : ((poids / poidsTotal) * 100).toFixed(3)

  return {
    portee,
    id_cible: idCible,
    libelle_cible: libelleCible,
    libelle_secondaire: libelleSecondaire,
    couleur,
    pourcentage_declare: part(poidsDeclare),
    pourcentage_valide: part(poidsValide),
    nombre_etapes: etapes.length,
    nombre_validees: etapes.filter(estValidee).length,
    nombre_bloquees: etapes.filter((etape) => etape.statut === 'BLOQUEE').length,
    nombre_en_retard: etapes.filter((etape) => etape.en_retard).length,
    date_calcul: DATE_REFERENCE.toISOString(),
  }
}

export function construireAvancementChantier(): AvancementAgregeDto {
  return agreger('CHANTIER', 'CH-GB', 'Résidence Grand-Bassam', null, null, toutesLesEtapes())
}

export function construireAvancementZones(): AvancementAgregeDto[] {
  return ZONES.map((zone) => {
    const logementsDeLaZone = logements.filter((logement) => logement.idZone === zone.id_zone)
    const etapes = logementsDeLaZone.flatMap((logement) =>
      construireEtapesLogement(logement.idLogement),
    )
    return agreger(
      'ZONE',
      zone.id_zone,
      zone.nom,
      `${logementsDeLaZone.length} logements`,
      null,
      etapes,
    )
  })
}

export function construireAvancementLogements(): AvancementAgregeDto[] {
  return logements.map((logement) =>
    agreger(
      'LOGEMENT',
      logement.idLogement,
      `Logement ${logement.numero}`,
      `${libelleZone(logement.idZone)} · ${TYPES_LOGEMENT[logement.codeType] ?? logement.codeType}`,
      null,
      construireEtapesLogement(logement.idLogement),
    ),
  )
}

export function construireAvancementCorpsEtat(): AvancementAgregeDto[] {
  const parCorps = new Map<string, LigneEtapeDto[]>()
  for (const etape of toutesLesEtapes()) {
    const lot = parCorps.get(etape.code_corps_etat)
    if (lot) lot.push(etape)
    else parCorps.set(etape.code_corps_etat, [etape])
  }

  return [...parCorps.entries()]
    .map(([code, etapes]) => {
      const premiere = etapes[0]!
      return agreger(
        'CORPS_ETAT',
        code,
        premiere.libelle_corps_etat,
        `${etapes.length} étapes sur le chantier`,
        premiere.couleur_corps_etat,
        etapes,
      )
    })
    .sort((a, b) => a.libelle_cible.localeCompare(b.libelle_cible, 'fr'))
}

function libelleMotif(code: string | null): string | null {
  if (!code) return null
  return MOTIFS_BLOCAGE.find((motif) => motif.code_motif === code)?.libelle ?? code
}

/** Dernier événement de blocage d'une étape, source du motif et du commentaire. */
function dernierBlocage(idEtape: string): { motif: string | null; commentaire: string | null } {
  const evenement = listerEvenementsEtape(idEtape).find(
    (candidat) => candidat.statut_apres === 'BLOQUEE',
  )
  return {
    motif: evenement?.motif_blocage_code_motif ?? null,
    commentaire: evenement?.commentaire ?? null,
  }
}

export function construireAlertesEtapes(): AlerteEtapeDto[] {
  const alertes: AlerteEtapeDto[] = []

  for (const logement of logements) {
    for (const etape of construireEtapesLogement(logement.idLogement)) {
      const bloquee = etape.statut === 'BLOQUEE'
      if (!etape.en_retard && !bloquee) continue

      const jours = etape.date_prevue
        ? Math.max(
            0,
            Math.floor(
              (DATE_REFERENCE.getTime() - new Date(etape.date_prevue).getTime()) / MS_PAR_JOUR,
            ),
          )
        : 0
      const contexte = bloquee ? dernierBlocage(etape.id_etape) : { motif: null, commentaire: null }

      alertes.push({
        id_etape: etape.id_etape,
        id_logement: etape.id_logement,
        numero_logement: etape.numero_logement,
        libelle_zone: libelleZone(logement.idZone),
        libelle_etape: etape.libelle_etape,
        libelle_corps_etat: etape.libelle_corps_etat,
        couleur_corps_etat: etape.couleur_corps_etat,
        statut: etape.statut,
        date_prevue: etape.date_prevue,
        jours_de_retard: etape.en_retard ? jours : 0,
        code_motif_blocage: contexte.motif,
        libelle_motif_blocage: libelleMotif(contexte.motif),
        commentaire: contexte.commentaire,
      })
    }
  }

  // Les blocages d'abord, puis le retard le plus ancien : c'est l'ordre dans
  // lequel le pilotage doit traiter (un blocage immobilise une équipe).
  return alertes.sort((a, b) => {
    if (a.statut === 'BLOQUEE' && b.statut !== 'BLOQUEE') return -1
    if (b.statut === 'BLOQUEE' && a.statut !== 'BLOQUEE') return 1
    return b.jours_de_retard - a.jours_de_retard
  })
}

export function construireSyntheseStock(): SyntheseStockDto {
  const lignes = construireLignesStock()
  return {
    nombre_articles: lignes.length,
    nombre_critique: lignes.filter(
      (ligne) => ligne.stock.niveau_alerte === 'CRITIQUE' || ligne.stock.niveau_alerte === 'VIDE',
    ).length,
    nombre_vigilance: lignes.filter((ligne) => ligne.stock.niveau_alerte === 'MINIMAL').length,
    nombre_negatif: lignes.filter((ligne) => nombre(ligne.stock.quantite) < 0).length,
  }
}

export function construireMouvementsRecents(limite: number): MouvementRecentDto[] {
  const lignes = construireLignesStock()
  return listerMouvementsRecents(limite).map((mouvement) => {
    const article = ARTICLES.find(
      (candidat) => candidat.id_article === mouvement.article_id_article,
    )
    const ligne = lignes.find(
      (candidate) => candidate.article.id_article === mouvement.article_id_article,
    )
    return {
      ...mouvement,
      code_article: article?.code ?? mouvement.article_id_article,
      libelle_article: article?.designation ?? mouvement.article_id_article,
      code_unite: article?.unite_base.code_unite ?? '',
      niveau_alerte_article: ligne?.stock.niveau_alerte ?? 'NORMAL',
    }
  })
}

/** Tous les événements du chantier, contexte compris, du plus récent au plus ancien. */
function tousLesEvenements(): EvenementJournalDto[] {
  const journal: EvenementJournalDto[] = []

  for (const logement of logements) {
    const zone = libelleZone(logement.idZone)
    for (const etape of construireEtapesLogement(logement.idLogement)) {
      for (const evenement of listerEvenementsEtape(etape.id_etape)) {
        journal.push({
          uuid: evenement.uuid,
          id_etape: etape.id_etape,
          libelle_etape: etape.libelle_etape,
          id_logement: logement.idLogement,
          numero_logement: logement.numero,
          libelle_zone: zone,
          code_corps_etat: etape.code_corps_etat,
          libelle_corps_etat: etape.libelle_corps_etat,
          statut_avant: evenement.statut_avant,
          statut_apres: evenement.statut_apres,
          horodatage_appareil: evenement.horodatage_appareil,
          horodatage_serveur: evenement.horodatage_serveur,
          id_auteur: evenement.utilisateur_id_utilisateur,
          nom_auteur: evenement.nom_auteur,
          est_delegation: evenement.est_delegation,
          code_motif_blocage: evenement.motif_blocage_code_motif,
          libelle_motif_blocage: libelleMotif(evenement.motif_blocage_code_motif),
          commentaire: evenement.commentaire,
        })
      }
    }
  }

  return journal.sort((a, b) => b.horodatage_serveur.localeCompare(a.horodatage_serveur))
}

export type FiltresJournalMock = {
  auteur?: string
  zone?: string
  /** Statut d'arrivée, reçu en minuscules depuis la couche `api`. */
  statut?: string
  depuis?: string
  jusqua?: string
}

export function construireJournal(filtres: FiltresJournalMock): EvenementJournalDto[] {
  const statutAttendu = filtres.statut ? filtres.statut.toUpperCase() : null
  const zoneAttendue = filtres.zone
    ? (ZONES.find((zone) => zone.id_zone === filtres.zone)?.nom ?? filtres.zone)
    : null

  return tousLesEvenements().filter((evenement) => {
    if (filtres.auteur && evenement.id_auteur !== filtres.auteur) return false
    if (statutAttendu && evenement.statut_apres !== statutAttendu) return false
    if (zoneAttendue && evenement.libelle_zone !== zoneAttendue) return false
    // Les bornes portent sur l'horodatage serveur, qui est l'instant de prise
    // en compte : c'est lui qui fait foi pour une recherche d'activité.
    const jour = evenement.horodatage_serveur.slice(0, 10)
    if (filtres.depuis && jour < filtres.depuis) return false
    if (filtres.jusqua && jour > filtres.jusqua) return false
    return true
  })
}

export function listerIntervenantsJournal(): IntervenantJournalDto[] {
  const parId = new Map<string, string>()
  for (const evenement of tousLesEvenements()) {
    if (!parId.has(evenement.id_auteur)) parId.set(evenement.id_auteur, evenement.nom_auteur)
  }
  return [...parId.entries()]
    .map(([id, nom]) => ({ id_utilisateur: id, nom }))
    .sort((a, b) => a.nom.localeCompare(b.nom, 'fr'))
}
