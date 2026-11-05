import { createContext, useContext } from 'react'

/** Tonalité d'une notification brève. */
export type TonToast = 'information' | 'succes' | 'alerte' | 'danger'

export type OptionsToast = {
  /** Phrase principale, au passé : « Fiche de route enregistrée ». */
  titre: string
  /** Précision facultative sur une ligne. */
  message?: string
  /** Tonalité. `information` par défaut. */
  ton?: TonToast
  /** Durée d'affichage en millisecondes. `0` maintient la notification. */
  dureeMs?: number
}

/** Notification en file d'attente, identifiée par le fournisseur. */
export type ToastEnregistre = OptionsToast & { id: string }

export type ToastContexteValeur = {
  /** Empile une notification et renvoie son identifiant. */
  afficherToast: (options: OptionsToast) => string
  /** Referme une notification avant la fin de sa durée d'affichage. */
  fermerToast: (id: string) => void
}

export const ToastContexte = createContext<ToastContexteValeur | null>(null)

export function useToast(): ToastContexteValeur {
  const contexte = useContext(ToastContexte)

  if (!contexte) {
    throw new Error("useToast doit être utilisé à l'intérieur de ToastProvider.")
  }

  return contexte
}
