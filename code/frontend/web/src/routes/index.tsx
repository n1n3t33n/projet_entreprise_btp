/*
  Routes du poste de pilotage.

  - Chaque écran est enveloppé par `EcranProtege`, qui applique la matrice
    d'accès de `config/navigation` : l'adresse ne contourne plus le menu.
  - La racine redirige vers l'écran d'accueil du rôle courant.
  - Les modules métier sont chargés à la demande (`lazy`) : le premier
    chargement n'embarque que la coquille, chaque module arrive quand on
    l'ouvre. Cela ramène le paquet initial sous le seuil d'alerte de Vite.
*/

import { lazy, Suspense, type ReactNode } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import { App } from '@/app/App'
import { Racine } from '@/app/Racine'
import { ChargementModule } from '@/app/ChargementModule'
import { EcranProtege, RedirectionAccueil } from '@/app/EcranProtege'
import { PageEnPreparation } from '@/components/ui/PageEnPreparation'
import type { IdEcran } from '@/config/navigation'

const PageTableauDeBord = lazy(() =>
  import('@/features/pilotage').then((module) => ({ default: module.PageTableauDeBord })),
)
const PageJournalExecution = lazy(() =>
  import('@/features/pilotage').then((module) => ({ default: module.PageJournalExecution })),
)
const PageAvancement = lazy(() =>
  import('@/features/avancement').then((module) => ({ default: module.PageAvancement })),
)
const PageStock = lazy(() =>
  import('@/features/stock').then((module) => ({ default: module.PageStock })),
)
const PageReferentiels = lazy(() =>
  import('@/features/referentiels').then((module) => ({ default: module.PageReferentiels })),
)
const PageGammes = lazy(() =>
  import('@/features/gammes').then((module) => ({ default: module.PageGammes })),
)
const PageParametrage = lazy(() =>
  import('@/features/parametrage').then((module) => ({ default: module.PageParametrage })),
)
const PageConnexion = lazy(() =>
  import('@/features/auth').then((module) => ({ default: module.PageConnexion })),
)
const PageAdministration = lazy(() =>
  import('@/features/admin').then((module) => ({ default: module.PageAdministration })),
)
const PageEquipes = lazy(() =>
  import('@/features/equipes').then((module) => ({ default: module.PageEquipes })),
)
const PageEspaceAcquereur = lazy(() =>
  import('@/features/acquereur').then((module) => ({ default: module.PageEspaceAcquereur })),
)
const DesignSystemPage = lazy(() =>
  import('@/theme/DesignSystemPage').then((module) => ({ default: module.DesignSystemPage })),
)
const UiKitPage = lazy(() =>
  import('@/theme/UiKitPage').then((module) => ({ default: module.UiKitPage })),
)

/** Écran protégé par la matrice d'accès, avec chargement à la demande. */
function ecran(id: IdEcran, contenu: ReactNode) {
  return (
    <EcranProtege ecran={id}>
      <Suspense fallback={<ChargementModule />}>{contenu}</Suspense>
    </EcranProtege>
  )
}

export const router = createBrowserRouter([
  {
    element: <Racine />,
    children: [
      {
        path: '/connexion',
        element: (
          <Suspense fallback={<ChargementModule />}>
            <PageConnexion />
          </Suspense>
        ),
      },
      {
        element: <App />,
        children: [
          { index: true, element: <RedirectionAccueil /> },
          { path: '/tableau-de-bord', element: ecran('tableau-de-bord', <PageTableauDeBord />) },
          { path: '/avancement', element: ecran('avancement', <PageAvancement />) },
          { path: '/journal', element: ecran('journal', <PageJournalExecution />) },
          { path: '/stock', element: ecran('stock', <PageStock />) },
          { path: '/referentiels', element: ecran('referentiels', <PageReferentiels />) },
          { path: '/gammes', element: ecran('gammes', <PageGammes />) },
          { path: '/equipes', element: ecran('equipes', <PageEquipes />) },
          { path: '/parametrage', element: ecran('parametrage', <PageParametrage />) },
          {
            path: '/administration',
            element: ecran('administration', <PageAdministration />),
          },
          {
            path: '/synchronisation',
            element: ecran('synchronisation', <PageEnPreparation titre="Synchronisation" />),
          },
          {
            path: '/espace-acquereur',
            element: ecran('espace-acquereur', <PageEspaceAcquereur />),
          },
          // Toute adresse inconnue ramène à l'accueil du rôle plutôt qu'à une page vide.
          { path: '*', element: <RedirectionAccueil /> },
        ],
      },
    ],
  },
  {
    path: '/design-system',
    element: (
      <Suspense fallback={<ChargementModule />}>
        <DesignSystemPage />
      </Suspense>
    ),
  },
  {
    path: '/ui-kit',
    element: (
      <Suspense fallback={<ChargementModule />}>
        <UiKitPage />
      </Suspense>
    ),
  },
])
