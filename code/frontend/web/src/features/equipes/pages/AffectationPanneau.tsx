/*
  Panneau d'affectation (EF-REF-06). Affecte des étapes à un membre d'équipe au
  moyen d'une fiche de route (MPD-5 `fiche_route` + `ligne_fiche_route`) : c'est
  le seul rattachement du travail à une personne permis par le modèle. Affecter
  « à une équipe » revient donc à affecter à l'un de ses membres.

  Déroulé : choisir une équipe, puis un membre ; on voit alors ses fiches de
  route existantes et, pour le responsable technique, un formulaire pour en
  créer une nouvelle (cycle, dates, étapes cochées). La création appelle
  `POST /fiches-route`, qui inscrit les étapes choisies comme lignes de la fiche.
*/

import { useMemo, useState } from 'react'
import { ClipboardText } from '@phosphor-icons/react'
import {
  Button,
  Card,
  type ColonneTable,
  FormField,
  Select,
  StatusPill,
  Table,
  useToast,
} from '@/components/ui'
import {
  creerAffectation,
  listerEquipes,
  listerEtapesAffectables,
  listerFichesMembre,
  listerMembres,
} from '@/features/equipes/api'
import {
  LIBELLE_CYCLE,
  LIBELLE_STATUT_FICHE,
  TON_STATUT_FICHE,
} from '@/features/equipes/presentation/libelles'
import { formatDate } from '@/lib/format'
import { useRequete } from '@/lib/hooks/useRequete'
import type { TypeCycleFiche } from '@/features/avancement/types/enums'
import type {
  EtapeAffectable,
  FicheRouteAffectation,
  MembreEquipe,
} from '@/features/equipes/types/domaine'

export type AffectationPanneauProps = {
  peutAffecter: boolean
}

export function AffectationPanneau({ peutAffecter }: AffectationPanneauProps) {
  const { afficherToast } = useToast()

  const equipesEtat = useRequete(listerEquipes, [])
  const etapesEtat = useRequete(listerEtapesAffectables, [])
  const equipes = useMemo(() => equipesEtat.donnees ?? [], [equipesEtat.donnees])
  const etapes = useMemo(() => etapesEtat.donnees ?? [], [etapesEtat.donnees])

  const [idEquipe, setIdEquipe] = useState('')
  const equipeActive = idEquipe || equipes[0]?.id || ''

  const membresEtat = useRequete(
    () => (equipeActive ? listerMembres(equipeActive) : Promise.resolve<MembreEquipe[]>([])),
    [equipeActive],
  )
  const membres = useMemo(() => membresEtat.donnees ?? [], [membresEtat.donnees])

  const [idMembre, setIdMembre] = useState('')
  const membreActif = idMembre || membres[0]?.idUtilisateur || ''

  const fichesEtat = useRequete(
    () =>
      membreActif ? listerFichesMembre(membreActif) : Promise.resolve<FicheRouteAffectation[]>([]),
    [membreActif],
  )
  const fiches = useMemo(() => fichesEtat.donnees ?? [], [fichesEtat.donnees])

  // Formulaire de nouvelle fiche.
  const [cycle, setCycle] = useState<TypeCycleFiche>('semaine')
  const [dateDebut, setDateDebut] = useState(() => new Date().toISOString().slice(0, 10))
  const [idsEtapes, setIdsEtapes] = useState<string[]>([])
  const [enCours, setEnCours] = useState(false)

  const nomEtapeParId = useMemo(() => {
    const index = new Map<string, EtapeAffectable>()
    for (const etape of etapes) {
      index.set(etape.idEtape, etape)
    }
    return index
  }, [etapes])

  async function affecter() {
    if (!membreActif || idsEtapes.length === 0) {
      return
    }
    setEnCours(true)
    try {
      await creerAffectation({
        idUtilisateur: membreActif,
        typeCycle: cycle,
        dateDebut,
        dateFin: null,
        idsEtapes,
      })
      afficherToast({
        ton: 'succes',
        titre: 'Affectation créée',
        message: `${idsEtapes.length} étape(s) inscrite(s) sur une nouvelle fiche de route.`,
      })
      setIdsEtapes([])
      fichesEtat.recharger()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "L'affectation a échoué",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  const colonnesEtapes: ColonneTable<EtapeAffectable>[] = [
    {
      cle: 'etape',
      entete: 'Étape',
      rendu: (etape) => <span className="text-sm font-medium text-marine">{etape.libelleEtape}</span>,
      triable: true,
      valeurTri: (etape) => etape.libelleEtape,
    },
    {
      cle: 'logement',
      entete: 'Logement',
      largeur: '8rem',
      rendu: (etape) => (
        <span className="text-sm text-texte">
          {etape.numeroLogement}
          <span className="ml-1 text-xs text-texte-secondaire">({etape.libelleZone})</span>
        </span>
      ),
      triable: true,
      valeurTri: (etape) => etape.numeroLogement,
    },
    {
      cle: 'corps',
      entete: "Corps d'état",
      largeur: '10rem',
      rendu: (etape) => <span className="text-sm text-texte-secondaire">{etape.libelleCorpsEtat}</span>,
      triable: true,
      valeurTri: (etape) => etape.libelleCorpsEtat,
    },
  ]

  const colonnesFiches: ColonneTable<FicheRouteAffectation>[] = [
    {
      cle: 'fiche',
      entete: 'Fiche',
      largeur: '8rem',
      rendu: (fiche) => <span className="font-medium text-marine">{fiche.idFiche}</span>,
    },
    {
      cle: 'cycle',
      entete: 'Cycle',
      largeur: '9rem',
      rendu: (fiche) => LIBELLE_CYCLE[fiche.typeCycle],
    },
    {
      cle: 'debut',
      entete: 'Début',
      largeur: '8rem',
      rendu: (fiche) => formatDate(fiche.dateDebut),
    },
    {
      cle: 'etapes',
      entete: 'Étapes',
      rendu: (fiche) => (
        <span className="text-sm text-texte">
          {fiche.idsEtapes.length === 0
            ? '—'
            : fiche.idsEtapes
                .map((id) => nomEtapeParId.get(id)?.libelleEtape ?? id)
                .join(', ')}
        </span>
      ),
    },
    {
      cle: 'statut',
      entete: 'Statut',
      alignement: 'centre',
      largeur: '7rem',
      rendu: (fiche) => (
        <StatusPill ton={TON_STATUT_FICHE[fiche.statut]} taille="sm" libelle={LIBELLE_STATUT_FICHE[fiche.statut]} />
      ),
    },
  ]

  return (
    <div className="flex flex-col gap-6">
      <Card titre="Choisir un membre" description="Affecter le travail se fait membre par membre (une fiche de route appartient à un technicien)">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Équipe">
            {(champ) => (
              <Select
                {...champ}
                value={equipeActive}
                onChange={(evenement) => {
                  setIdEquipe(evenement.target.value)
                  setIdMembre('')
                }}
              >
                {equipes.map((equipe) => (
                  <option key={equipe.id} value={equipe.id}>
                    {equipe.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>

          <FormField libelle="Membre">
            {(champ) => (
              <Select
                {...champ}
                value={membreActif}
                onChange={(evenement) => setIdMembre(evenement.target.value)}
              >
                {membres.map((membre) => (
                  <option key={membre.idUtilisateur} value={membre.idUtilisateur}>
                    {membre.nom} — {membre.fonction}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        </div>
      </Card>

      <Card
        titre="Fiches de route du membre"
        description="Affectations déjà confiées à ce membre (MPD-5 fiche de route)"
      >
        <Table
          intitule="Fiches de route du membre"
          colonnes={colonnesFiches}
          lignes={fiches}
          cleLigne={(fiche) => fiche.idFiche}
          chargement={fichesEtat.statut === 'chargement' || fichesEtat.statut === 'attente'}
          messageVide="Aucune fiche de route pour ce membre."
          lectureSeule
        />
      </Card>

      {peutAffecter ? (
        <Card
          titre="Nouvelle affectation"
          description="Composer une fiche de route : cycle, date de début et étapes à confier"
        >
          <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FormField libelle="Cycle">
              {(champ) => (
                <Select
                  {...champ}
                  value={cycle}
                  onChange={(evenement) => setCycle(evenement.target.value as TypeCycleFiche)}
                >
                  {(Object.keys(LIBELLE_CYCLE) as TypeCycleFiche[]).map((valeur) => (
                    <option key={valeur} value={valeur}>
                      {LIBELLE_CYCLE[valeur]}
                    </option>
                  ))}
                </Select>
              )}
            </FormField>

            <FormField libelle="Date de début">
              {(champ) => (
                <input
                  {...champ}
                  type="date"
                  value={dateDebut}
                  onChange={(evenement) => setDateDebut(evenement.target.value)}
                  className="w-full rounded-controle border border-bordure bg-surface px-3 py-2 text-sm text-texte focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
                />
              )}
            </FormField>
          </div>

          <Table
            intitule="Étapes à affecter"
            colonnes={colonnesEtapes}
            lignes={etapes}
            cleLigne={(etape) => etape.idEtape}
            chargement={etapesEtat.statut === 'chargement' || etapesEtat.statut === 'attente'}
            selectionnable
            onSelectionChanger={setIdsEtapes}
            parPage={10}
            messageVide="Aucune étape affectable."
          />

          <div className="mt-4 flex items-center justify-end gap-3">
            <span className="text-sm text-texte-secondaire">
              {idsEtapes.length} étape(s) sélectionnée(s)
            </span>
            <Button
              variante="primaire"
              icone={ClipboardText}
              onClick={affecter}
              disabled={idsEtapes.length === 0 || !membreActif}
              enChargement={enCours}
            >
              Affecter sur une fiche de route
            </Button>
          </div>
        </Card>
      ) : (
        <Card titre="Affectation">
          <p className="text-sm text-texte-secondaire">
            Seul le responsable technique affecte les étapes aux membres. Vous consultez les
            affectations existantes en lecture seule.
          </p>
        </Card>
      )}
    </div>
  )
}
