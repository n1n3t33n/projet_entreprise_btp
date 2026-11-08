/*
  Indicateur discret affiché pendant l'arrivée d'un module chargé à la demande
  (voir `routes/index.tsx`).
*/

export function ChargementModule() {
  return (
    <p role="status" className="px-1 py-6 text-sm text-texte-secondaire">
      Chargement…
    </p>
  )
}
