import { CircleNotch, type Icon } from '@phosphor-icons/react'
import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/cn'

/** Niveau hiérarchique du bouton dans un écran. */
export type VarianteBouton = 'primaire' | 'secondaire' | 'discret' | 'danger'

/** Gabarit du bouton. */
export type TailleBouton = 'sm' | 'md' | 'lg'

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  /** Niveau hiérarchique. Un seul bouton primaire par zone d'écran. */
  variante?: VarianteBouton
  /** Gabarit. `md` par défaut. */
  taille?: TailleBouton
  /** Icône Phosphor facultative, purement décorative. */
  icone?: Icon
  /** Côté de l'icône par rapport au libellé. */
  positionIcone?: 'avant' | 'apres'
  /** Remplace l'icône par un indicateur d'attente et neutralise le bouton. */
  enChargement?: boolean
  /** Occupe toute la largeur disponible. */
  pleineLargeur?: boolean
  /** Libellé du bouton. Obligatoire sauf si `aria-label` est fourni. */
  children?: ReactNode
}

const PAR_VARIANTE: Record<VarianteBouton, string> = {
  primaire: 'bg-marine text-white shadow-douce hover:bg-marine/90 active:bg-marine',
  secondaire: 'border border-bordure bg-surface text-texte hover:bg-fond active:bg-fond-alt',
  discret: 'text-texte-secondaire hover:bg-fond hover:text-texte active:bg-fond-alt',
  danger: 'bg-danger text-white shadow-douce hover:bg-danger/90 active:bg-danger',
}

const PAR_TAILLE: Record<TailleBouton, string> = {
  sm: 'h-8 gap-1.5 px-3 text-xs',
  md: 'h-10 gap-2 px-4 text-sm',
  lg: 'h-12 gap-2.5 px-5 text-base',
}

const TAILLE_ICONE: Record<TailleBouton, number> = {
  sm: 14,
  md: 18,
  lg: 20,
}

export function Button({
  variante = 'secondaire',
  taille = 'md',
  icone,
  positionIcone = 'avant',
  enChargement = false,
  pleineLargeur = false,
  children,
  className,
  disabled,
  type = 'button',
  ...reste
}: ButtonProps) {
  const neutralise = disabled === true || enChargement
  const Icone = icone
  const dimensionIcone = TAILLE_ICONE[taille]

  const indicateur = enChargement ? (
    <CircleNotch size={dimensionIcone} weight="bold" aria-hidden className="animate-spin" />
  ) : Icone ? (
    <Icone size={dimensionIcone} weight="regular" aria-hidden />
  ) : null

  return (
    <button
      type={type}
      disabled={neutralise}
      aria-busy={enChargement || undefined}
      className={cn(
        'inline-flex shrink-0 items-center justify-center rounded-controle font-semibold',
        'transition-[background-color,border-color,box-shadow,transform] ease-out',
        'duration-[var(--duree-bouton)]',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle',
        'focus-visible:ring-offset-2 focus-visible:ring-offset-surface',
        'active:scale-[0.98] motion-reduce:active:scale-100',
        'disabled:pointer-events-none disabled:opacity-50',
        PAR_VARIANTE[variante],
        PAR_TAILLE[taille],
        pleineLargeur && 'w-full',
        className,
      )}
      {...reste}
    >
      {positionIcone === 'avant' && indicateur}
      {children}
      {positionIcone === 'apres' && indicateur}
    </button>
  )
}
