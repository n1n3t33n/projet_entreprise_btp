type PageEnPreparationProps = {
  titre: string
  description?: string
}

export function PageEnPreparation({ titre, description }: PageEnPreparationProps) {
  return (
    <div className="mx-auto max-w-2xl rounded-carte border border-bordure bg-surface p-10 text-center shadow-douce">
      <h2 className="text-xl font-bold text-marine">{titre}</h2>
      <p className="mt-2 text-texte-secondaire">{description ?? 'Écran en préparation.'}</p>
    </div>
  )
}
