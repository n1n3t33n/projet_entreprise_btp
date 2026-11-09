/*
  Corps d'état — consultation et édition (EF-REF-05).

  Liste les corps d'état dans leur ordre d'affichage, avec leur pastille de
  couleur, et ouvre le formulaire de création ou de modification.
*/

import { useMemo, useState } from 'react'
import { HardHat, PencilSimple, Plus } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, KpiCard, Table } from '@/components/ui'
import { PageListe } from '@/components/templates'
import { listerCorpsEtat } from '@/features/gammes/api'
import { FormulaireCorpsEtat } from '@/features/gammes/pages/FormulaireCorpsEtat'
import { useRequete } from '@/lib/hooks/useRequete'
import type { CorpsEtat } from '@/features/gammes/types'

export type CorpsEtatReferentielProps = {
  peutEditer: boolean
}

export function CorpsEtatReferentiel({ peutEditer }: CorpsEtatReferentielProps) {
  const corpsEtat = useRequete(listerCorpsEtat, [])
  const [ouvert, setOuvert] = useState(false)
  const [edite, setEdite] = useState<CorpsEtat | null>(null)

  const liste = useMemo(() => corpsEtat.donnees ?? [], [corpsEtat.donnees])
  const ordreSuivant = useMemo(
    () => liste.reduce((max, corps) => Math.max(max, corps.ordre), 0) + 1,
    [liste],
  )

  function ouvrirCreation() {
    setEdite(null)
    setOuvert(true)
  }

  function ouvrirModification(corps: CorpsEtat) {
    setEdite(corps)
    setOuvert(true)
  }

  const colonnes: ColonneTable<CorpsEtat>[] = [
    {
      cle: 'ordre',
      entete: 'Ordre',
      largeur: '6rem',
      alignement: 'centre',
      triable: true,
      valeurTri: (corps) => corps.ordre,
      rendu: (corps) => <span className="text-texte-secondaire">{corps.ordre}</span>,
    },
    {
      cle: 'corps',
      entete: "Corps d'état",
      triable: true,
      valeurTri: (corps) => corps.libelle,
      rendu: (corps) => (
        <div className="flex items-center gap-2">
          <span
            className="h-3 w-3 shrink-0 rounded-full"
            style={{ backgroundColor: corps.couleur }}
            aria-hidden
          />
          <span className="font-medium text-texte">{corps.libelle}</span>
        </div>
      ),
    },
    {
      cle: 'code',
      entete: 'Code',
      largeur: '8rem',
      rendu: (corps) => <span className="font-medium text-marine">{corps.code}</span>,
    },
  ]

  if (peutEditer) {
    colonnes.push({
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '7rem',
      rendu: (corps) => (
        <Button
          variante="discret"
          taille="sm"
          icone={PencilSimple}
          onClick={() => ouvrirModification(corps)}
        >
          Modifier
        </Button>
      ),
    })
  }

  if (corpsEtat.statut === 'erreur') {
    return (
      <Card>
        <p className="text-sm text-danger">{corpsEtat.erreur}</p>
      </Card>
    )
  }

  const chargement = corpsEtat.statut === 'chargement' || corpsEtat.statut === 'attente'

  return (
    <>
      <PageListe
        titre="Corps d'état"
        description="Métiers du chantier, ordonnés du gros œuvre aux finitions"
        lectureSeule={!peutEditer}
        actions={
          peutEditer ? (
            <Button variante="primaire" icone={Plus} onClick={ouvrirCreation}>
              Nouveau corps d'état
            </Button>
          ) : undefined
        }
        indicateurs={
          <KpiCard libelle="Corps d'état" valeur={liste.length} icone={HardHat} accent="marine" />
        }
      >
        <Table
          intitule="Corps d'état"
          colonnes={colonnes}
          lignes={liste}
          cleLigne={(corps) => corps.code}
          chargement={chargement}
          triInitial={{ cle: 'ordre', sens: 'asc' }}
          messageVide="Aucun corps d'état enregistré."
        />
      </PageListe>

      {peutEditer && (
        <FormulaireCorpsEtat
          ouvert={ouvert}
          onFermer={() => setOuvert(false)}
          corpsEtat={edite}
          ordreSuivant={ordreSuivant}
          onEnregistre={() => corpsEtat.recharger()}
        />
      )}
    </>
  )
}
