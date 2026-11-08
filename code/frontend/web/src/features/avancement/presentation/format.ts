/*
  Formatage d'affichage (pourcentages, dates) en conventions françaises.

  Note : `formatDate` / `formatDateHeure` recoupent ceux du module stock ;
  candidats à un dossier partagé lors d'un nettoyage ultérieur.
*/

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

/** Pourcentage arrondi à l'entier, par exemple « 72 % ». */
export function formatPourcentage(valeur: number): string {
  return `${Math.round(valeur)} %`
}

/** Date au format jour/mois/année. */
export function formatDate(iso: string | null): string {
  if (!iso) {
    return '—'
  }
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '—' : FORMAT_DATE.format(date)
}

/** Date et heure, pour l'horodatage d'un événement. */
export function formatDateHeure(iso: string | null): string {
  if (!iso) {
    return '—'
  }
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '—' : FORMAT_DATE_HEURE.format(date)
}
