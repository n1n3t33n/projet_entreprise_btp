/*
  Gammes opératoires — consultation et gestion des versions (EF-REF-05, EF-REF-09).

  Liste toutes les versions de gammes, groupables par type de logement, avec
  leur statut, leur version, leur nombre d'étapes et leur poids total. Un clic
  ouvre le détail, d'où partent les actions du cycle de vie.
*/

import { useMemo, useState } from 'react'
import { Eye, ListChecks, Stack } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, KpiCard, StatusPill, Table } from '@/components/ui'
import { PageListe } from '@/components/templates'
import { listerCorpsEtat, listerGammes } from '@/features/gammes/api'
import { DetailGamme } from '@/features/gammes/pages/DetailGamme'
import { LIBELLE_STATUT_GAMME, TON_STATUT_GAMME } from '@/features/gammes/presentation/libelles'
import { useRequete } from '@/lib/hooks/useRequete'
import { formatPourcentage } from '@/lib/format'
import type { Gamme } from '@/features/gammes/types'

export type GammesReferentielProps = {
  peutEditer: boolean
}

export function GammesReferentiel({ peutEditer }: GammesReferentielProps) {
  const gammesEtat = useRequete(listerGammes, [])
  const corpsEtatEtat = useRequete(listerCorpsEtat, [])

  const [detailOuvert, setDetailOuvert] = useState(false)
  const [idSelection, setIdSelection] = useState<string | null>(null)

  const gammes = useMemo(() => gammesEtat.donnees ?? [], [gammesEtat.donnees])
  const corpsEtat = useMemo(() => corpsEtatEtat.donnees ?? [], [corpsEtatEtat.donnees])

  const indicateurs = useMemo(() => {
    const actives = gammes.filter((gamme) => gamme.statut === 'active').length
    const brouillons = gammes.filter((gamme) => gamme.statut === 'brouillon').length
    return { total: gammes.length, actives, brouillons }
  }, [gammes])

  function ouvrirDetail(gamme: Gamme) {
    setIdSelection(gamme.id)
    setDetailOuvert(true)
  }

  const colonnes: ColonneTable<Gamme>[] = [
    {
      cle: 'type',
      entete: 'Type de logement',
      triable: true,
      valeurTri: (gamme) => `${gamme.libelleTypeLogement}-${100 - gamme.version}`,
      rendu: (gamme) => (
        <div className="min-w-0">
          <p className="truncate font-medium text-texte">{gamme.libelleTypeLogement}</p>
          <p className="truncate text-xs text-texte-secondaire">{gamme.libelle}</p>
        </div>
      ),
    },
    {
      cle: 'version',
      entete: 'Version',
      alignement: 'centre',
      largeur: '6rem',
      triable: true,
      valeurTri: (gamme) => gamme.version,
      rendu: (gamme) => <span className="text-texte-secondaire">v{gamme.version}</span>,
    },
    {
      cle: 'statut',
      entete: 'Statut',
      largeur: '8rem',
      triable: true,
      valeurTri: (gamme) => gamme.statut,
      rendu: (gamme) => (
        <StatusPill
          libelle={LIBELLE_STATUT_GAMME[gamme.statut]}
          ton={TON_STATUT_GAMME[gamme.statut]}
          taille="sm"
        />
      ),
    },
    {
      cle: 'etapes',
      entete: 'Étapes',
      alignement: 'droite',
      largeur: '6rem',
      triable: true,
      valeurTri: (gamme) => gamme.nombreEtapes,
      rendu: (gamme) => <span className="text-texte-secondaire">{gamme.nombreEtapes}</span>,
    },
    {
      cle: 'poids',
      entete: 'Poids total',
      alignement: 'droite',
      largeur: '8rem',
      triable: true,
      valeurTri: (gamme) => gamme.poidsTotal,
      rendu: (gamme) => (
        <span
          className={gamme.poidsTotal === 100 ? 'text-texte' : 'font-medium text-or'}
          title={gamme.poidsTotal === 100 ? undefined : 'Le poids total diffère de 100 %'}
        >
          {formatPourcentage(gamme.poidsTotal)}
        </span>
      ),
    },
    {
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '7rem',
      rendu: (gamme) => (
        <Button variante="discret" taille="sm" icone={Eye} onClick={() => ouvrirDetail(gamme)}>
          {peutEditer && gamme.statut !== 'archivee' ? 'Gérer' : 'Voir'}
        </Button>
      ),
    },
  ]

  if (gammesEtat.statut === 'erreur') {
    return (
      <Card>
        <p className="text-sm text-danger">{gammesEtat.erreur}</p>
      </Card>
    )
  }

  const chargement = gammesEtat.statut === 'chargement' || gammesEtat.statut === 'attente'

  return (
    <>
      <PageListe
        titre="Gammes opératoires"
        description="Versions de gammes par type de logement, du brouillon à l'archive"
        lectureSeule={!peutEditer}
        indicateurs={
          <>
            <KpiCard libelle="Gammes" valeur={indicateurs.total} icone={Stack} accent="marine" />
            <KpiCard
              libelle="Actives"
              valeur={indicateurs.actives}
              icone={ListChecks}
              accent="succes"
            />
            <KpiCard
              libelle="Brouillons"
              valeur={indicateurs.brouillons}
              icone={ListChecks}
              accent="or"
            />
          </>
        }
      >
        <Table
          intitule="Gammes opératoires"
          colonnes={colonnes}
          lignes={gammes}
          cleLigne={(gamme) => gamme.id}
          chargement={chargement}
          triInitial={{ cle: 'type', sens: 'asc' }}
          parPage={12}
          messageVide="Aucune gamme enregistrée."
        />
      </PageListe>

      <DetailGamme
        ouvert={detailOuvert}
        onFermer={() => setDetailOuvert(false)}
        idGamme={idSelection}
        peutEditer={peutEditer}
        corpsEtat={corpsEtat}
        onAction={() => gammesEtat.recharger()}
      />
    </>
  )
}
