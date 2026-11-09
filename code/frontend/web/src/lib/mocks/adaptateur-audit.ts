/*
  Table de routes de simulation du journal d'audit (EF-AUT-08). Lecture seule
  (le journal est immuable, RG-S8) : la seule écriture possible est l'ajout fait
  par les autres routes via `consignerAudit`, jamais par une requête de cet
  écran. Renvoie `undefined` si aucune route ne correspond.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { listerAudit } from '@/lib/mocks/audit-grand-bassam'

function reponse<T>(config: InternalAxiosRequestConfig, data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: 'OK',
    headers: {},
    config,
  } as AxiosResponse<T>
}

export function routerAudit(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = (config.url ?? '').split('?')[0]

  if (methode === 'get' && url === '/audit') {
    const params = (config.params ?? {}) as Record<string, unknown>
    const actionFiltre = typeof params.action === 'string' ? params.action : null
    const auteurFiltre = typeof params.auteur === 'string' ? params.auteur : null

    let entrees = listerAudit()
    if (actionFiltre) {
      entrees = entrees.filter((entree) => entree.action === actionFiltre)
    }
    if (auteurFiltre) {
      entrees = entrees.filter((entree) => entree.utilisateur_id_utilisateur === auteurFiltre)
    }
    return reponse(config, entrees)
  }

  return undefined
}
