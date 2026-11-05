import { Outlet } from 'react-router-dom'
import { RoleProvider } from '@/app/RoleProvider'
import { Sidebar } from '@/app/Sidebar'
import { TopBar } from '@/app/TopBar'
import { ToastProvider } from '@/components/ui'
import { PARAMETRES_PAR_DEFAUT } from '@/config/parametres'

export function App() {
  return (
    <RoleProvider>
      <ToastProvider dureeParDefautMs={PARAMETRES_PAR_DEFAUT.notifications.dureeToastMs}>
        <div className="flex h-dvh overflow-hidden bg-fond">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <TopBar />
            <main className="flex-1 overflow-y-auto px-6 py-6">
              <Outlet />
            </main>
          </div>
        </div>
      </ToastProvider>
    </RoleProvider>
  )
}
