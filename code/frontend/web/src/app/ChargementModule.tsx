import { tr } from '@/i18n/tr'
/*
  Indicateur discret affiché pendant ltr('arrivée d')un module chargé à la demande
  (voir `routes/index.tsx`).
*/

export function ChargementModule() {
  return (
    <p role="status" className="px-1 py-6 text-sm text-texte-secondaire">
      {tr('Chargement…')}
    </p>
  )
}
