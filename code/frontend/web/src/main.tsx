import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import '@fontsource/plus-jakarta-sans/400.css'
import '@fontsource/plus-jakarta-sans/500.css'
import '@fontsource/plus-jakarta-sans/600.css'
import '@fontsource/plus-jakarta-sans/700.css'
import { installerMocks } from '@/lib/mocks'
import { router } from '@/routes'
import '@/index.css'

// Branche l'adaptateur de simulation quand VITE_USE_MOCKS=true, avant tout
// rendu : les écrans reçoivent alors les données de démonstration.
installerMocks()

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error("Élément racine introuvable : vérifier l'identifiant « root ».")
}

createRoot(rootElement).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
