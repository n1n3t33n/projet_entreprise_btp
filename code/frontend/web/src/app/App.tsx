/*
  Coquille du poste de pilotage, réservée aux sessions ouvertes.

  Sans session, toute adresse renvoie vers l'écran de connexion : la coquille
  n'est jamais rendue, donc aucun appel de données n'est émis pour un visiteur
  non connecté. Les droits ne sont chargés qu'ensuite, pour le compte connecté.
*/

import { Navigate, Outlet } from 'react-router-dom'
import { DroitsProvider } from '@/app/DroitsProvider'
import { Sidebar } from '@/app/Sidebar'
import { TopBar } from '@/app/TopBar'
import { useSession } from '@/app/session-context'

export function App() {
  const { connecte } = useSession()

  if (!connecte) {
    return <Navigate to="/connexion" replace />
  }

  return (
    <DroitsProvider>
      <div className="flex h-dvh overflow-hidden bg-fond">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar />
          <main className="flex-1 overflow-y-auto px-6 py-6">
            <Outlet />
          </main>
        </div>
      </div>
    </DroitsProvider>
  )
}
