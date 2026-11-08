/*
  Branchement de l'adaptateur de simulation.

  Appelé une fois au démarrage (`main.tsx`), piloté par `VITE_USE_MOCKS`. Quand
  les mocks sont actifs, l'adaptateur du client axios partagé est remplacé ;
  sinon, le client garde son transport réseau par défaut et parle à l'API Django
  réelle. Le basculement ne modifie aucun écran ni aucune fonction d'API.

  Règle de défaut : tant que le backend Django n'existe pas, la simulation doit
  fonctionner sans configuration. La variable est donc interprétée ainsi :
  - « true »  : simulation active (en développement comme en production) ;
  - « false » : simulation désactivée, le client cible l'API réelle ;
  - non définie : simulation active EN DÉVELOPPEMENT seulement. En production,
    l'absence de la variable laisse la simulation inactive, pour ne jamais
    livrer de données de démonstration par mégarde.
  Ce choix évite qu'un oubli de fichier `.env` fasse paraître l'application
  cassée en local, sans risque de fuite des données de démo dans une build.
*/

import { http } from '@/lib/api/http'
import { adaptateurMock } from '@/lib/mocks/adaptateur'

/** Vrai si la simulation doit être branchée (voir la règle de défaut ci-dessus). */
export function mocksActifs(): boolean {
  const valeur = import.meta.env.VITE_USE_MOCKS
  if (valeur === 'true') {
    return true
  }
  if (valeur === 'false') {
    return false
  }
  // Variable non définie : active en développement, inactive en production.
  return import.meta.env.DEV
}

/** Installe l'adaptateur de simulation sur le client partagé, si demandé. */
export function installerMocks(): void {
  if (mocksActifs()) {
    http.defaults.adapter = adaptateurMock
  }
}
