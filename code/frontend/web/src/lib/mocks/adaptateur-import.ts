/*
  Table de routes de simulation de l'import CSV des référentiels (EF-ADM-02).
  Renvoie `undefined` si aucune route ne correspond.

  La confirmation d'un import est une action d'administration : elle est
  journalisée (EF-AUT-08), comme la révocation d'un appareil.
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  analyserImportMock,
  confirmerImportMock,
} from '@/lib/mocks/import-csv-grand-bassam'
import { consignerAudit } from '@/lib/mocks/audit-grand-bassam'
import type { CibleImport } from '@/features/admin/types/import-csv'

function reponse<T>(config: InternalAxiosRequestConfig, data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: 'OK',
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

const CIBLES: CibleImport[] = ['articles', 'magasins', 'chantiers']

function cibleValide(valeur: unknown): CibleImport | null {
  return typeof valeur === 'string' && (CIBLES as string[]).includes(valeur)
    ? (valeur as CibleImport)
    : null
}

const LIBELLE_CIBLE: Record<CibleImport, string> = {
  articles: 'articles',
  magasins: 'magasins',
  chantiers: 'chantiers et zones',
}

export function routerImport(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  if (methode === 'post' && url === '/import/analyse') {
    const corps = corpsJson(config)
    const cible = cibleValide(corps.cible)
    const contenu = typeof corps.contenu === 'string' ? corps.contenu : ''
    if (!cible) {
      return reponse(config, { message: 'Cible inconnue.' }, 400)
    }
    return reponse(config, analyserImportMock(cible, contenu))
  }

  if (methode === 'post' && url === '/import/confirmation') {
    const corps = corpsJson(config)
    const cible = cibleValide(corps.cible)
    const contenu = typeof corps.contenu === 'string' ? corps.contenu : ''
    if (!cible) {
      return reponse(config, { message: 'Cible inconnue.' }, 400)
    }
    const nombre = confirmerImportMock(cible, contenu)
    consignerAudit({
      action: 'IMPORT_CSV',
      typeObjet: 'referentiel',
      idObjet: cible,
      resume: `Import de ${nombre} ${LIBELLE_CIBLE[cible]} par fichier CSV`,
    })
    return reponse(config, { cible, nombre_importees: nombre })
  }

  return undefined
}
