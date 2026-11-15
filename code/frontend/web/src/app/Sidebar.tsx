import { SignOut, UserCircle } from '@phosphor-icons/react'
import { NavLink } from 'react-router-dom'
import { useT } from '@/app/preferences-context'
import { useRole } from '@/app/role-context'
import { useSession } from '@/app/session-context'
import { Logo } from '@/components/ui/Logo'
import { useDroits } from '@/app/droits-context'

export function Sidebar() {
  const { role } = useRole()
  const { ecransAutorises } = useDroits()
  const { session, fermerSession } = useSession()
  const entrees = ecransAutorises(role)
  const utilisateur = session?.utilisateur
  const t = useT()

  return (
    <aside className="fond-facade flex h-dvh w-64 shrink-0 flex-col text-white">
      <div className="p-5">
        <Logo variant="sur-marine" />
      </div>

      <nav aria-label={t.navigation.principale} className="flex-1 overflow-y-auto px-3 py-2">
        <ul className="space-y-1">
          {entrees.map((entree) => {
            const Icone = entree.icone
            return (
              <li key={entree.id}>
                <NavLink
                  to={entree.chemin}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-full px-4 py-2.5 text-sm transition-colors duration-[var(--duree-bouton)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 ${
                      isActive
                        ? 'bg-white font-semibold text-encre shadow-douce'
                        : 'font-medium text-white/85 hover:bg-white/10'
                    }`
                  }
                >
                  <Icone size={20} weight="regular" aria-hidden />
                  <span>{t.navigation[entree.id]}</span>
                </NavLink>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="border-t border-white/10 p-4">
        <div className="flex items-center gap-3">
          <UserCircle size={32} weight="regular" aria-hidden className="text-white/85" />
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold">
              {utilisateur ? `${utilisateur.prenom} ${utilisateur.nom}` : t.coquille.utilisateur}
            </p>
            <p className="truncate text-xs text-white/70">{t.roles[role]}</p>
            {utilisateur && (
              <p className="truncate text-xs text-white/50">{utilisateur.libellePerimetre}</p>
            )}
          </div>
        </div>
        <button
          type="button"
          onClick={fermerSession}
          className="mt-3 flex w-full items-center gap-2 rounded-full px-3 py-2 text-sm font-medium text-white/85 transition-colors duration-150 hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
        >
          <SignOut size={18} weight="regular" aria-hidden />
          {t.coquille.deconnexion}
        </button>
      </div>
    </aside>
  )
}
