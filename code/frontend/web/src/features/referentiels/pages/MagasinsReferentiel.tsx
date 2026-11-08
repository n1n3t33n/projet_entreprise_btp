/*
  Magasins — consultation et édition (EF-REF-02).

  Liste les magasins avec leur chantier de rattachement et leur statut, et
  ouvre le formulaire de création ou de modification. Charge aussi les chantiers
  pour alimenter le choix de rattachement du formulaire.
*/

import { useMemo, useState } from 'react'
import { Buildings, PencilSimple, Plus, Warehouse } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, KpiCard, StatusPill, Table } from '@/components/ui'
import { PageListe } from '@/components/templates'
import { listerChantiers, listerMagasins } from '@/features/referentiels/api'
import { FormulaireMagasin } from '@/features/referentiels/pages/FormulaireMagasin'
import { useRequete } from '@/lib/hooks/useRequete'
import { tonActif } from '@/features/referentiels/presentation/libelles'
import type { MagasinVue } from '@/features/referentiels/types'

export type MagasinsReferentielProps = {
  peutEditer: boolean
}

export function MagasinsReferentiel({ peutEditer }: MagasinsReferentielProps) {
  const magasinsEtat = useRequete(listerMagasins, [])
  const chantiersEtat = useRequete(listerChantiers, [])

  const [modaleOuverte, setModaleOuverte] = useState(false)
  const [magasinEdite, setMagasinEdite] = useState<MagasinVue | null>(null)

  const magasins = useMemo(() => magasinsEtat.donnees ?? [], [magasinsEtat.donnees])
  const chantiers = useMemo(() => chantiersEtat.donnees ?? [], [chantiersEtat.donnees])

  const indicateurs = useMemo(() => {
    const actifs = magasins.filter((magasin) => magasin.actif).length
    return { total: magasins.length, actifs }
  }, [magasins])

  function ouvrirCreation() {
    setMagasinEdite(null)
    setModaleOuverte(true)
  }

  function ouvrirModification(magasin: MagasinVue) {
    setMagasinEdite(magasin)
    setModaleOuverte(true)
  }

  const colonnes: ColonneTable<MagasinVue>[] = [
    {
      cle: 'code',
      entete: 'Code',
      largeur: '9rem',
      rendu: (magasin) => <span className="font-medium text-marine">{magasin.code}</span>,
      triable: true,
      valeurTri: (magasin) => magasin.code,
    },
    {
      cle: 'nom',
      entete: 'Nom',
      rendu: (magasin) => magasin.nom,
      triable: true,
      valeurTri: (magasin) => magasin.nom,
    },
    {
      cle: 'chantier',
      entete: 'Chantier',
      rendu: (magasin) => magasin.libelleChantier,
      triable: true,
      valeurTri: (magasin) => magasin.libelleChantier,
    },
    {
      cle: 'actif',
      entete: 'Statut',
      alignement: 'centre',
      largeur: '7rem',
      rendu: (magasin) => (
        <StatusPill ton={tonActif(magasin.actif)} libelle={magasin.actif ? 'Actif' : 'Inactif'} />
      ),
      triable: true,
      valeurTri: (magasin) => (magasin.actif ? 1 : 0),
    },
  ]

  if (peutEditer) {
    colonnes.push({
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '7rem',
      rendu: (magasin) => (
        <Button
          variante="discret"
          taille="sm"
          icone={PencilSimple}
          onClick={() => ouvrirModification(magasin)}
        >
          Modifier
        </Button>
      ),
    })
  }

  if (magasinsEtat.statut === 'erreur') {
    return (
      <Card>
        <p className="text-sm text-danger">{magasinsEtat.erreur}</p>
      </Card>
    )
  }

  const chargement = magasinsEtat.statut === 'chargement' || magasinsEtat.statut === 'attente'

  return (
    <>
      <PageListe
        titre="Magasins"
        description="Lieux de stockage rattachés aux chantiers"
        lectureSeule={!peutEditer}
        actions={
          peutEditer ? (
            <Button variante="primaire" icone={Plus} onClick={ouvrirCreation}>
              Nouveau magasin
            </Button>
          ) : undefined
        }
        indicateurs={
          <>
            <KpiCard
              libelle="Magasins"
              valeur={indicateurs.total}
              icone={Warehouse}
              accent="marine"
            />
            <KpiCard
              libelle="Actifs"
              valeur={indicateurs.actifs}
              icone={Buildings}
              accent="succes"
            />
          </>
        }
      >
        <Table
          intitule="Magasins"
          colonnes={colonnes}
          lignes={magasins}
          cleLigne={(magasin) => magasin.id}
          chargement={chargement}
          triInitial={{ cle: 'code', sens: 'asc' }}
          parPage={12}
          messageVide="Aucun magasin enregistré."
        />
      </PageListe>

      {peutEditer && (
        <FormulaireMagasin
          ouvert={modaleOuverte}
          onFermer={() => setModaleOuverte(false)}
          magasin={magasinEdite}
          chantiers={chantiers}
          onEnregistre={() => magasinsEtat.recharger()}
        />
      )}
    </>
  )
}
