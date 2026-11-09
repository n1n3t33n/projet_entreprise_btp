import { Bell, MagnifyingGlass, MapPin, Question } from '@phosphor-icons/react'
import { useLocation } from 'react-router-dom'
import { libelleRole, useRole } from '@/app/role-context'
import { ECRANS } from '@/config/navigation'

/** Chantier unique du pilote (hypothèse H2 du cahier des charges). */
const CHANTIER_PILOTE = 'Chantier de Grand-Bassam'

export function TopBar() {
  const { role } = useRole()
  const location = useLocation()
  const entreeCourante = ECRANS.find((entree) => entree.chemin === location.pathname)

  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b border-bordure bg-surface px-6">
      <h1 className="text-lg font-semibold text-marine">{entreeCourante?.libelle ?? ''}</h1>

      <div className="relative ml-4 hidden max-w-sm flex-1 md:block">
        <MagnifyingGlass
          size={18}
          weight="regular"
          aria-hidden
          className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-texte-attenue"
        />
        <input
          type="search"
          placeholder="Recherche globale — bientôt disponible"
          aria-label="Recherche globale (bientôt disponible)"
          disabled
          title="La recherche globale n'est pas encore disponible."
          className="w-full rounded-controle border border-bordure bg-fond py-2 pl-10 pr-3 text-sm text-texte placeholder:text-texte-attenue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle disabled:cursor-not-allowed disabled:opacity-60"
        />
      </div>

      <div className="ml-auto flex items-center gap-2">
        <span className="flex items-center gap-2 rounded-controle border border-bordure px-3 py-1.5">
          <span className="text-xs text-texte-secondaire">Rôle</span>
          <span className="text-sm font-medium text-texte">{libelleRole(role)}</span>
        </span>

        {/* Le pilote porte un seul chantier (cahier des charges, hypothèse H2) :
            une étiquette fixe plutôt qu'un menu qui ne proposerait rien. */}
        <span
          className="flex items-center gap-2 rounded-controle border border-bordure px-3 py-2 text-sm font-medium text-texte"
          title="Chantier pilote"
        >
          <MapPin size={18} weight="regular" aria-hidden className="text-sarcelle" />
          <span>{CHANTIER_PILOTE}</span>
        </span>

        <button
          type="button"
          aria-label="Notifications (bientôt disponible)"
          title="Notifications : bientôt disponible"
          disabled
          className="rounded-controle p-2 disabled:cursor-not-allowed disabled:opacity-50 text-texte-secondaire transition-colors duration-150 hover:bg-fond focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        >
          <Bell size={20} weight="regular" aria-hidden />
        </button>

        <button
          type="button"
          aria-label="Aide (bientôt disponible)"
          title="Aide : bientôt disponible"
          disabled
          className="rounded-controle p-2 disabled:cursor-not-allowed disabled:opacity-50 text-texte-secondaire transition-colors duration-150 hover:bg-fond focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        >
          <Question size={20} weight="regular" aria-hidden />
        </button>
      </div>
    </header>
  )
}
