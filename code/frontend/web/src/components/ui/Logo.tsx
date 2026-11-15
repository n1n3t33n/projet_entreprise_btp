import embleme from '@/assets/logo/schiavone-embleme.svg'
import logoComplet from '@/assets/logo/schiavone-logo.svg'
import { useT } from '@/app/preferences-context'

type LogoProps = {
  variant?: 'sur-marine' | 'sur-clair'
  avecSousTitre?: boolean
}

/*
  Logo officiel du groupe Schiavone (fichiers de cadrage/logo, seulement
  recadres). Sur fond marine : la facade seule dans une tuile blanche, le nom
  en blanc. Sur fond clair : le logo complet, pose sur une plaque blanche pour
  rester lisible aussi en theme sombre (le nom du groupe est marine).
*/
export function Logo({ variant = 'sur-clair', avecSousTitre = true }: LogoProps) {
  const t = useT()

  if (variant === 'sur-clair') {
    return (
      <div className="flex flex-col items-center gap-3">
        <span className="rounded-carte bg-white px-5 py-3 shadow-douce">
          <img
            src={logoComplet}
            alt="Schiavone Group"
            width={176}
            height={86}
            className="h-[86px] w-auto"
          />
        </span>
        {avecSousTitre && (
          <span className="text-sm font-medium text-texte-secondaire">{t.marque.sousTitre}</span>
        )}
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3">
      <span className="flex size-11 shrink-0 items-center justify-center rounded-controle bg-white">
        <img src={embleme} alt="" width={32} height={15} className="w-8" />
      </span>
      <span className="leading-tight">
        <span className="block text-sm font-bold tracking-wide text-white">SCHIAVONE GROUP</span>
        {avecSousTitre && <span className="block text-xs text-white/70">{t.marque.sousTitre}</span>}
      </span>
    </div>
  )
}
