import { createBrowserRouter, Navigate } from 'react-router-dom'
import { App } from '@/app/App'
import { PageEnPreparation } from '@/components/ui/PageEnPreparation'
import { PageStock } from '@/features/stock'
import { DesignSystemPage } from '@/theme/DesignSystemPage'
import { UiKitPage } from '@/theme/UiKitPage'

export const router = createBrowserRouter([
  {
    element: <App />,
    children: [
      { index: true, element: <Navigate to="/tableau-de-bord" replace /> },
      { path: '/tableau-de-bord', element: <PageEnPreparation titre="Tableau de bord" /> },
      { path: '/avancement', element: <PageEnPreparation titre="Avancement" /> },
      { path: '/stock', element: <PageStock /> },
      { path: '/referentiels', element: <PageEnPreparation titre="Référentiels" /> },
      { path: '/administration', element: <PageEnPreparation titre="Administration" /> },
      { path: '/synchronisation', element: <PageEnPreparation titre="Synchronisation" /> },
      { path: '/espace-acquereur', element: <PageEnPreparation titre="Espace acquéreur" /> },
    ],
  },
  {
    path: '/design-system',
    element: <DesignSystemPage />,
  },
  {
    path: '/ui-kit',
    element: <UiKitPage />,
  },
])
