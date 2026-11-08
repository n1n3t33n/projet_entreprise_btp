/*
  Formatage d'affichage partagé, en conventions françaises.

  Exemplaire unique consommé par tous les modules. Il regroupe les fonctions
  qui existaient en double ou en triple dans les dossiers `presentation/` des
  modules stock, avancement et référentiels jusqu'à l'étape 7. Les libellés
  métier (statuts, origines…) restent, eux, dans chaque module : seul le
  formatage générique (nombres, dates, unités) est mutualisé ici.
*/

const FORMAT_QUANTITE = new Intl.NumberFormat('fr-FR', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 3,
})

const FORMAT_SURFACE = new Intl.NumberFormat('fr-FR', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
})

const FORMAT_DATE = new Intl.DateTimeFormat('fr-FR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
})

const FORMAT_DATE_HEURE = new Intl.DateTimeFormat('fr-FR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

/** Quantité avec son unité, par exemple « 12,5 sac » (trois décimales au plus, comme `numeric(14,3)`). */
export function formatQuantite(valeur: number, unite?: string): string {
  const nombre = FORMAT_QUANTITE.format(valeur)
  return unite ? `${nombre} ${unite}` : nombre
}

/** Surface en m², par exemple « 72,5 m² ». */
export function formatSurface(valeur: number): string {
  return `${FORMAT_SURFACE.format(valeur)} m²`
}

/** Pourcentage arrondi à l'entier, par exemple « 72 % ». */
export function formatPourcentage(valeur: number): string {
  return `${Math.round(valeur)} %`
}

/** Date au format jour/mois/année ; tiret cadratin si absente ou invalide. */
export function formatDate(iso: string | null): string {
  if (!iso) {
    return '—'
  }
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '—' : FORMAT_DATE.format(date)
}

/** Date et heure, pour l'horodatage d'un mouvement ou d'un événement. */
export function formatDateHeure(iso: string | null): string {
  if (!iso) {
    return '—'
  }
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '—' : FORMAT_DATE_HEURE.format(date)
}
