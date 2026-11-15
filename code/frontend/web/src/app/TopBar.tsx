import { Bell, MagnifyingGlass, MapPin, Question } from '@phosphor-icons/react'
import { useLocation } from 'react-router-dom'
import { useT } from '@/app/preferences-context'
import { Reglages } from '@/app/Reglages'
import { useRole } from '@/app/role-context'
import { ECRANS } from '@/config/navigation'

export function TopBar() {
  const { role } = useRole()
  const location = useLocation()
  const t = useT()
  const entreeCourante = ECRANS.find((entree) => entree.chemin === location.pathname)

  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b border-bordure bg-surface/85 px-6 backdrop-blur">
      <h1 className="text-lg font-semibold text-marine">
        {entreeCourante ? t.navigation[entreeCourante.id] : ''}
      </h1>

      <div className="relative ml-4 hidden max-w-sm flex-1 md:block">
        <MagnifyingGlass
          size={18}
          weight="regular"
          aria-hidden
          className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-texte-attenue"
        />
        <input
          type="search"
          placeholder={t.coquille.recherche}
          aria-label={t.coquille.recherche}
          disabled
          title={t.coquille.recherche}
          className="w-full rounded-full border border-bordure bg-fond py-2 pl-10 pr-3 text-sm text-texte placeholder:text-texte-attenue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle disabled:cursor-not-allowed disabled:opacity-60"
        />
      </div>

      <div className="ml-auto flex items-center gap-2">
        <Reglages />

        <span className="hidden items-center gap-2 rounded-full border border-bordure px-3 py-1.5 xl:flex">
          <span className="text-xs text-texte-secondaire">{t.coquille.role}</span>
          <span className="text-sm font-medium text-texte">{t.roles[role]}</span>
        </span>

        {/* Le pilote porte un seul chantier (cahier des charges, hypothèse H2) :
            une étiquette fixe plutôt qu'un menu qui ne proposerait rien. */}
        <span className="hidden items-center gap-2 rounded-full border border-bordure px-3 py-2 text-sm font-medium text-texte lg:flex">
          <MapPin size={18} weight="regular" aria-hidden className="text-sarcelle" />
          <span>{t.coquille.chantierPilote}</span>
        </span>

        <button
          type="button"
          aria-label={t.coquille.notifications}
          title={t.coquille.notifications}
          disabled
          className="rounded-controle p-2 disabled:cursor-not-allowed disabled:opacity-50 text-texte-secondaire transition-colors duration-150 hover:bg-fond focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        >
          <Bell size={20} weight="regular" aria-hidden />
        </button>

        <button
          type="button"
          aria-label={t.coquille.aide}
          title={t.coquille.aide}
          disabled
          className="rounded-controle p-2 disabled:cursor-not-allowed disabled:opacity-50 text-texte-secondaire transition-colors duration-150 hover:bg-fond focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
        >
          <Question size={20} weight="regular" aria-hidden />
        </button>
      </div>
    </header>
  )
}
