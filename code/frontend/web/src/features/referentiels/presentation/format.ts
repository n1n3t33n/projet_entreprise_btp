/*
  Formatage d'affichage (dates, surfaces) en conventions françaises.

  DUPLICATION ASSUMÉE : `formatDate` reprend celui des modules stock et
  avancement. La mutualisation vers `lib/` est renvoyée à la même branche de
  nettoyage que `useRequete`, pour garder le diff de cette étape ciblé.
*/

const FORMAT_SURFACE = new Intl.NumberFormat('fr-FR', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
})

const FORMAT_DATE = new Intl.DateTimeFormat('fr-FR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
})

/** Date au format jour/mois/année ; tiret cadratin si absente ou invalide. */
export function formatDate(iso: string | null): string {
  if (!iso) {
    return '—'
  }
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '—' : FORMAT_DATE.format(date)
}

/** Surface en m², par exemple « 72,5 m² ». */
export function formatSurface(valeur: number): string {
  return `${FORMAT_SURFACE.format(valeur)} m²`
}
