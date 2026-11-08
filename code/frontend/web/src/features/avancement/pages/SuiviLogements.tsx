/*
  Suivi de l'avancement par logement (EF-DSH-05).

  Tableau des logements du chantier : avancement déclaré et validé, nombre
  d'étapes, blocages et retards. Filtrage en mémoire sur les lignes déjà
  chargées (zone, recherche de numéro). Vue de consultation ; l'action ouvre le
  détail du logement.
*/

import { useMemo } from 'react'
import { Button, Card, type ColonneTable, FilterPill, Input, StatusPill, Table } from '@/components/ui'
import { BarreAvancement } from '@/features/avancement/components/BarreAvancement'
import { formatPourcentage } from '@/lib/format'
import {
  LIBELLE_STATUT_LOGEMENT,
  TON_STATUT_LOGEMENT,
} from '@/features/avancement/presentation/libelles'
import type { FiltreAvancement, LigneLogement, Zone } from '@/features/avancement/types'

export type SuiviLogementsProps = {
  lignes: LigneLogement[]
  chargement: boolean
  zones: Zone[]
  filtre: FiltreAvancement
  onFiltre: (filtre: FiltreAvancement) => void
  onVoirLogement: (ligne: LigneLogement) => void
}

function sansAccents(valeur: string): string {
  return valeur.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

export function SuiviLogements({
  lignes,
  chargement,
  zones,
  filtre,
  onFiltre,
  onVoirLogement,
}: SuiviLogementsProps) {
  const lignesFiltrees = useMemo(() => {
    const recherche = sansAccents(filtre.recherche.trim())
    return lignes.filter((ligne) => {
      if (filtre.idZone !== 'toutes' && !ligne.libelleZone.includes(zoneLibelle(zones, filtre.idZone))) {
        return false
      }
      if (recherche.length > 0) {
        const cible = sansAccents(`${ligne.numero} ${ligne.libelleZone} ${ligne.libelleType}`)
        if (!cible.includes(recherche)) {
          return false
        }
      }
      return true
    })
  }, [lignes, filtre, zones])

  const colonnes: ColonneTable<LigneLogement>[] = [
    {
      cle: 'numero',
      entete: 'Logement',
      largeur: '8rem',
      rendu: (ligne) => <span className="font-medium text-marine">{ligne.numero}</span>,
      triable: true,
      valeurTri: (ligne) => ligne.numero,
    },
    {
      cle: 'zone',
      entete: 'Zone',
      rendu: (ligne) => ligne.libelleZone,
      triable: true,
      valeurTri: (ligne) => ligne.libelleZone,
    },
    {
      cle: 'type',
      entete: 'Type',
      rendu: (ligne) => ligne.libelleType,
    },
    {
      cle: 'avancement',
      entete: 'Avancement',
      largeur: '17rem',
      rendu: (ligne) => (
        <BarreAvancement
          taille="sm"
          pourcentageDeclare={ligne.pourcentageDeclare}
          pourcentageValide={ligne.pourcentageValide}
        />
      ),
      triable: true,
      valeurTri: (ligne) => ligne.pourcentageValide,
    },
    {
      cle: 'etapes',
      entete: 'Étapes',
      alignement: 'droite',
      largeur: '6rem',
      rendu: (ligne) => `${ligne.nombreValidees}/${ligne.nombreEtapes}`,
    },
    {
      cle: 'alertes',
      entete: 'Points d’attention',
      largeur: '12rem',
      rendu: (ligne) => (
        <div className="flex flex-wrap gap-1">
          {ligne.nombreBloquees > 0 && (
            <StatusPill taille="sm" ton="danger" libelle={`${ligne.nombreBloquees} bloquée${ligne.nombreBloquees > 1 ? 's' : ''}`} />
          )}
          {ligne.nombreEnRetard > 0 && (
            <StatusPill taille="sm" ton="alerte" libelle={`${ligne.nombreEnRetard} en retard`} />
          )}
          {ligne.nombreBloquees === 0 && ligne.nombreEnRetard === 0 && (
            <span className="text-sm text-texte-attenue">—</span>
          )}
        </div>
      ),
    },
    {
      cle: 'statut',
      entete: 'Statut',
      largeur: '7rem',
      rendu: (ligne) => (
        <StatusPill
          taille="sm"
          ton={TON_STATUT_LOGEMENT[ligne.statut]}
          libelle={LIBELLE_STATUT_LOGEMENT[ligne.statut]}
        />
      ),
    },
    {
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '6rem',
      rendu: (ligne) => (
        <Button variante="discret" taille="sm" onClick={() => onVoirLogement(ligne)}>
          Détail
        </Button>
      ),
    },
  ]

  return (
    <Card
      sansRemplissage
      pied={
        <span className="text-sm text-texte-secondaire">
          {lignesFiltrees.length} logement{lignesFiltrees.length > 1 ? 's' : ''} · avancement validé
          moyen {formatPourcentage(moyenneValide(lignesFiltrees))}
        </span>
      }
    >
      <div className="flex flex-wrap items-center gap-2 border-b border-bordure p-4">
        <Input
          type="search"
          aria-label="Rechercher un logement"
          placeholder="Rechercher un logement…"
          value={filtre.recherche}
          onChange={(evenement) => onFiltre({ ...filtre, recherche: evenement.target.value })}
          className="max-w-xs"
        />
        <span className="mx-1 h-6 w-px bg-bordure" aria-hidden />
        <FilterPill
          libelle="Toutes les zones"
          actif={filtre.idZone === 'toutes'}
          onBasculer={() => onFiltre({ ...filtre, idZone: 'toutes' })}
        />
        {zones.map((zone) => (
          <FilterPill
            key={zone.idZone}
            libelle={zone.nom}
            actif={filtre.idZone === zone.idZone}
            onBasculer={() => onFiltre({ ...filtre, idZone: zone.idZone })}
          />
        ))}
      </div>

      <Table
        intitule="Suivi de l'avancement par logement"
        colonnes={colonnes}
        lignes={lignesFiltrees}
        cleLigne={(ligne) => ligne.idLogement}
        chargement={chargement}
        triInitial={{ cle: 'avancement', sens: 'asc' }}
        parPage={12}
        messageVide="Aucun logement ne correspond aux filtres."
      />
    </Card>
  )
}

function zoneLibelle(zones: Zone[], idZone: string): string {
  return zones.find((zone) => zone.idZone === idZone)?.nom ?? ''
}

function moyenneValide(lignes: LigneLogement[]): number {
  if (lignes.length === 0) return 0
  return lignes.reduce((somme, ligne) => somme + ligne.pourcentageValide, 0) / lignes.length
}
