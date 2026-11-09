import { SignOut, UserCircle } from '@phosphor-icons/react'
import { NavLink } from 'react-router-dom'
import { libelleRole, useRole } from '@/app/role-context'
import { useSession } from '@/app/session-context'
import { Logo } from '@/components/ui/Logo'
import { useDroits } from '@/app/droits-context'

export function Sidebar() {
  const { role } = useRole()
  const { ecransAutorises } = useDroits()
  const { session, fermerSession } = useSession()
  const entrees = ecransAutorises(role)
  const utilisateur = session?.utilisateur

  return (
    <aside className="flex h-dvh w-64 shrink-0 flex-col bg-marine text-white">
      <div className="p-5">
        <Logo variant="sur-marine" />
      </div>

      <nav aria-label="Navigation principale" className="flex-1 overflow-y-auto px-3 py-2">
        <ul className="space-y-1">
          {entrees.map((entree) => {
            const Icone = entree.icone
            return (
              <li key={entree.id}>
                <NavLink
                  to={entree.chemin}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-controle px-3 py-2.5 text-sm transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 ${
                      isActive
                        ? 'bg-white/15 font-semibold text-white'
                        : 'font-medium text-white/85 hover:bg-white/10'
                    }`
                  }
                >
                  <Icone size={20} weight="regular" aria-hidden />
                  <span>{entree.libelle}</span>
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
              {utilisateur ? `${utilisateur.prenom} ${utilisateur.nom}` : 'Utilisateur'}
            </p>
            <p className="truncate text-xs text-white/70">{libelleRole(role)}</p>
            {utilisateur && (
              <p className="truncate text-xs text-white/50">{utilisateur.libellePerimetre}</p>
            )}
          </div>
        </div>
        <button
          type="button"
          onClick={fermerSession}
          className="mt-3 flex w-full items-center gap-2 rounded-controle px-3 py-2 text-sm font-medium text-white/85 transition-colors duration-150 hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
        >
          <SignOut size={18} weight="regular" aria-hidden />
          Se déconnecter
        </button>
      </div>
    </aside>
  )
}
