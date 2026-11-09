/*
  Table de routes de simulation du module pilotage. Résout une requête contre
  les données agrégées de Grand-Bassam ; renvoie `undefined` si aucune route ne
  correspond, pour laisser la main à l'appelant.

  Toutes les routes sont en lecture : le pilotage n'écrit rien (RG-A5).
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  construireAlertesEtapes,
  construireAvancementChantier,
  construireAvancementCorpsEtat,
  construireAvancementLogements,
  construireAvancementZones,
  construireJournal,
  construireMouvementsRecents,
  construireSyntheseStock,
  listerIntervenantsJournal,
  type FiltresJournalMock,
} from '@/lib/mocks/pilotage-grand-bassam'

function reponse<T>(config: InternalAxiosRequestConfig, data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: 'OK',
    headers: {},
    config,
  } as AxiosResponse<T>
}

/** Lit un paramètre de requête textuel, qu'axios transmet dans `config.params`. */
function parametre(config: InternalAxiosRequestConfig, nom: string): string | undefined {
  const params = config.params as Record<string, unknown> | undefined
  const valeur = params?.[nom]
  return typeof valeur === 'string' && valeur.length > 0 ? valeur : undefined
}

function entier(config: InternalAxiosRequestConfig, nom: string, defaut: number): number {
  const params = config.params as Record<string, unknown> | undefined
  const valeur = params?.[nom]
  if (typeof valeur === 'number' && Number.isFinite(valeur)) return valeur
  if (typeof valeur === 'string') {
    const parse = Number.parseInt(valeur, 10)
    if (Number.isFinite(parse)) return parse
  }
  return defaut
}

export function routerPilotage(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''
  if (methode !== 'get') return undefined

  if (url === '/pilotage/avancement/chantier') {
    return reponse(config, construireAvancementChantier())
  }
  if (url === '/pilotage/avancement/zones') {
    return reponse(config, construireAvancementZones())
  }
  if (url === '/pilotage/avancement/logements') {
    return reponse(config, construireAvancementLogements())
  }
  if (url === '/pilotage/avancement/corps-etat') {
    return reponse(config, construireAvancementCorpsEtat())
  }
  if (url === '/pilotage/alertes-etapes') {
    return reponse(config, construireAlertesEtapes())
  }
  if (url === '/pilotage/stock/synthese') {
    return reponse(config, construireSyntheseStock())
  }
  if (url === '/pilotage/stock/mouvements-recents') {
    return reponse(config, construireMouvementsRecents(entier(config, 'limite', 8)))
  }
  if (url === '/pilotage/journal/intervenants') {
    return reponse(config, listerIntervenantsJournal())
  }
  if (url === '/pilotage/journal') {
    const filtres: FiltresJournalMock = {}
    const auteur = parametre(config, 'auteur')
    const zone = parametre(config, 'zone')
    const statut = parametre(config, 'statut')
    const depuis = parametre(config, 'depuis')
    const jusqua = parametre(config, 'jusqua')
    if (auteur) filtres.auteur = auteur
    if (zone) filtres.zone = zone
    if (statut) filtres.statut = statut
    if (depuis) filtres.depuis = depuis
    if (jusqua) filtres.jusqua = jusqua
    return reponse(config, construireJournal(filtres))
  }

  return undefined
}
