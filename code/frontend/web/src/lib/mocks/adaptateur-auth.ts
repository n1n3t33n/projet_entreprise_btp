/*
  Table de routes de simulation de la connexion et des comptes. Renvoie
  `undefined` si aucune route ne correspond.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  creerCompteMock,
  listerComptes,
  listerPerimetres,
  modifierCompteMock,
  tenterConnexion,
} from '@/lib/mocks/auth-grand-bassam'

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

export function routerAuth(config: InternalAxiosRequestConfig): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  if (methode === 'post' && url === '/auth/connexion') {
    const resultat = tenterConnexion(corpsJson(config))
    if (resultat.ok) {
      return reponse(config, resultat.session)
    }
    // Un échec de connexion doit parvenir à l'appelant comme une erreur HTTP,
    // avec son corps : axios rejette la promesse, et la couche api la qualifie.
    const erreur = Object.assign(new Error(resultat.echec.message), {
      isAxiosError: true,
      config,
      response: reponse(config, resultat.echec, resultat.statut),
    })
    throw erreur
  }

  if (methode === 'post' && url === '/auth/deconnexion') {
    return reponse(config, null, 204)
  }

  if (methode === 'get' && url === '/auth/perimetres') {
    return reponse(config, listerPerimetres())
  }

  if (methode === 'get' && url === '/auth/comptes') {
    return reponse(config, listerComptes())
  }

  if (methode === 'post' && url === '/auth/comptes') {
    return reponse(config, creerCompteMock(corpsJson(config)), 201)
  }

  const compteMatch = url.match(/^\/auth\/comptes\/([^/]+)$/)
  if (methode === 'put' && compteMatch) {
    const compte = modifierCompteMock(compteMatch[1] ?? '', corpsJson(config))
    return compte ? reponse(config, compte) : reponse(config, null, 404)
  }

  return undefined
}
