/*
  Liste des articles d'un magasin, avec indicateurs, filtres et niveaux.

  Premier des cinq écrans : il compose le gabarit `PageListe` (en-tête,
  indicateurs, filtres, contenu) avec le tableau générique et la jauge de
  seuils. Le filtrage est calculé localement, en mémoire, à partir des lignes
  déjà chargées — le changement de filtre ne relance aucun appel réseau.
*/

import { useMemo } from 'react'
import { ArrowLineDown, ArrowLineUp, Package, Warning, WarningOctagon } from '@phosphor-icons/react'
import {
  Button,
  type ColonneTable,
  FilterPill,
  Input,
  KpiCard,
  Table,
  ThresholdGauge,
} from '@/components/ui'
import { PageListe } from '@/components/templates'
import type { NiveauSeuil } from '@/lib/seuils'
import { formatQuantite } from '@/lib/format'
import { LIBELLE_NIVEAU } from '@/features/stock/presentation/libelles'
import type { FiltreStock, LigneStock } from '@/features/stock/types'

const ORDRE_NIVEAU: Record<NiveauSeuil, number> = { vide: 0, critique: 1, mini: 2, plein: 3 }
const NIVEAUX: NiveauSeuil[] = ['vide', 'critique', 'mini', 'plein']

export type ListeArticlesStockProps = {
  lignes: LigneStock[]
  chargement: boolean
  magasinLibelle: string
  chantierLibelle: string
  filtre: FiltreStock
  onFiltre: (filtre: FiltreStock) => void
  lectureSeule: boolean
  peutSaisir: boolean
  onNouvelleEntree: () => void
  onNouvelleSortie: () => void
  onVoirFiche: (ligne: LigneStock) => void
}

function sansAccents(valeur: string): string {
  return valeur.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

export function ListeArticlesStock({
  lignes,
  chargement,
  magasinLibelle,
  chantierLibelle,
  filtre,
  onFiltre,
  lectureSeule,
  peutSaisir,
  onNouvelleEntree,
  onNouvelleSortie,
  onVoirFiche,
}: ListeArticlesStockProps) {
  const famillesDisponibles = useMemo(() => {
    const parCode = new Map<string, string>()
    for (const ligne of lignes) {
      parCode.set(ligne.codeFamille, ligne.libelleFamille)
    }
    return [...parCode.entries()]
      .map(([code, libelle]) => ({ code, libelle }))
      .sort((a, b) => a.libelle.localeCompare(b.libelle, 'fr'))
  }, [lignes])

  const lignesFiltrees = useMemo(() => {
    const recherche = sansAccents(filtre.recherche.trim())
    return lignes.filter((ligne) => {
      if (filtre.niveau !== 'tous' && ligne.niveau !== filtre.niveau) {
        return false
      }
      if (filtre.codeFamille !== 'toutes' && ligne.codeFamille !== filtre.codeFamille) {
        return false
      }
      if (recherche.length > 0) {
        const cible = sansAccents(`${ligne.code} ${ligne.designation}`)
        if (!cible.includes(recherche)) {
          return false
        }
      }
      return true
    })
  }, [lignes, filtre])

  const indicateurs = useMemo(() => {
    const aSurveiller = lignes.filter((ligne) => ligne.niveau !== 'plein').length
    const ruptures = lignes.filter((ligne) => ligne.niveau === 'vide').length
    const anomalies = lignes.filter((ligne) => ligne.quantite < 0).length
    return { total: lignes.length, aSurveiller, ruptures, anomalies }
  }, [lignes])

  const colonnes: ColonneTable<LigneStock>[] = [
    {
      cle: 'code',
      entete: 'Code',
      largeur: '7rem',
      rendu: (ligne) => <span className="font-medium text-marine">{ligne.code}</span>,
      triable: true,
      valeurTri: (ligne) => ligne.code,
    },
    {
      cle: 'designation',
      entete: 'Désignation',
      rendu: (ligne) => ligne.designation,
      triable: true,
      valeurTri: (ligne) => ligne.designation,
    },
    {
      cle: 'famille',
      entete: 'Famille',
      rendu: (ligne) => ligne.libelleFamille,
      triable: true,
      valeurTri: (ligne) => ligne.libelleFamille,
    },
    {
      cle: 'niveau',
      entete: 'Niveau',
      largeur: '15rem',
      rendu: (ligne) => (
        <ThresholdGauge
          taille="sm"
          valeur={ligne.quantite}
          seuilMini={ligne.seuilMini}
          seuilConfort={ligne.seuilConfort}
          niveau={ligne.niveau}
          unite={ligne.uniteLibelle}
          afficherValeurs={false}
        />
      ),
      triable: true,
      valeurTri: (ligne) => ORDRE_NIVEAU[ligne.niveau],
    },
    {
      cle: 'quantite',
      entete: 'Quantité',
      alignement: 'droite',
      largeur: '9rem',
      rendu: (ligne) => formatQuantite(ligne.quantite, ligne.uniteLibelle),
      triable: true,
      valeurTri: (ligne) => ligne.quantite,
    },
    {
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '6rem',
      rendu: (ligne) => (
        <Button variante="discret" taille="sm" onClick={() => onVoirFiche(ligne)}>
          Voir
        </Button>
      ),
    },
  ]

  return (
    <PageListe
      titre="Stock du magasin"
      description={`${magasinLibelle} · ${chantierLibelle}`}
      lectureSeule={lectureSeule}
      actions={
        peutSaisir ? (
          <>
            <Button variante="secondaire" icone={ArrowLineDown} onClick={onNouvelleEntree}>
              Nouvelle entrée
            </Button>
            <Button variante="primaire" icone={ArrowLineUp} onClick={onNouvelleSortie}>
              Nouvelle sortie
            </Button>
          </>
        ) : undefined
      }
      indicateurs={
        <>
          <KpiCard
            libelle="Références suivies"
            valeur={indicateurs.total}
            icone={Package}
            accent="marine"
          />
          <KpiCard
            libelle="À surveiller"
            valeur={indicateurs.aSurveiller}
            icone={Warning}
            accent="or"
          />
          <KpiCard
            libelle="En rupture"
            valeur={indicateurs.ruptures}
            icone={WarningOctagon}
            accent="danger"
          />
          <KpiCard
            libelle="Anomalies de stock"
            valeur={indicateurs.anomalies}
            icone={WarningOctagon}
            accent="danger"
          />
        </>
      }
      filtres={
        <>
          <Input
            type="search"
            aria-label="Rechercher un article"
            placeholder="Rechercher un code ou une désignation…"
            value={filtre.recherche}
            onChange={(evenement) => onFiltre({ ...filtre, recherche: evenement.target.value })}
            className="max-w-xs"
          />

          <select
            aria-label="Filtrer par famille"
            value={filtre.codeFamille}
            onChange={(evenement) =>
              onFiltre({
                ...filtre,
                codeFamille: evenement.target.value as FiltreStock['codeFamille'],
              })
            }
            className="h-10 rounded-controle border border-bordure bg-surface px-3 text-sm text-texte focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
          >
            <option value="toutes">Toutes les familles</option>
            {famillesDisponibles.map((famille) => (
              <option key={famille.code} value={famille.code}>
                {famille.libelle}
              </option>
            ))}
          </select>

          <span className="mx-1 h-6 w-px bg-bordure" aria-hidden />

          <FilterPill
            libelle="Tous les niveaux"
            actif={filtre.niveau === 'tous'}
            onBasculer={() => onFiltre({ ...filtre, niveau: 'tous' })}
          />
          {NIVEAUX.map((niveau) => (
            <FilterPill
              key={niveau}
              libelle={LIBELLE_NIVEAU[niveau]}
              actif={filtre.niveau === niveau}
              onBasculer={() => onFiltre({ ...filtre, niveau })}
            />
          ))}
        </>
      }
    >
      <Table
        intitule={`Articles en stock — ${magasinLibelle}`}
        colonnes={colonnes}
        lignes={lignesFiltrees}
        cleLigne={(ligne) => ligne.idArticle}
        chargement={chargement}
        triInitial={{ cle: 'niveau', sens: 'asc' }}
        parPage={12}
        hauteurMax="40rem"
        messageVide="Aucun article ne correspond aux filtres."
      />
    </PageListe>
  )
}
