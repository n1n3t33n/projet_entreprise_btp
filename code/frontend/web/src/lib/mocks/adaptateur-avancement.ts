/*
  Table de routes de simulation du module avancement. Résout une requête contre
  les données de Grand-Bassam ; renvoie `undefined` si aucune route ne
  correspond, pour laisser la main à l'appelant.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  appliquerBlocage,
  appliquerValidation,
  construireEtapesAValider,
  construireEtapesLogement,
  construireLignesLogement,
  construireSynthese,
  listerEvenementsEtape,
  MOTIFS_BLOCAGE,
  ZONES,
} from '@/lib/mocks/avancement-grand-bassam'

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

function texte(valeur: unknown): string {
  return typeof valeur === 'string' ? valeur : ''
}

export function routerAvancement(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  if (methode === 'get' && url === '/avancement/zones') {
    return reponse(config, ZONES)
  }
  if (methode === 'get' && url === '/avancement/synthese') {
    return reponse(config, construireSynthese())
  }
  if (methode === 'get' && url === '/avancement/logements') {
    return reponse(config, construireLignesLogement())
  }
  if (methode === 'get' && url === '/avancement/etapes-a-valider') {
    return reponse(config, construireEtapesAValider())
  }
  if (methode === 'get' && url === '/motifs-blocage') {
    return reponse(config, MOTIFS_BLOCAGE)
  }

  const etapesMatch = url.match(/^\/logements\/([^/]+)\/etapes$/)
  if (methode === 'get' && etapesMatch) {
    return reponse(config, construireEtapesLogement(etapesMatch[1] ?? ''))
  }

  const evenementsMatch = url.match(/^\/etapes\/([^/]+)\/evenements$/)
  if (methode === 'get' && evenementsMatch) {
    return reponse(config, listerEvenementsEtape(evenementsMatch[1] ?? ''))
  }

  const validationMatch = url.match(/^\/etapes\/([^/]+)\/validation$/)
  if (methode === 'post' && validationMatch) {
    const corps = corpsJson(config)
    const decision = texte(corps.decision) === 'rejeter' ? 'rejeter' : 'valider'
    const motif = typeof corps.motif === 'string' ? corps.motif : null
    const evenement = appliquerValidation(validationMatch[1] ?? '', decision, motif)
    if (!evenement) {
      throw new Error("Cette étape n'est plus en attente de validation.")
    }
    return reponse(config, evenement, 201)
  }

  const blocageMatch = url.match(/^\/etapes\/([^/]+)\/blocage$/)
  if (methode === 'post' && blocageMatch) {
    const corps = corpsJson(config)
    const commentaire = typeof corps.commentaire === 'string' ? corps.commentaire : null
    const evenement = appliquerBlocage(blocageMatch[1] ?? '', texte(corps.code_motif), commentaire)
    if (!evenement) {
      throw new Error("Cette étape ne peut pas être déclarée bloquée dans son état actuel.")
    }
    return reponse(config, evenement, 201)
  }

  return undefined
}
