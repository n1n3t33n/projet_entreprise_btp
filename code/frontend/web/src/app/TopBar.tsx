import { Bell, CaretDown, MagnifyingGlass, MapPin, Question } from '@phosphor-icons/react'
import { useLocation } from 'react-router-dom'
import { ROLES, useRole, type Role } from '@/app/role-context'
import { navigation } from '@/config/navigation'

export function TopBar() {
  const { role, definirRole } = useRole()
  const location = useLocation()
  const entreeCourante = navigation.find((entree) => entree.chemin === location.pathname)

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
          placeholder="Rechercher un lot, un rapport, un jalon…"
          aria-label="Rechercher"
          className="w-full rounded-controle border border-bordure bg-fond py-2 pl-10 pr-3 text-sm text-texte placeholder:text-texte-attenue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        />
      </div>

      <div className="ml-auto flex items-center gap-2">
        <label className="flex items-center gap-2 rounded-controle border border-bordure px-2.5 py-1.5">
          <span className="text-xs text-texte-secondaire">Rôle</span>
          <select
            value={role}
            onChange={(event) => definirRole(event.target.value as Role)}
            aria-label="Aperçu par rôle"
            className="bg-transparent text-sm font-medium text-texte focus-visible:outline-none"
          >
            {ROLES.map((item) => (
              <option key={item.value} value={item.value}>
                {item.libelle}
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          aria-label="Sélectionner un chantier"
          className="flex items-center gap-2 rounded-controle border border-bordure px-3 py-2 text-sm font-medium text-texte transition-colors duration-150 hover:bg-fond focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        >
          <MapPin size={18} weight="regular" aria-hidden className="text-sarcelle" />
          <span>Chantier</span>
          <CaretDown size={14} weight="regular" aria-hidden className="text-texte-secondaire" />
        </button>

        <button
          type="button"
          aria-label="Notifications"
          className="rounded-controle p-2 text-texte-secondaire transition-colors duration-150 hover:bg-fond focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        >
          <Bell size={20} weight="regular" aria-hidden />
        </button>

        <button
          type="button"
          aria-label="Aide"
          className="rounded-controle p-2 text-texte-secondaire transition-colors duration-150 hover:bg-fond focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        >
          <Question size={20} weight="regular" aria-hidden />
        </button>
      </div>
    </header>
  )
}
