import { Warning } from '@phosphor-icons/react'
import {
  useId,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
  type TextareaHTMLAttributes,
} from 'react'
import { cn } from '@/lib/cn'

/**
 * Attributs à reporter sur le contrôle de saisie.
 *
 * `FormField` fabrique les identifiants et les relations ARIA, puis les confie
 * au contrôle : c'est ce qui garantit qu'un lecteur d'écran annonce le libellé,
 * l'aide et l'erreur ensemble, sans que l'écran appelant ait à les recâbler.
 */
export type ProprietesChamp = {
  id: string
  'aria-describedby': string | undefined
  'aria-invalid': boolean | undefined
  'aria-required': boolean | undefined
}

export type FormFieldProps = {
  /** Libellé visible. Jamais remplacé par un texte indicatif seul. */
  libelle: string
  /**
   * Contrôle de saisie, écrit comme une fonction qui reçoit les attributs à
   * reporter : `{(champ) => <Input {...champ} />}`.
   */
  children: (champ: ProprietesChamp) => ReactNode
  /** Identifiant imposé. Un identifiant unique est généré si rien n'est fourni. */
  id?: string
  /** Consigne de saisie affichée sous le contrôle. */
  aide?: string
  /** Message d'erreur affiché sous le contrôle, à la place de l'aide. */
  erreur?: string
  /** Marque le champ comme obligatoire. */
  requis?: boolean
  className?: string
}

export function FormField({
  libelle,
  children,
  id,
  aide,
  erreur,
  requis = false,
  className,
}: FormFieldProps) {
  const identifiantGenere = useId()
  const idChamp = id ?? identifiantGenere
  const idAide = `${idChamp}-aide`
  const idErreur = `${idChamp}-erreur`

  const descriptions = [aide ? idAide : null, erreur ? idErreur : null].filter(Boolean)

  const champ: ProprietesChamp = {
    id: idChamp,
    'aria-describedby': descriptions.length > 0 ? descriptions.join(' ') : undefined,
    'aria-invalid': erreur ? true : undefined,
    'aria-required': requis ? true : undefined,
  }

  return (
    <div className={cn('flex min-w-0 flex-col gap-1.5', className)}>
      <label htmlFor={idChamp} className="text-sm font-semibold text-texte">
        {libelle}
        {requis && (
          <span className="ml-1 text-danger" aria-hidden>
            *
          </span>
        )}
        {requis && <span className="sr-only"> (obligatoire)</span>}
      </label>

      {children(champ)}

      {aide && !erreur && (
        <p id={idAide} className="text-xs text-texte-secondaire">
          {aide}
        </p>
      )}

      {erreur && (
        <p
          id={idErreur}
          role="alert"
          className="flex items-start gap-1.5 text-xs font-medium text-danger"
        >
          <Warning size={14} weight="regular" aria-hidden className="mt-px shrink-0" />
          {erreur}
        </p>
      )}
    </div>
  )
}

const CLASSES_CONTROLE = [
  'w-full rounded-controle border bg-surface px-3 py-2 text-sm text-texte',
  'transition-colors duration-[var(--duree-survol)] ease-out placeholder:text-texte-attenue',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle',
  'disabled:cursor-not-allowed disabled:bg-fond disabled:opacity-60',
  'read-only:bg-fond read-only:text-texte-secondaire',
].join(' ')

type PropsCommunes = {
  /** Trace le contour en rouge. Positionné par `FormField` via `aria-invalid`. */
  invalide?: boolean
  /**
   * Interdit la modification tout en laissant la valeur sélectionnable et
   * copiable, contrairement à `disabled`. C'est le réglage attendu pour le
   * rôle acquéreur, qui consulte sans jamais saisir.
   */
  lectureSeule?: boolean
}

export type InputProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'readOnly'> & PropsCommunes

export function Input({ invalide = false, lectureSeule = false, className, ...reste }: InputProps) {
  return (
    <input
      readOnly={lectureSeule}
      className={cn(CLASSES_CONTROLE, invalide ? 'border-danger' : 'border-bordure', className)}
      {...reste}
    />
  )
}

export type TextareaProps = Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'readOnly'> &
  PropsCommunes

export function Textarea({
  invalide = false,
  lectureSeule = false,
  className,
  rows = 4,
  ...reste
}: TextareaProps) {
  return (
    <textarea
      rows={rows}
      readOnly={lectureSeule}
      className={cn(
        CLASSES_CONTROLE,
        'resize-y',
        invalide ? 'border-danger' : 'border-bordure',
        className,
      )}
      {...reste}
    />
  )
}

export type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  invalide?: boolean
  children: ReactNode
}

export function Select({ invalide = false, className, children, ...reste }: SelectProps) {
  return (
    <select
      className={cn(
        CLASSES_CONTROLE,
        'cursor-pointer',
        invalide ? 'border-danger' : 'border-bordure',
        className,
      )}
      {...reste}
    >
      {children}
    </select>
  )
}
