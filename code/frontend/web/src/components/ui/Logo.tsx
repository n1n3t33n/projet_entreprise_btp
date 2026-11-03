type LogoProps = {
  variant?: 'sur-marine' | 'sur-clair'
  avecSousTitre?: boolean
}

export function Logo({ variant = 'sur-clair', avecSousTitre = true }: LogoProps) {
  const surMarine = variant === 'sur-marine'
  const couleurMarque = surMarine ? 'text-white' : 'text-marine'
  const couleurSousTitre = surMarine ? 'text-white/70' : 'text-texte-secondaire'

  return (
    <div className="flex items-center gap-3">
      <span className={couleurMarque} aria-hidden>
        <svg viewBox="0 0 40 40" width="36" height="36" fill="none" role="presentation">
          <rect x="7" y="4" width="26" height="32" rx="4" stroke="currentColor" strokeWidth="2.5" />
          <line x1="7" y1="13" x2="33" y2="13" stroke="currentColor" strokeWidth="2.5" />
          <rect x="12" y="18" width="5" height="5" rx="1" fill="currentColor" />
          <rect x="23" y="18" width="5" height="5" rx="1" fill="currentColor" />
          <rect x="17" y="27" width="6" height="9" rx="1" fill="currentColor" />
        </svg>
      </span>
      <span className="leading-tight">
        <span className={`block text-sm font-bold tracking-wide ${couleurMarque}`}>
          SCHIAVONE GROUP
        </span>
        {avecSousTitre && (
          <span className={`block text-xs ${couleurSousTitre}`}>
            ChantierSync · Poste de pilotage
          </span>
        )}
      </span>
    </div>
  )
}
