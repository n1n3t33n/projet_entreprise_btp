/*
  Table de routes de simulation de l'espace acquéreur (UC-5, EF-ACQ-01/02).
  Lecture seule. Renvoie `undefined` si aucune route ne correspond.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { logementAcquereur, notificationsAcquereur } from '@/lib/mocks/acquereur-grand-bassam'

function reponse<T>(config: InternalAxiosRequestConfig, data: T): AxiosResponse<T> {
  return {
    data,
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  } as AxiosResponse<T>
}

export function routerAcquereur(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  if (methode === 'get' && url === '/acquereur/logement') {
    return reponse(config, logementAcquereur())
  }

  if (methode === 'get' && url === '/acquereur/notifications') {
    return reponse(config, notificationsAcquereur())
  }

  return undefined
}
