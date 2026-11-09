/*
  Table de routes de simulation du module parametrage (paramètres de chantier et
  règles de validation). Renvoie `undefined` si aucune route ne correspond.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  creerParametreDepuis,
  creerRegleDepuis,
  listerParametresDto,
  listerReglesDto,
  modifierParametreDepuis,
  modifierRegleDepuis,
} from '@/lib/mocks/parametrage-grand-bassam'

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

export function routerParametrage(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  /* ------------------------------ Paramètres ---------------------------- */
  if (methode === 'get' && url === '/parametrage/parametres') {
    return reponse(config, listerParametresDto())
  }
  if (methode === 'post' && url === '/parametrage/parametres') {
    return reponse(config, creerParametreDepuis(corpsJson(config)), 201)
  }
  const parametreMatch = url.match(/^\/parametrage\/parametres\/([^/]+)$/)
  if (methode === 'put' && parametreMatch) {
    const maj = modifierParametreDepuis(parametreMatch[1] ?? '', corpsJson(config))
    if (!maj) throw new Error('Paramètre introuvable.')
    return reponse(config, maj)
  }

  /* -------------------------- Règles de validation ---------------------- */
  if (methode === 'get' && url === '/parametrage/regles') {
    return reponse(config, listerReglesDto())
  }
  if (methode === 'post' && url === '/parametrage/regles') {
    return reponse(config, creerRegleDepuis(corpsJson(config)), 201)
  }
  const regleMatch = url.match(/^\/parametrage\/regles\/([^/]+)$/)
  if (methode === 'put' && regleMatch) {
    const maj = modifierRegleDepuis(regleMatch[1] ?? '', corpsJson(config))
    if (!maj) throw new Error('Règle introuvable.')
    return reponse(config, maj)
  }

  return undefined
}
