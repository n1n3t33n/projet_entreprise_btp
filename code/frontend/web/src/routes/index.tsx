
import { createBrowserRouter } from 'react-router-dom'
import { App } from '@/app/App'
import { DesignSystemPage } from '@/theme/DesignSystemPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
  },
  {
    path: '/design-system',
    element: <DesignSystemPage />,
  },
])
