/*
  Tableau d'avancement agrégé, commun aux trois groupements du tableau de bord
  (zone, corps d'état, logement).

  Un seul composant sert les trois vues parce que RG-A6 définit une seule
  règle de calcul pour les quatre portées : les lignes ont donc exactement la
  même forme, seul leur intitulé change. Écrire trois tableaux aurait fait
  trois occasions de les laisser diverger.
*/

import { JaugeProgression, Table, type ColonneTable } from '@/components/ui'
import { formatPourcentage } from '@/lib/format'
import { ecartDeclareValide, type AvancementAgrege } from '@/features/pilotage/types'

export type TableauAgregatsProps = {
  /** Objet du tableau, lu par les lecteurs d'écran. */
  intitule: string
  /** En-tête de la première colonne, par exemple « Zone ». */
  enteteCible: string
  lignes: AvancementAgrege[]
  chargement?: boolean
  messageVide?: string
}

export function TableauAgregats({
  intitule,
  enteteCible,
  lignes,
  chargement = false,
  messageVide = 'Aucun élément à afficher.',
}: TableauAgregatsProps) {
  const colonnes: ColonneTable<AvancementAgrege>[] = [
    {
      cle: 'cible',
      entete: enteteCible,
      triable: true,
      valeurTri: (ligne) => ligne.libelleCible,
      rendu: (ligne) => (
        <div className="flex min-w-0 items-center gap-2">
          {ligne.couleur && (
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: ligne.couleur }}
              aria-hidden
            />
          )}
          <div className="min-w-0">
            <p className="truncate font-medium text-texte">{ligne.libelleCible}</p>
            {ligne.libelleSecondaire && (
              <p className="truncate text-xs text-texte-secondaire">{ligne.libelleSecondaire}</p>
            )}
          </div>
        </div>
      ),
    },
    {
      cle: 'progression',
      entete: 'Progression',
      largeur: '16rem',
      triable: true,
      valeurTri: (ligne) => ligne.pourcentageValide,
      rendu: (ligne) => (
        <JaugeProgression
          valeur={ligne.pourcentageValide}
          valeurSecondaire={ligne.pourcentageDeclare}
          libelleValeur="Validé"
          libelleValeurSecondaire="Déclaré"
          taille="sm"
          afficherLegende={false}
          descriptionAccessible={`Validé ${Math.round(ligne.pourcentageValide)} %, déclaré ${Math.round(ligne.pourcentageDeclare)} %`}
        />
      ),
    },
    {
      cle: 'valide',
      entete: 'Validé',
      alignement: 'droite',
      triable: true,
      valeurTri: (ligne) => ligne.pourcentageValide,
      rendu: (ligne) => (
        <span className="font-medium text-texte">{formatPourcentage(ligne.pourcentageValide)}</span>
      ),
    },
    {
      cle: 'declare',
      entete: 'Déclaré',
      alignement: 'droite',
      triable: true,
      valeurTri: (ligne) => ligne.pourcentageDeclare,
      rendu: (ligne) => formatPourcentage(ligne.pourcentageDeclare),
    },
    {
      cle: 'ecart',
      entete: 'À contrôler',
      alignement: 'droite',
      triable: true,
      valeurTri: (ligne) => ecartDeclareValide(ligne),
      rendu: (ligne) => {
        const ecart = ecartDeclareValide(ligne)
        return (
          <span className={ecart > 0 ? 'font-medium text-or' : 'text-texte-secondaire'}>
            {formatPourcentage(ecart)}
          </span>
        )
      },
    },
    {
      cle: 'etapes',
      entete: 'Étapes',
      alignement: 'droite',
      triable: true,
      valeurTri: (ligne) => ligne.nombreEtapes,
      rendu: (ligne) => (
        <span className="text-texte-secondaire">
          {ligne.nombreValidees} / {ligne.nombreEtapes}
        </span>
      ),
    },
    {
      cle: 'incidents',
      entete: 'Retards · blocages',
      alignement: 'droite',
      triable: true,
      valeurTri: (ligne) => ligne.nombreBloquees * 100 + ligne.nombreEnRetard,
      rendu: (ligne) => {
        if (ligne.nombreBloquees === 0 && ligne.nombreEnRetard === 0) {
          return <span className="text-texte-secondaire">—</span>
        }
        return (
          <span className="font-medium text-danger">
            {ligne.nombreEnRetard} · {ligne.nombreBloquees}
          </span>
        )
      },
    },
  ]

  return (
    <Table
      intitule={intitule}
      colonnes={colonnes}
      lignes={lignes}
      cleLigne={(ligne) => `${ligne.portee}-${ligne.idCible}`}
      triInitial={{ cle: 'cible', sens: 'asc' }}
      chargement={chargement}
      messageVide={messageVide}
      lectureSeule
      parPage={12}
    />
  )
}
