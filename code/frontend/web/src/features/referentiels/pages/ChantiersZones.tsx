/*
  Chantiers & zones — consultation et édition (EF-REF-01).

  La structure d'un chantier (chantier → zones → logements) est présentée dans
  un arbre ; le nœud sélectionné ouvre un panneau de détail d'où partent les
  actions d'édition. Les créations et modifications passent par des modales qui
  rechargent l'arbre.
*/

import { useMemo, useState, type ReactNode } from 'react'
import {
  Buildings,
  HouseLine,
  MapPinLine,
  PencilSimple,
  Plus,
  Stack,
} from '@phosphor-icons/react'
import { Button, Card, type NoeudArbre, StatusPill, Tree } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import { chargerArborescence, listerChantiers, listerTypesLogement } from '@/features/referentiels/api'
import { FormulaireChantier } from '@/features/referentiels/pages/FormulaireChantier'
import { FormulaireLogement } from '@/features/referentiels/pages/FormulaireLogement'
import { FormulaireZone } from '@/features/referentiels/pages/FormulaireZone'
import { useRequete } from '@/features/referentiels/hooks/useRequete'
import { formatDate, formatSurface } from '@/features/referentiels/presentation/format'
import { libelleStatut, libelleTypeZone, tonStatut } from '@/features/referentiels/presentation/libelles'
import type {
  Chantier,
  ChantierArbre,
  Logement,
  LogementVue,
  Zone,
  ZoneArbre,
} from '@/features/referentiels/types'

export type ChantiersZonesProps = {
  peutEditer: boolean
}

/** Une ligne « intitulé / valeur » du panneau de détail. */
function Ligne({ intitule, valeur }: { intitule: string; valeur: ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-xs font-medium uppercase tracking-wide text-texte-secondaire">
        {intitule}
      </dt>
      <dd className="text-sm text-texte">{valeur}</dd>
    </div>
  )
}

export function ChantiersZones({ peutEditer }: ChantiersZonesProps) {
  const chantiersEtat = useRequete(listerChantiers, [])
  const typesEtat = useRequete(listerTypesLogement, [])

  const chantiers = useMemo(() => chantiersEtat.donnees ?? [], [chantiersEtat.donnees])
  // Le pilote ne compte qu'un chantier ; un sélecteur de chantier s'ajoutera
  // ici quand le périmètre couvrira plusieurs chantiers.
  const idChantier = chantiers[0]?.id ?? ''

  const arbreEtat = useRequete(
    () => (idChantier ? chargerArborescence(idChantier) : Promise.resolve<ChantierArbre | null>(null)),
    [idChantier],
  )
  const arbre = arbreEtat.donnees ?? null

  const [selectionId, setSelectionId] = useState<string | null>(null)
  const [formChantier, setFormChantier] = useState(false)
  const [formZone, setFormZone] = useState<{ ouvert: boolean; zone: Zone | null }>({
    ouvert: false,
    zone: null,
  })
  const [formLogement, setFormLogement] = useState<{
    ouvert: boolean
    logement: Logement | null
    idZone: string
  }>({ ouvert: false, logement: null, idZone: '' })

  const types = useMemo(() => typesEtat.donnees ?? [], [typesEtat.donnees])

  // Nœud sélectionné par défaut : la racine chantier, tant que rien n'est choisi.
  const selection = selectionId ?? (arbre ? `chantier:${arbre.chantier.id}` : null)

  const noeuds: NoeudArbre[] = useMemo(() => {
    if (!arbre) {
      return []
    }
    return [
      {
        id: `chantier:${arbre.chantier.id}`,
        libelle: arbre.chantier.nom,
        icone: Buildings,
        badge: `${arbre.zones.length} zone${arbre.zones.length > 1 ? 's' : ''}`,
        enfants: arbre.zones.map((entree) => ({
          id: `zone:${entree.zone.id}`,
          libelle: entree.zone.nom,
          icone: MapPinLine,
          badge: `${entree.logements.length}`,
          enfants: entree.logements.map((logement) => ({
            id: `logement:${logement.id}`,
            libelle: `${logement.numero} · ${logement.libelleType}`,
            icone: HouseLine,
          })),
        })),
      },
    ]
  }, [arbre])

  function rechargerStructure() {
    arbreEtat.recharger()
    chantiersEtat.recharger()
  }

  if (chantiersEtat.statut === 'erreur' || arbreEtat.statut === 'erreur') {
    return (
      <Card>
        <p className="text-sm text-danger">
          {chantiersEtat.erreur ?? arbreEtat.erreur ?? 'Chargement impossible.'}
        </p>
      </Card>
    )
  }

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Chantiers & zones"
        description="Structure des chantiers : zones et logements"
        niveauTitre={2}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)]">
        <Card titre="Structure" icone={Stack}>
          {arbre ? (
            <Tree
              intitule="Structure du chantier"
              noeuds={noeuds}
              selectionne={selection ?? undefined}
              onSelectionner={setSelectionId}
              ouvertsInitiaux={[`chantier:${arbre.chantier.id}`, ...arbre.zones.map((z) => `zone:${z.zone.id}`)]}
            />
          ) : (
            <p className="text-sm text-texte-secondaire">Chargement de la structure…</p>
          )}
        </Card>

        <PanneauDetail
          arbre={arbre}
          selection={selection}
          peutEditer={peutEditer}
          onModifierChantier={() => setFormChantier(true)}
          onAjouterZone={() => setFormZone({ ouvert: true, zone: null })}
          onModifierZone={(zone) => setFormZone({ ouvert: true, zone })}
          onAjouterLogement={(idZone) => setFormLogement({ ouvert: true, logement: null, idZone })}
          onModifierLogement={(logement) =>
            setFormLogement({ ouvert: true, logement, idZone: logement.idZone })
          }
        />
      </div>

      {peutEditer && arbre && (
        <>
          <FormulaireChantier
            ouvert={formChantier}
            onFermer={() => setFormChantier(false)}
            chantier={arbre.chantier}
            onEnregistre={rechargerStructure}
          />
          <FormulaireZone
            ouvert={formZone.ouvert}
            onFermer={() => setFormZone({ ouvert: false, zone: null })}
            zone={formZone.zone}
            idChantier={arbre.chantier.id}
            onEnregistre={rechargerStructure}
          />
          <FormulaireLogement
            ouvert={formLogement.ouvert}
            onFermer={() => setFormLogement({ ouvert: false, logement: null, idZone: '' })}
            logement={formLogement.logement}
            idZone={formLogement.idZone}
            typesLogement={types}
            onEnregistre={rechargerStructure}
          />
        </>
      )}
    </div>
  )
}

/* ----------------------------- Panneau de détail -------------------------- */

type PanneauDetailProps = {
  arbre: ChantierArbre | null
  selection: string | null
  peutEditer: boolean
  onModifierChantier: () => void
  onAjouterZone: () => void
  onModifierZone: (zone: Zone) => void
  onAjouterLogement: (idZone: string) => void
  onModifierLogement: (logement: LogementVue) => void
}

function PanneauDetail({
  arbre,
  selection,
  peutEditer,
  onModifierChantier,
  onAjouterZone,
  onModifierZone,
  onAjouterLogement,
  onModifierLogement,
}: PanneauDetailProps) {
  if (!arbre || !selection) {
    return (
      <Card titre="Détail">
        <p className="text-sm text-texte-secondaire">
          Sélectionnez un élément de la structure pour voir son détail.
        </p>
      </Card>
    )
  }

  const [type, id] = selection.split(':')

  if (type === 'zone') {
    const entree = arbre.zones.find((z) => z.zone.id === id)
    if (entree) {
      return (
        <DetailZone
          entree={entree}
          peutEditer={peutEditer}
          onModifier={() => onModifierZone(entree.zone)}
          onAjouterLogement={() => onAjouterLogement(entree.zone.id)}
          onModifierLogement={onModifierLogement}
        />
      )
    }
  }

  if (type === 'logement') {
    for (const entree of arbre.zones) {
      const logement = entree.logements.find((l) => l.id === id)
      if (logement) {
        return (
          <DetailLogement
            logement={logement}
            zone={entree.zone}
            peutEditer={peutEditer}
            onModifier={() => onModifierLogement(logement)}
          />
        )
      }
    }
  }

  return (
    <DetailChantier
      chantier={arbre.chantier}
      nombreZones={arbre.zones.length}
      peutEditer={peutEditer}
      onModifier={onModifierChantier}
      onAjouterZone={onAjouterZone}
    />
  )
}

function DetailChantier({
  chantier,
  nombreZones,
  peutEditer,
  onModifier,
  onAjouterZone,
}: {
  chantier: Chantier
  nombreZones: number
  peutEditer: boolean
  onModifier: () => void
  onAjouterZone: () => void
}) {
  return (
    <Card
      titre={chantier.nom}
      icone={Buildings}
      actions={
        peutEditer ? (
          <div className="flex gap-2">
            <Button variante="secondaire" taille="sm" icone={Plus} onClick={onAjouterZone}>
              Ajouter une zone
            </Button>
            <Button variante="discret" taille="sm" icone={PencilSimple} onClick={onModifier}>
              Modifier
            </Button>
          </div>
        ) : undefined
      }
    >
      <dl className="grid grid-cols-2 gap-4">
        <Ligne intitule="Code" valeur={chantier.code} />
        <Ligne
          intitule="Statut"
          valeur={<StatusPill ton={tonStatut(chantier.statut)} libelle={libelleStatut(chantier.statut)} />}
        />
        <Ligne intitule="Programme" valeur={chantier.programme || '—'} />
        <Ligne intitule="Date de début" valeur={formatDate(chantier.dateDebut)} />
        <Ligne intitule="Zones" valeur={nombreZones} />
      </dl>
    </Card>
  )
}

function DetailZone({
  entree,
  peutEditer,
  onModifier,
  onAjouterLogement,
  onModifierLogement,
}: {
  entree: ZoneArbre
  peutEditer: boolean
  onModifier: () => void
  onAjouterLogement: () => void
  onModifierLogement: (logement: LogementVue) => void
}) {
  return (
    <Card
      titre={entree.zone.nom}
      icone={MapPinLine}
      actions={
        peutEditer ? (
          <div className="flex gap-2">
            <Button variante="secondaire" taille="sm" icone={Plus} onClick={onAjouterLogement}>
              Ajouter un logement
            </Button>
            <Button variante="discret" taille="sm" icone={PencilSimple} onClick={onModifier}>
              Modifier
            </Button>
          </div>
        ) : undefined
      }
    >
      <dl className="mb-4 grid grid-cols-2 gap-4">
        <Ligne intitule="Code" valeur={entree.zone.code} />
        <Ligne intitule="Type" valeur={libelleTypeZone(entree.zone.typeZone)} />
        <Ligne intitule="Logements" valeur={entree.logements.length} />
      </dl>

      <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-texte-secondaire">
        Logements
      </h4>
      {entree.logements.length === 0 ? (
        <p className="text-sm text-texte-secondaire">Aucun logement dans cette zone.</p>
      ) : (
        <ul className="divide-y divide-bordure">
          {entree.logements.map((logement) => (
            <li key={logement.id} className="flex items-center justify-between gap-3 py-2">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-texte">{logement.numero}</p>
                <p className="truncate text-xs text-texte-secondaire">
                  {logement.libelleType} · {formatSurface(logement.surfaceReference)}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <StatusPill
                  taille="sm"
                  ton={tonStatut(logement.statut)}
                  libelle={libelleStatut(logement.statut)}
                />
                {peutEditer && (
                  <Button
                    variante="discret"
                    taille="sm"
                    icone={PencilSimple}
                    onClick={() => onModifierLogement(logement)}
                  >
                    Modifier
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}

function DetailLogement({
  logement,
  zone,
  peutEditer,
  onModifier,
}: {
  logement: LogementVue
  zone: Zone
  peutEditer: boolean
  onModifier: () => void
}) {
  return (
    <Card
      titre={`Logement ${logement.numero}`}
      icone={HouseLine}
      actions={
        peutEditer ? (
          <Button variante="discret" taille="sm" icone={PencilSimple} onClick={onModifier}>
            Modifier
          </Button>
        ) : undefined
      }
    >
      <dl className="grid grid-cols-2 gap-4">
        <Ligne intitule="Zone" valeur={zone.nom} />
        <Ligne intitule="Type" valeur={logement.libelleType} />
        <Ligne intitule="Surface de référence" valeur={formatSurface(logement.surfaceReference)} />
        <Ligne
          intitule="Statut"
          valeur={<StatusPill ton={tonStatut(logement.statut)} libelle={libelleStatut(logement.statut)} />}
        />
        <Ligne intitule="Livraison prévue" valeur={formatDate(logement.dateLivraisonPrevue)} />
      </dl>
    </Card>
  )
}
