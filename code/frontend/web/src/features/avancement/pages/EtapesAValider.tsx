/*
  File des étapes à valider (EF-AVA-06) : toutes les étapes à contrôle déclarées
  terminées, en attente de décision, tous logements confondus. « Examiner »
  ouvre le détail de l'étape, où la validation ou le rejet a lieu.
*/

import { Button, Card, type ColonneTable, StatusPill, Table } from '@/components/ui'
import { formatDate } from '@/features/avancement/presentation/format'
import type { LigneEtape } from '@/features/avancement/types'

export type EtapesAValiderProps = {
  etapes: LigneEtape[]
  chargement: boolean
  onExaminer: (etape: LigneEtape) => void
}

export function EtapesAValider({ etapes, chargement, onExaminer }: EtapesAValiderProps) {
  const colonnes: ColonneTable<LigneEtape>[] = [
    {
      cle: 'logement',
      entete: 'Logement',
      largeur: '8rem',
      rendu: (etape) => <span className="font-medium text-marine">{etape.numeroLogement}</span>,
      triable: true,
      valeurTri: (etape) => etape.numeroLogement,
    },
    {
      cle: 'etape',
      entete: 'Étape',
      rendu: (etape) => (
        <span className="inline-flex items-center gap-1.5">
          <span
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: etape.couleurCorpsEtat }}
            aria-hidden
          />
          {etape.libelleEtape}
          <span className="text-texte-secondaire"> · {etape.libelleCorpsEtat}</span>
        </span>
      ),
    },
    {
      cle: 'declaree',
      entete: 'Déclarée le',
      largeur: '8rem',
      rendu: (etape) => formatDate(etape.dateFinDeclaree),
      triable: true,
      valeurTri: (etape) => etape.dateFinDeclaree ?? '',
    },
    {
      cle: 'auteur',
      entete: 'Déclarée par',
      rendu: (etape) => etape.nomAuteurDeclaration ?? '—',
    },
    {
      cle: 'retard',
      entete: '',
      largeur: '7rem',
      rendu: (etape) =>
        etape.enRetard ? <StatusPill taille="sm" ton="alerte" libelle="En retard" /> : null,
    },
    {
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '7rem',
      rendu: (etape) => (
        <Button variante="secondaire" taille="sm" onClick={() => onExaminer(etape)}>
          Examiner
        </Button>
      ),
    },
  ]

  return (
    <Card
      titre="Étapes à valider"
      description="Étapes à contrôle déclarées terminées, en attente de décision."
      sansRemplissage
    >
      <Table
        intitule="Étapes à valider"
        colonnes={colonnes}
        lignes={etapes}
        cleLigne={(etape) => etape.idEtape}
        chargement={chargement}
        triInitial={{ cle: 'declaree', sens: 'asc' }}
        parPage={10}
        messageVide="Aucune étape en attente de validation."
      />
    </Card>
  )
}
