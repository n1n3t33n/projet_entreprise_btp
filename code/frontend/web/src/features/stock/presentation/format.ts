/*
  Formatage d'affichage (quantités, dates) en conventions françaises.
*/

const FORMAT_QUANTITE = new Intl.NumberFormat('fr-FR', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 3,
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

/** Quantité avec son unité, par exemple « 12,5 sac ». */
export function formatQuantite(valeur: number, unite?: string): string {
  const nombre = FORMAT_QUANTITE.format(valeur)
  return unite ? `${nombre} ${unite}` : nombre
}

/** Date au format jour/mois/année. */
export function formatDate(iso: string | null): string {
  if (!iso) {
    return '—'
  }
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '—' : FORMAT_DATE.format(date)
}

/** Date et heure, pour l'horodatage d'un mouvement. */
export function formatDateHeure(iso: string | null): string {
  if (!iso) {
    return '—'
  }
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '—' : FORMAT_DATE_HEURE.format(date)
}
