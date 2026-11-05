import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { DUREE_SORTIE_MS } from '@/components/ui/motion'
import { Toast } from '@/components/ui/Toast'
import {
  ToastContexte,
  type OptionsToast,
  type ToastEnregistre,
} from '@/components/ui/toast-context'

const DUREE_PAR_DEFAUT_MS = 5000

/** Compteur de module : garantit un identifiant unique sans dépendance externe. */
let compteurToast = 0

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastEnregistre[]>([])
  const [sortants, setSortants] = useState<string[]>([])
  const minuteurs = useRef<Map<string, number>>(new Map())

  const annulerMinuteur = useCallback((id: string) => {
    const minuteur = minuteurs.current.get(id)
    if (minuteur !== undefined) {
      window.clearTimeout(minuteur)
      minuteurs.current.delete(id)
    }
  }, [])

  const retirer = useCallback(
    (id: string) => {
      annulerMinuteur(id)
      setToasts((liste) => liste.filter((toast) => toast.id !== id))
      setSortants((liste) => liste.filter((identifiant) => identifiant !== id))
    },
    [annulerMinuteur],
  )

  const fermerToast = useCallback(
    (id: string) => {
      annulerMinuteur(id)
      setSortants((liste) => (liste.includes(id) ? liste : [...liste, id]))
      minuteurs.current.set(
        id,
        window.setTimeout(() => retirer(id), DUREE_SORTIE_MS),
      )
    },
    [annulerMinuteur, retirer],
  )

  const afficherToast = useCallback(
    (options: OptionsToast) => {
      compteurToast += 1
      const id = `toast-${compteurToast}`

      setToasts((liste) => [...liste, { ...options, id }])

      const duree = options.dureeMs ?? DUREE_PAR_DEFAUT_MS
      if (duree > 0) {
        minuteurs.current.set(
          id,
          window.setTimeout(() => fermerToast(id), duree),
        )
      }

      return id
    },
    [fermerToast],
  )

  // Un démontage pendant qu'une notification est encore affichée laisserait des
  // minuteurs actifs, qui tenteraient de modifier un état disparu.
  useEffect(() => {
    const minuteursActifs = minuteurs.current
    return () => {
      minuteursActifs.forEach((minuteur) => window.clearTimeout(minuteur))
      minuteursActifs.clear()
    }
  }, [])

  const valeur = useMemo(() => ({ afficherToast, fermerToast }), [afficherToast, fermerToast])

  return (
    <ToastContexte.Provider value={valeur}>
      {children}

      {/* La pile de notifications est rendue par un portail : elle doit rester
          au-dessus des tiroirs et des modales, sans dépendre du contexte
          d'empilement de l'écran qui l'a déclenchée. */}
      {createPortal(
        <div
          role="region"
          aria-label="Notifications"
          aria-live="polite"
          className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-full max-w-sm flex-col gap-3"
        >
          {toasts.map((toast) => (
            <Toast
              key={toast.id}
              titre={toast.titre}
              message={toast.message}
              ton={toast.ton}
              sortie={sortants.includes(toast.id)}
              onFermer={() => fermerToast(toast.id)}
              className="pointer-events-auto"
            />
          ))}
        </div>,
        document.body,
      )}
    </ToastContexte.Provider>
  )
}
