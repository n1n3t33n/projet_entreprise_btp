/*
  Table de routes de simulation du domaine « appareils enrôlés ». Renvoie
  `undefined` si aucune route ne correspond, pour laisser la main à l'appelant.

  La révocation (SQ-5 étape 12 : « blocage serveur immédiat et journalisation »)
  consigne en même temps une entrée dans le journal d'audit (EF-AUT-08) : c'est
  le serveur qui trace l'action, l'écran n'a rien à faire de plus. La
  simulation reproduit ce couplage en écrivant dans le même magasin d'audit que
  celui lu par l'écran « Journal d'audit ».
*/

import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { listerAppareils, revoquerAppareilMock } from '@/lib/mocks/appareils-grand-bassam'
import { consignerAudit } from '@/lib/mocks/audit-grand-bassam'

function reponse<T>(config: InternalAxiosRequestConfig, data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: status === 204 ? 'No Content' : 'OK',
    headers: {},
    config,
  } as AxiosResponse<T>
}

export function routerAppareils(
  config: InternalAxiosRequestConfig,
): AxiosResponse<unknown> | undefined {
  const methode = (config.method ?? 'get').toLowerCase()
  const url = config.url ?? ''

  if (methode === 'get' && url === '/appareils') {
    return reponse(config, listerAppareils())
  }

  const revocationMatch = url.match(/^\/appareils\/([^/]+)\/revocation$/)
  if (methode === 'post' && revocationMatch) {
    const id = revocationMatch[1] ?? ''
    const appareil = revoquerAppareilMock(id)
    if (!appareil) {
      return reponse(config, { message: 'Appareil introuvable.' }, 404)
    }
    // Journalisation de l'action d'administration (EF-AUT-08, SQ-5 étape 12).
    consignerAudit({
      action: 'REVOCATION_APPAREIL',
      typeObjet: 'appareil',
      idObjet: appareil.id_appareil,
      resume: `Révocation de l'appareil ${appareil.empreinte_materiel} (${appareil.nom_utilisateur})`,
    })
    return reponse(config, appareil)
  }

  return undefined
}
