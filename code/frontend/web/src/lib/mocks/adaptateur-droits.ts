/*
  Table de routes de simulation du domaine « accès et droits ». Renvoie
  `undefined` si aucune route ne correspond, pour laisser la main à l'appelant.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  listerDroits,
  listerPermissions,
  listerRoles,
  remplacerDroits,
} from '@/lib/mocks/droits-grand-bassam'

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

export function routerDroits(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  if (methode === 'get' && url === '/droits/roles') {
    return reponse(config, listerRoles())
  }

  if (methode === 'get' && url === '/droits/permissions') {
    return reponse(config, listerPermissions())
  }

  if (methode === 'get' && url === '/droits/accordes') {
    return reponse(config, listerDroits())
  }

  if (methode === 'put' && url === '/droits/accordes') {
    return reponse(config, remplacerDroits(corpsJson(config)))
  }

  return undefined
}
