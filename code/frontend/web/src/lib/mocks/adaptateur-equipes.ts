/*
  Table de routes de simulation du module « équipes et affectation » (EF-REF-06).
  Renvoie `undefined` si aucune route ne correspond.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  creerFicheMock,
  listerEquipes,
  listerEtapesAffectables,
  listerFichesMembre,
  listerMembres,
} from '@/lib/mocks/equipes-grand-bassam'

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

export function routerEquipes(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  if (methode === 'get' && url === '/equipes') {
    return reponse(config, listerEquipes())
  }

  const membresMatch = url.match(/^\/equipes\/([^/]+)\/membres$/)
  if (methode === 'get' && membresMatch) {
    return reponse(config, listerMembres(membresMatch[1] ?? ''))
  }

  if (methode === 'get' && url === '/etapes-affectables') {
    return reponse(config, listerEtapesAffectables())
  }

  const fichesMatch = url.match(/^\/membres\/([^/]+)\/fiches$/)
  if (methode === 'get' && fichesMatch) {
    return reponse(config, listerFichesMembre(fichesMatch[1] ?? ''))
  }

  if (methode === 'post' && url === '/fiches-route') {
    const fiche = creerFicheMock(corpsJson(config))
    if (!fiche) {
      return reponse(config, { message: 'Membre inconnu.' }, 404)
    }
    return reponse(config, fiche, 201)
  }

  return undefined
}
