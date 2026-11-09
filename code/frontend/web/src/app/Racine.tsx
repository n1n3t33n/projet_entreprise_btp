/*
  Racine de l'application.

  Elle porte ce qui vaut avant toute connexion : la session et les messages
  éphémères. L'écran de connexion et la coquille applicative sont ses deux
  enfants, de sorte que la page de connexion dispose elle aussi du contexte de
  session et des notifications.
*/

import { Outlet } from 'react-router-dom'
import { SessionProvider } from '@/app/SessionProvider'
import { ToastProvider } from '@/components/ui'
import { PARAMETRES_PAR_DEFAUT } from '@/config/parametres'

export function Racine() {
  return (
    <SessionProvider>
      <ToastProvider dureeParDefautMs={PARAMETRES_PAR_DEFAUT.notifications.dureeToastMs}>
        <Outlet />
      </ToastProvider>
    </SessionProvider>
  )
}
