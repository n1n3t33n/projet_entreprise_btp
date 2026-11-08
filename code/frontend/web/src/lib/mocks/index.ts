/*
  Branchement de l'adaptateur de simulation.

  Appelé une fois au démarrage (`main.tsx`), piloté par `VITE_USE_MOCKS`. Quand
  les mocks sont actifs, l'adaptateur du client axios partagé est remplacé ;
  sinon, le client garde son transport réseau par défaut et parle à l'API Django
  réelle. Le basculement ne modifie aucun écran ni aucune fonction d'API.
*/

import { http } from '@/lib/api/http'
import { adaptateurMock } from '@/lib/mocks/adaptateur'

/** Vrai si la variable d'environnement demande les données de démonstration. */
export function mocksActifs(): boolean {
  return import.meta.env.VITE_USE_MOCKS === 'true'
}

/** Installe l'adaptateur de simulation sur le client partagé, si demandé. */
export function installerMocks(): void {
  if (mocksActifs()) {
    http.defaults.adapter = adaptateurMock
  }
}
