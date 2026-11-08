/*
  Détail d'un logement en tiroir, avec maître-détail interne :
  - la liste ordonnée de ses étapes ;
  - le détail d'une étape sélectionnée : historique complet (EF-AVA-10),
    validation ou rejet (EF-AVA-06), déclaration de blocage (EF-AVA-05).

  Tout tient dans un seul tiroir : sélectionner une étape remplace la liste par
  son détail, avec un retour. Les formulaires de rejet et de blocage sont en
  ligne dans le détail — pas de fenêtre empilée sur le tiroir.

  Le contrôle auteur ≠ validateur (RG-D11) est appliqué ici : on ne peut pas
  valider une étape qu'on a soi-même déclarée terminée, même avec le rôle
  validateur.
*/

import { useMemo, useState, type FormEvent } from 'react'
import {
  Button,
  type ColonneTable,
  Drawer,
  FormField,
  Input,
  Select,
  StatusPill,
  Table,
  useToast,
} from '@/components/ui'
import { BarreAvancement } from '@/features/avancement/components/BarreAvancement'
import {
  declarerBlocage,
  listerEtapesLogement,
  listerEvenementsEtape,
  validerEtape,
} from '@/features/avancement/api'
import { useRequete, type EtatRequete } from '@/lib/hooks/useRequete'
import {
  ID_UTILISATEUR_COURANT,
  type CapacitesAvancement,
} from '@/features/avancement/config/capacites'
import { formatDate, formatDateHeure } from '@/lib/format'
import { LIBELLE_STATUT_ETAPE, TON_STATUT_ETAPE } from '@/features/avancement/presentation/libelles'
import type { EvenementExecution, LigneEtape, MotifBlocage } from '@/features/avancement/types'

export type CibleLogement = {
  idLogement: string
  numero: string
  idEtapeInitiale: string | null
}

export type FicheLogementTiroirProps = {
  cible: CibleLogement | null
  capacites: CapacitesAvancement
  motifs: MotifBlocage[]
  onFermer: () => void
  /** Rafraîchit le suivi et les files après une validation ou un blocage. */
  onChangement: () => void
}

export function FicheLogementTiroir({
  cible,
  capacites,
  motifs,
  onFermer,
  onChangement,
}: FicheLogementTiroirProps) {
  return (
    <Drawer
      ouvert={cible !== null}
      onFermer={onFermer}
      titre={cible ? `Logement ${cible.numero}` : ''}
      description="Avancement et étapes"
      largeur="lg"
      pied={
        <Button variante="secondaire" onClick={onFermer}>
          Fermer
        </Button>
      }
    >
      {cible && (
        <ContenuLogement
          key={cible.idLogement}
          cible={cible}
          capacites={capacites}
          motifs={motifs}
          onChangement={onChangement}
        />
      )}
    </Drawer>
  )
}

type ContenuLogementProps = {
  cible: CibleLogement
  capacites: CapacitesAvancement
  motifs: MotifBlocage[]
  onChangement: () => void
}

function ContenuLogement({ cible, capacites, motifs, onChangement }: ContenuLogementProps) {
  const etapesEtat = useRequete(() => listerEtapesLogement(cible.idLogement), [cible.idLogement])
  const [idEtapeSel, setIdEtapeSel] = useState<string | null>(cible.idEtapeInitiale)

  // Mémoïsé : `?? []` seul créerait un nouveau tableau à chaque rendu, ce qui
  // invaliderait le `useMemo` de calcul d'avancement ci-dessous (avertissement
  // react-hooks/exhaustive-deps relevé à l'étape 6, corrigé à l'étape 8).
  const etapes = useMemo(() => etapesEtat.donnees ?? [], [etapesEtat.donnees])
  const etapeSelectionnee = etapes.find((etape) => etape.idEtape === idEtapeSel) ?? null

  const { declare, valide } = useMemo(() => calculerAvancement(etapes), [etapes])

  function apresAction() {
    etapesEtat.recharger()
    onChangement()
    setIdEtapeSel(null)
  }

  if (etapesEtat.statut === 'erreur') {
    return <p className="text-sm text-danger">{etapesEtat.erreur}</p>
  }

  if (etapeSelectionnee) {
    return (
      <DetailEtape
        key={etapeSelectionnee.idEtape}
        etape={etapeSelectionnee}
        capacites={capacites}
        motifs={motifs}
        onRetour={() => setIdEtapeSel(null)}
        onAction={apresAction}
      />
    )
  }

  return (
    <div className="flex flex-col gap-5">
      <BarreAvancement pourcentageDeclare={declare} pourcentageValide={valide} />
      <ListeEtapes
        etapes={etapes}
        chargement={etapesEtat.statut === 'chargement'}
        onVoir={(etape) => setIdEtapeSel(etape.idEtape)}
      />
    </div>
  )
}

function calculerAvancement(etapes: LigneEtape[]): { declare: number; valide: number } {
  const total = etapes.reduce((somme, etape) => somme + etape.poidsEffectif, 0)
  if (total <= 0) {
    return { declare: 0, valide: 0 }
  }
  const declarePoids = etapes
    .filter((etape) => etape.statut === 'terminee_declaree' || etape.statut === 'validee')
    .reduce((somme, etape) => somme + etape.poidsEffectif, 0)
  const validePoids = etapes
    .filter((etape) => etape.statut === 'validee')
    .reduce((somme, etape) => somme + etape.poidsEffectif, 0)
  return { declare: (declarePoids / total) * 100, valide: (validePoids / total) * 100 }
}

function PastilleCorps({ couleur, libelle }: { couleur: string; libelle: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-sm">
      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: couleur }} aria-hidden />
      {libelle}
    </span>
  )
}

function ListeEtapes({
  etapes,
  chargement,
  onVoir,
}: {
  etapes: LigneEtape[]
  chargement: boolean
  onVoir: (etape: LigneEtape) => void
}) {
  const colonnes: ColonneTable<LigneEtape>[] = [
    {
      cle: 'ordre',
      entete: '#',
      largeur: '3rem',
      rendu: (etape) => <span className="text-texte-secondaire">{etape.ordre}</span>,
    },
    {
      cle: 'etape',
      entete: 'Étape',
      rendu: (etape) => (
        <div className="flex flex-col">
          <span className="font-medium text-texte">{etape.libelleEtape}</span>
          <PastilleCorps couleur={etape.couleurCorpsEtat} libelle={etape.libelleCorpsEtat} />
        </div>
      ),
    },
    {
      cle: 'statut',
      entete: 'Statut',
      largeur: '11rem',
      rendu: (etape) => (
        <div className="flex flex-col gap-1">
          <StatusPill
            taille="sm"
            ton={TON_STATUT_ETAPE[etape.statut]}
            libelle={LIBELLE_STATUT_ETAPE[etape.statut]}
          />
          {etape.enRetard && <StatusPill taille="sm" ton="alerte" libelle="En retard" />}
        </div>
      ),
    },
    {
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '6rem',
      rendu: (etape) => (
        <Button variante="discret" taille="sm" onClick={() => onVoir(etape)}>
          Détail
        </Button>
      ),
    },
  ]

  return (
    <Table
      intitule="Étapes du logement"
      colonnes={colonnes}
      lignes={etapes}
      cleLigne={(etape) => etape.idEtape}
      chargement={chargement}
      messageVide="Aucune étape pour ce logement."
    />
  )
}

type DetailEtapeProps = {
  etape: LigneEtape
  capacites: CapacitesAvancement
  motifs: MotifBlocage[]
  onRetour: () => void
  onAction: () => void
}

function DetailEtape({ etape, capacites, motifs, onRetour, onAction }: DetailEtapeProps) {
  const { afficherToast } = useToast()
  const evenementsEtat = useRequete(() => listerEvenementsEtape(etape.idEtape), [etape.idEtape])
  const [mode, setMode] = useState<'aucun' | 'rejet' | 'blocage'>('aucun')
  const [motifRejet, setMotifRejet] = useState('')
  const [codeBlocage, setCodeBlocage] = useState('')
  const [commentaireBlocage, setCommentaireBlocage] = useState('')
  const [erreur, setErreur] = useState<string | null>(null)
  const [enCours, setEnCours] = useState(false)

  const estAuteur = etape.idAuteurDeclaration === ID_UTILISATEUR_COURANT
  const peutEtreValidee = etape.statut === 'terminee_declaree' && etape.controleRequis
  const peutEtreBloquee = etape.statut === 'en_cours' || etape.statut === 'a_faire'
  const motifsActifs = motifs.filter((motif) => motif.actif)

  async function valider() {
    setEnCours(true)
    try {
      await validerEtape({ idEtape: etape.idEtape, decision: 'valider', motif: null })
      afficherToast({ ton: 'succes', titre: 'Étape validée' })
      onAction()
    } catch (erreurAppel) {
      afficherToast({
        ton: 'danger',
        titre: 'La validation a échoué',
        message: erreurAppel instanceof Error ? erreurAppel.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  async function confirmerRejet(evenement: FormEvent) {
    evenement.preventDefault()
    if (motifRejet.trim() === '') {
      setErreur('Le motif du rejet est obligatoire.')
      return
    }
    setErreur(null)
    setEnCours(true)
    try {
      await validerEtape({ idEtape: etape.idEtape, decision: 'rejeter', motif: motifRejet.trim() })
      afficherToast({ ton: 'succes', titre: 'Étape rejetée', message: 'Renvoyée en cours.' })
      onAction()
    } catch (erreurAppel) {
      afficherToast({
        ton: 'danger',
        titre: 'Le rejet a échoué',
        message: erreurAppel instanceof Error ? erreurAppel.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  async function confirmerBlocage(evenement: FormEvent) {
    evenement.preventDefault()
    if (codeBlocage === '') {
      setErreur('Choisir un motif de blocage.')
      return
    }
    setErreur(null)
    setEnCours(true)
    try {
      await declarerBlocage({
        idEtape: etape.idEtape,
        codeMotif: codeBlocage,
        commentaire: commentaireBlocage.trim() === '' ? null : commentaireBlocage.trim(),
      })
      afficherToast({ ton: 'succes', titre: 'Étape déclarée bloquée' })
      onAction()
    } catch (erreurAppel) {
      afficherToast({
        ton: 'danger',
        titre: 'La déclaration a échoué',
        message: erreurAppel instanceof Error ? erreurAppel.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <button
        type="button"
        onClick={onRetour}
        className="self-start text-sm font-medium text-sarcelle hover:underline"
      >
        ← Retour aux étapes
      </button>

      <div className="flex flex-col gap-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-marine">{etape.libelleEtape}</h3>
            <PastilleCorps couleur={etape.couleurCorpsEtat} libelle={etape.libelleCorpsEtat} />
          </div>
          <StatusPill
            ton={TON_STATUT_ETAPE[etape.statut]}
            libelle={LIBELLE_STATUT_ETAPE[etape.statut]}
          />
        </div>

        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
          <Donnee intitule="Date prévue" valeur={formatDate(etape.datePrevue)} />
          <Donnee intitule="Déclarée terminée le" valeur={formatDate(etape.dateFinDeclaree)} />
          <Donnee intitule="Validée le" valeur={formatDate(etape.dateValidation)} />
          <Donnee intitule="Déclarée par" valeur={etape.nomAuteurDeclaration ?? '—'} />
        </dl>

        {etape.enRetard && (
          <p className="rounded-controle bg-or-clair px-3 py-2 text-sm text-or">
            Date prévue dépassée : étape en retard.
          </p>
        )}
      </div>

      {/* Zone d'actions, selon le statut, les capacités et RG-D11. */}
      {peutEtreValidee && capacites.peutValider && (
        <div className="rounded-carte border border-bordure p-4">
          {estAuteur ? (
            <p className="text-sm text-texte-secondaire">
              Vous avez déclaré cette étape terminée : vous ne pouvez pas la valider vous-même
              (séparation des tâches). Un autre responsable doit la contrôler.
            </p>
          ) : mode === 'rejet' ? (
            <form onSubmit={confirmerRejet} className="flex flex-col gap-3" noValidate>
              <FormField libelle="Motif du rejet" requis erreur={erreur ?? undefined}>
                {(champ) => (
                  <Input
                    {...champ}
                    invalide={Boolean(erreur)}
                    value={motifRejet}
                    onChange={(e) => setMotifRejet(e.target.value)}
                  />
                )}
              </FormField>
              <div className="flex gap-2">
                <Button variante="danger" type="submit" enChargement={enCours}>
                  Confirmer le rejet
                </Button>
                <Button variante="secondaire" onClick={() => setMode('aucun')} disabled={enCours}>
                  Annuler
                </Button>
              </div>
            </form>
          ) : (
            <div className="flex flex-col gap-2">
              <p className="text-sm font-medium text-texte">Étape à contrôler</p>
              <div className="flex gap-2">
                <Button variante="primaire" onClick={valider} enChargement={enCours}>
                  Valider l'étape
                </Button>
                <Button variante="secondaire" onClick={() => setMode('rejet')} disabled={enCours}>
                  Rejeter
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {peutEtreBloquee && capacites.peutDeclarerBlocage && (
        <div className="rounded-carte border border-bordure p-4">
          {mode === 'blocage' ? (
            <form onSubmit={confirmerBlocage} className="flex flex-col gap-3" noValidate>
              <FormField libelle="Motif du blocage" requis erreur={erreur ?? undefined}>
                {(champ) => (
                  <Select
                    {...champ}
                    invalide={Boolean(erreur)}
                    value={codeBlocage}
                    onChange={(e) => setCodeBlocage(e.target.value)}
                  >
                    <option value="">— Choisir un motif —</option>
                    {motifsActifs.map((motif) => (
                      <option key={motif.codeMotif} value={motif.codeMotif}>
                        {motif.libelle}
                      </option>
                    ))}
                  </Select>
                )}
              </FormField>
              <FormField libelle="Commentaire" aide="Facultatif.">
                {(champ) => (
                  <Input
                    {...champ}
                    value={commentaireBlocage}
                    onChange={(e) => setCommentaireBlocage(e.target.value)}
                  />
                )}
              </FormField>
              <div className="flex gap-2">
                <Button variante="danger" type="submit" enChargement={enCours}>
                  Déclarer bloquée
                </Button>
                <Button variante="secondaire" onClick={() => setMode('aucun')} disabled={enCours}>
                  Annuler
                </Button>
              </div>
            </form>
          ) : (
            <Button variante="secondaire" onClick={() => setMode('blocage')}>
              Déclarer cette étape bloquée
            </Button>
          )}
        </div>
      )}

      <HistoriqueEtape etat={evenementsEtat} />
    </div>
  )
}

function Donnee({ intitule, valeur }: { intitule: string; valeur: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs font-medium uppercase tracking-wide text-texte-secondaire">
        {intitule}
      </dt>
      <dd className="mt-0.5 text-texte">{valeur}</dd>
    </div>
  )
}

function HistoriqueEtape({
  etat,
}: {
  etat: EtatRequete<EvenementExecution[]> & { recharger: () => void }
}) {
  if (etat.statut === 'erreur') {
    return <p className="text-sm text-danger">{etat.erreur}</p>
  }
  const evenements = etat.donnees ?? []

  return (
    <section className="flex flex-col gap-2">
      <h4 className="text-sm font-semibold text-texte">Historique de l'étape</h4>
      {etat.statut === 'chargement' && evenements.length === 0 ? (
        <div className="h-24 animate-pulse rounded-controle bg-fond-alt" />
      ) : evenements.length === 0 ? (
        <p className="text-sm text-texte-secondaire">Aucun événement.</p>
      ) : (
        <ol className="flex flex-col gap-3 border-l border-bordure pl-4">
          {evenements.map((evenement) => (
            <li key={evenement.uuid} className="relative">
              <span
                className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-sarcelle"
                aria-hidden
              />
              <p className="text-sm text-texte">
                {evenement.statutAvant
                  ? `${LIBELLE_STATUT_ETAPE[evenement.statutAvant]} → ${LIBELLE_STATUT_ETAPE[evenement.statutApres]}`
                  : LIBELLE_STATUT_ETAPE[evenement.statutApres]}
                {evenement.estDelegation && ' (délégation)'}
              </p>
              <p className="text-xs text-texte-secondaire">
                {formatDateHeure(evenement.horodatageServeur)} · {evenement.nomAuteur}
              </p>
              {evenement.commentaire && (
                <p className="mt-0.5 text-xs text-texte">« {evenement.commentaire} »</p>
              )}
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
