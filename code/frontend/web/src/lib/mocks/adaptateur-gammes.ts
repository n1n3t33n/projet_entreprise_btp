/*
  Table de routes de simulation du module gammes (corps d'état et gammes
  opératoires). Renvoie `undefined` si aucune route ne correspond.

  Les règles métier (publier un brouillon, archiver une active, éditer les
  seules gammes brouillon) sont portées par le magasin de données
  `gammes-grand-bassam`. Quand une règle est violée, le magasin renvoie un objet
  `{ erreur }` que cet adaptateur transforme en rejet, comme le ferait un
  serveur répondant par un code d'erreur.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  archiverGammeDepuis,
  chargerGammeDto,
  creerCorpsEtatDepuis,
  creerVersionDepuis,
  enregistrerEtapesDepuis,
  listerCorpsEtatDto,
  listerGammesDto,
  modifierCorpsEtatDepuis,
  publierGammeDepuis,
} from '@/lib/mocks/gammes-grand-bassam'

function reponse<T>(config: InternalAxiosRequestConfig, data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: status === 204 ? 'No Content' : 'OK',
    headers: {},
    config,
  } as AxiosResponse<T>
}

function corpsJson(config: InternalAxiosRequestConfig): Record<string, unknown> {
  if (typeof config.data === 'string') {
    try {
      return JSON.parse(config.data) as Record<string, unknown>
    } catch {
      return {}
    }
  }
  if (config.data && typeof config.data === 'object') {
    return config.data as Record<string, unknown>
  }
  return {}
}

/** Lève une erreur quand le magasin renvoie `{ erreur }`, sinon rend la valeur. */
function ouLever<T>(resultat: T | { erreur: string }): T {
  if (resultat && typeof resultat === 'object' && 'erreur' in resultat) {
    throw new Error((resultat as { erreur: string }).erreur)
  }
  return resultat as T
}

export function routerGammes(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  /* ------------------------------ Corps d'état ---------------------------- */
  if (methode === 'get' && url === '/gammes/corps-etat') {
    return reponse(config, listerCorpsEtatDto())
  }
  if (methode === 'post' && url === '/gammes/corps-etat') {
    return reponse(config, creerCorpsEtatDepuis(corpsJson(config)), 201)
  }
  const corpsMatch = url.match(/^\/gammes\/corps-etat\/([^/]+)$/)
  if (methode === 'put' && corpsMatch) {
    return reponse(config, modifierCorpsEtatDepuis(corpsMatch[1] ?? '', corpsJson(config)))
  }

  /* -------------------------------- Gammes -------------------------------- */
  if (methode === 'get' && url === '/gammes') {
    return reponse(config, listerGammesDto())
  }

  const etapesMatch = url.match(/^\/gammes\/([^/]+)\/etapes$/)
  if (etapesMatch) {
    const idGamme = etapesMatch[1] ?? ''
    if (methode === 'get') {
      const detail = chargerGammeDto(idGamme)
      if (!detail) return undefined
      return reponse(config, detail.etapes)
    }
    if (methode === 'put') {
      return reponse(config, ouLever(enregistrerEtapesDepuis(idGamme, corpsJson(config))))
    }
  }

  const versionsMatch = url.match(/^\/gammes\/([^/]+)\/versions$/)
  if (methode === 'post' && versionsMatch) {
    return reponse(config, ouLever(creerVersionDepuis(versionsMatch[1] ?? '')), 201)
  }

  const publicationMatch = url.match(/^\/gammes\/([^/]+)\/publication$/)
  if (methode === 'post' && publicationMatch) {
    return reponse(config, ouLever(publierGammeDepuis(publicationMatch[1] ?? '')))
  }

  const archivageMatch = url.match(/^\/gammes\/([^/]+)\/archivage$/)
  if (methode === 'post' && archivageMatch) {
    return reponse(config, ouLever(archiverGammeDepuis(archivageMatch[1] ?? '')))
  }

  const detailMatch = url.match(/^\/gammes\/([^/]+)$/)
  if (methode === 'get' && detailMatch) {
    const detail = chargerGammeDto(detailMatch[1] ?? '')
    if (!detail) return undefined
    return reponse(config, detail.gamme)
  }

  return undefined
}
