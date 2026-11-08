/*
  Adaptateur de simulation pour axios.

  Remplace le transport réseau du client partagé par une table de routes servie
  depuis les données de Grand-Bassam. Les composants et la couche `api` ne
  changent pas : seul le client sait qu'il répond en local. Une courte latence
  est ajoutée pour que les écrans exercent leurs états d'attente.
*/

import type { AxiosAdapter, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import {
  appliquerMouvement,
  construireArborescence,
  construireLignesStock,
  definirSeuilsMock,
  listerMouvementsArticle,
  MAGASIN_PILOTE,
  TYPES_MOUVEMENT,
  type EntreeMouvementMock,
} from '@/lib/mocks/donnees-grand-bassam'
import { routerAvancement } from '@/lib/mocks/adaptateur-avancement'
import { routerReferentiels } from '@/lib/mocks/adaptateur-referentiels'

const LATENCE_MS = 280

function attendre(ms: number): Promise<void> {
  return new Promise((resoudre) => {
    setTimeout(resoudre, ms)
  })
}

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

/**
 * Résout une requête contre les données de démonstration.
 *
 * Renvoie `undefined` si aucune route ne correspond, pour que l'appelant
 * signale une route non simulée.
 */
function router(config: InternalAxiosRequestConfig): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  if (methode === 'get' && url === '/magasins') {
    return reponse(config, [MAGASIN_PILOTE])
  }

  if (methode === 'get' && url === '/types-mouvement') {
    return reponse(config, TYPES_MOUVEMENT)
  }

  if (methode === 'get' && url === '/stock/arborescence') {
    return reponse(config, construireArborescence())
  }

  if (methode === 'get' && /^\/magasins\/[^/]+\/stock$/.test(url)) {
    return reponse(config, construireLignesStock())
  }

  const mouvementsMatch = url.match(/^\/magasins\/[^/]+\/articles\/([^/]+)\/mouvements$/)
  if (methode === 'get' && mouvementsMatch) {
    const idArticle = mouvementsMatch[1] ?? ''
    return reponse(config, listerMouvementsArticle(idArticle))
  }

  if (methode === 'post' && url === '/mouvements') {
    const corps = corpsJson(config)
    const entree: EntreeMouvementMock = {
      article_id_article: texte(corps.article_id_article),
      magasin_id_magasin: texte(corps.magasin_id_magasin),
      type_mouvement_code_type_mouvement: texte(corps.type_mouvement_code_type_mouvement),
      quantite_saisie: texte(corps.quantite_saisie),
      logement_id_logement: typeof corps.logement_id_logement === 'string'
        ? corps.logement_id_logement
        : null,
      reference_externe: typeof corps.reference_externe === 'string'
        ? corps.reference_externe
        : null,
      motif: typeof corps.motif === 'string' ? corps.motif : null,
    }
    return reponse(config, appliquerMouvement(entree), 201)
  }

  const seuilMatch = url.match(/^\/magasins\/[^/]+\/articles\/([^/]+)\/seuil$/)
  if (methode === 'put' && seuilMatch) {
    const corps = corpsJson(config)
    const idArticle = seuilMatch[1] ?? ''
    definirSeuilsMock(
      idArticle,
      Number.parseFloat(texte(corps.seuil_minimal)) || 0,
      Number.parseFloat(texte(corps.seuil_critique)) || 0,
    )
    return reponse(config, null, 204)
  }

  return undefined
}

export const adaptateurMock: AxiosAdapter = async (config) => {
  await attendre(LATENCE_MS)
  // On essaie successivement les routes du stock, de l'avancement puis des
  // référentiels : chaque module apporte sa table de routes, le client reste
  // unique.
  const resultat = router(config) ?? routerAvancement(config) ?? routerReferentiels(config)
  if (!resultat) {
    throw new Error(`Route non simulée : ${config.method?.toUpperCase()} ${config.url}`)
  }
  return resultat
}
