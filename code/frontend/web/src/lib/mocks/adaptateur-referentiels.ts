/*
  Table de routes de simulation du module référentiels. Résout une requête
  contre les données de Grand-Bassam ; renvoie `undefined` si aucune route ne
  correspond, pour laisser la main à l'appelant.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  construireArborescence,
  creerArticleMock,
  creerLogementMock,
  creerMagasinMock,
  creerZoneMock,
  listerArticles,
  listerCategories,
  listerChantiers,
  listerMagasins,
  listerTypesLogement,
  listerUnites,
  modifierArticleMock,
  modifierChantierMock,
  modifierLogementMock,
  modifierMagasinMock,
  modifierZoneMock,
} from '@/lib/mocks/referentiels-grand-bassam'

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

export function routerReferentiels(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  /* ------------------------------ Catalogue ------------------------------ */

  if (methode === 'get' && url === '/referentiels/categories') {
    return reponse(config, listerCategories())
  }

  if (methode === 'get' && url === '/referentiels/unites') {
    return reponse(config, listerUnites())
  }

  if (methode === 'get' && url === '/referentiels/articles') {
    return reponse(config, listerArticles())
  }

  if (methode === 'post' && url === '/referentiels/articles') {
    return reponse(config, creerArticleMock(corpsJson(config)), 201)
  }

  const articleMatch = url.match(/^\/referentiels\/articles\/([^/]+)$/)
  if (methode === 'put' && articleMatch) {
    const article = modifierArticleMock(articleMatch[1] ?? '', corpsJson(config))
    return article ? reponse(config, article) : reponse(config, null, 404)
  }

  /* ------------------------------- Magasins ------------------------------ */

  if (methode === 'get' && url === '/referentiels/magasins') {
    return reponse(config, listerMagasins())
  }

  if (methode === 'post' && url === '/referentiels/magasins') {
    const magasin = creerMagasinMock(corpsJson(config))
    return magasin ? reponse(config, magasin, 201) : reponse(config, null, 400)
  }

  const magasinMatch = url.match(/^\/referentiels\/magasins\/([^/]+)$/)
  if (methode === 'put' && magasinMatch) {
    const magasin = modifierMagasinMock(magasinMatch[1] ?? '', corpsJson(config))
    return magasin ? reponse(config, magasin) : reponse(config, null, 404)
  }

  /* -------------------------- Chantiers & zones -------------------------- */

  if (methode === 'get' && url === '/referentiels/chantiers') {
    return reponse(config, listerChantiers())
  }

  if (methode === 'get' && url === '/referentiels/types-logement') {
    return reponse(config, listerTypesLogement())
  }

  const arboMatch = url.match(/^\/referentiels\/chantiers\/([^/]+)\/arborescence$/)
  if (methode === 'get' && arboMatch) {
    const arbre = construireArborescence(arboMatch[1] ?? '')
    return arbre ? reponse(config, arbre) : reponse(config, null, 404)
  }

  const chantierMatch = url.match(/^\/referentiels\/chantiers\/([^/]+)$/)
  if (methode === 'put' && chantierMatch) {
    const chantier = modifierChantierMock(chantierMatch[1] ?? '', corpsJson(config))
    return chantier ? reponse(config, chantier) : reponse(config, null, 404)
  }

  if (methode === 'post' && url === '/referentiels/zones') {
    return reponse(config, creerZoneMock(corpsJson(config)), 201)
  }

  const zoneMatch = url.match(/^\/referentiels\/zones\/([^/]+)$/)
  if (methode === 'put' && zoneMatch) {
    const zone = modifierZoneMock(zoneMatch[1] ?? '', corpsJson(config))
    return zone ? reponse(config, zone) : reponse(config, null, 404)
  }

  if (methode === 'post' && url === '/referentiels/logements') {
    return reponse(config, creerLogementMock(corpsJson(config)), 201)
  }

  const logementMatch = url.match(/^\/referentiels\/logements\/([^/]+)$/)
  if (methode === 'put' && logementMatch) {
    const logement = modifierLogementMock(logementMatch[1] ?? '', corpsJson(config))
    return logement ? reponse(config, logement) : reponse(config, null, 404)
  }

  return undefined
}
