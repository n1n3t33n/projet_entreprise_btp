/*
  Fiche article en tiroir : état du stock, seuils, historique des mouvements.

  Le contenu est un composant séparé monté avec l'article : il se démonte quand
  le tiroir se ferme, ce qui réinitialise ses onglets et laisse chaque fiche
  recharger son propre historique. L'onglet « Seuils » n'est modifiable que si
  le rôle en a la capacité ; sinon il reste en lecture seule.
*/

import { useState, type FormEvent } from 'react'
import {
  Button,
  type ColonneTable,
  Drawer,
  FormField,
  Input,
  StatusPill,
  Table,
  Tabs,
  ThresholdGauge,
  useToast,
} from '@/components/ui'
import { definirSeuils, listerMouvementsArticle } from '@/features/stock/api'
import { useRequete } from '@/lib/hooks/useRequete'
import { formatDateHeure, formatQuantite } from '@/lib/format'
import {
  LIBELLE_SENS,
  LIBELLE_STATUT_VALIDATION,
  TON_STATUT_VALIDATION,
} from '@/features/stock/presentation/libelles'
import type { CapacitesStock } from '@/features/stock/config/capacites'
import type { LigneStock, MouvementStock } from '@/features/stock/types'

export type FicheArticleTiroirProps = {
  ligne: LigneStock | null
  idMagasin: string
  capacites: CapacitesStock
  onFermer: () => void
  /** Rafraîchit le stock après une modification des seuils. */
  onMiseAJour: () => void
}

export function FicheArticleTiroir({
  ligne,
  idMagasin,
  capacites,
  onFermer,
  onMiseAJour,
}: FicheArticleTiroirProps) {
  return (
    <Drawer
      ouvert={ligne !== null}
      onFermer={onFermer}
      titre={ligne?.designation ?? ''}
      description={ligne ? `${ligne.code} · ${ligne.libelleFamille}` : undefined}
      largeur="lg"
      pied={
        <Button variante="secondaire" onClick={onFermer}>
          Fermer
        </Button>
      }
    >
      {ligne && (
        <FicheContenu
          key={ligne.idArticle}
          ligne={ligne}
          idMagasin={idMagasin}
          capacites={capacites}
          onMiseAJour={onMiseAJour}
        />
      )}
    </Drawer>
  )
}

type FicheContenuProps = {
  ligne: LigneStock
  idMagasin: string
  capacites: CapacitesStock
  onMiseAJour: () => void
}

function FicheContenu({ ligne, idMagasin, capacites, onMiseAJour }: FicheContenuProps) {
  const [onglet, setOnglet] = useState('etat')

  return (
    <div className="flex flex-col gap-5">
      <Tabs
        intitule="Détail de l'article"
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'etat', libelle: 'État du stock' },
          { id: 'seuils', libelle: 'Seuils' },
          { id: 'historique', libelle: 'Historique' },
        ]}
      >
        {onglet === 'etat' && <OngletEtat ligne={ligne} />}
        {onglet === 'seuils' && (
          <OngletSeuils
            ligne={ligne}
            idMagasin={idMagasin}
            modifiable={capacites.peutDefinirSeuils}
            onMiseAJour={onMiseAJour}
          />
        )}
        {onglet === 'historique' && <OngletHistorique ligne={ligne} idMagasin={idMagasin} />}
      </Tabs>
    </div>
  )
}

function OngletEtat({ ligne }: { ligne: LigneStock }) {
  return (
    <div className="flex flex-col gap-5">
      <ThresholdGauge
        valeur={ligne.quantite}
        seuilMini={ligne.seuilMini}
        seuilConfort={ligne.seuilConfort}
        niveau={ligne.niveau}
        unite={ligne.uniteLibelle}
      />

      {ligne.quantite < 0 && (
        <p className="rounded-controle bg-danger/10 px-3 py-2 text-sm text-danger">
          Stock négatif : anomalie à régulariser par un inventaire. La valeur est conservée
          telle quelle, elle ne bloque pas la consultation.
        </p>
      )}

      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
        <Donnee intitule="Quantité en stock" valeur={formatQuantite(ligne.quantite, ligne.uniteLibelle)} />
        <Donnee intitule="Unité de base" valeur={ligne.uniteLibelle} />
        <Donnee intitule="Famille" valeur={ligne.libelleFamille} />
        <Donnee intitule="Code article" valeur={ligne.code} />
        <Donnee intitule="Code-barres" valeur={ligne.codeBarre ?? '—'} />
        <Donnee intitule="Article actif" valeur={ligne.actif ? 'Oui' : 'Non'} />
      </dl>
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

type OngletSeuilsProps = {
  ligne: LigneStock
  idMagasin: string
  modifiable: boolean
  onMiseAJour: () => void
}

function OngletSeuils({ ligne, idMagasin, modifiable, onMiseAJour }: OngletSeuilsProps) {
  const { afficherToast } = useToast()
  const [minimal, setMinimal] = useState(String(ligne.seuilMinimal))
  const [critique, setCritique] = useState(String(ligne.seuilCritique))
  const [erreur, setErreur] = useState<string | null>(null)
  const [enCours, setEnCours] = useState(false)

  const minimalNombre = Number.parseFloat(minimal.replace(',', '.'))
  const critiqueNombre = Number.parseFloat(critique.replace(',', '.'))

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()
    if (!Number.isFinite(minimalNombre) || !Number.isFinite(critiqueNombre)) {
      setErreur('Saisir deux seuils numériques.')
      return
    }
    if (minimalNombre < 0 || critiqueNombre < 0) {
      setErreur('Les seuils ne peuvent pas être négatifs.')
      return
    }
    if (critiqueNombre > minimalNombre) {
      setErreur('Le seuil critique doit rester inférieur ou égal au seuil minimal.')
      return
    }
    setErreur(null)
    setEnCours(true)
    try {
      await definirSeuils(idMagasin, ligne.idArticle, {
        seuilMinimal: minimalNombre,
        seuilCritique: critiqueNombre,
      })
      afficherToast({ ton: 'succes', titre: 'Seuils enregistrés' })
      onMiseAJour()
    } catch (erreurAppel) {
      afficherToast({
        ton: 'danger',
        titre: "Les seuils n'ont pas pu être enregistrés",
        message: erreurAppel instanceof Error ? erreurAppel.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  if (!modifiable) {
    return (
      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
        <Donnee intitule="Seuil minimal" valeur={formatQuantite(ligne.seuilMinimal, ligne.uniteLibelle)} />
        <Donnee intitule="Seuil critique" valeur={formatQuantite(ligne.seuilCritique, ligne.uniteLibelle)} />
      </dl>
    )
  }

  return (
    <form onSubmit={soumettre} className="flex max-w-md flex-col gap-4" noValidate>
      <p className="text-sm text-texte-secondaire">
        Seuils définis pour cet article dans ce magasin. En dessous du seuil minimal, le stock
        passe « mini » ; en dessous du seuil critique, « critique ».
      </p>

      <FormField libelle="Seuil minimal" requis aide={`Unité : ${ligne.uniteLibelle}`}>
        {(champ) => (
          <Input
            {...champ}
            type="number"
            min={0}
            step="0.001"
            inputMode="decimal"
            value={minimal}
            onChange={(evenement) => setMinimal(evenement.target.value)}
          />
        )}
      </FormField>

      <FormField
        libelle="Seuil critique"
        requis
        erreur={erreur ?? undefined}
        aide={erreur ? undefined : `Unité : ${ligne.uniteLibelle}`}
      >
        {(champ) => (
          <Input
            {...champ}
            type="number"
            min={0}
            step="0.001"
            inputMode="decimal"
            invalide={Boolean(erreur)}
            value={critique}
            onChange={(evenement) => setCritique(evenement.target.value)}
          />
        )}
      </FormField>

      <div>
        <Button variante="primaire" type="submit" enChargement={enCours}>
          Enregistrer les seuils
        </Button>
      </div>
    </form>
  )
}

const COLONNES_HISTORIQUE: ColonneTable<MouvementStock>[] = [
  {
    cle: 'date',
    entete: 'Date',
    rendu: (mouvement) => formatDateHeure(mouvement.dateOperation),
    triable: true,
    valeurTri: (mouvement) => mouvement.dateOperation,
  },
  {
    cle: 'sens',
    entete: 'Sens',
    rendu: (mouvement) => LIBELLE_SENS[mouvement.sens],
  },
  {
    cle: 'quantite',
    entete: 'Quantité',
    alignement: 'droite',
    rendu: (mouvement) => formatQuantite(mouvement.quantiteSaisie),
    triable: true,
    valeurTri: (mouvement) => mouvement.quantiteSaisie,
  },
  {
    cle: 'statut',
    entete: 'Statut',
    rendu: (mouvement) => (
      <StatusPill
        taille="sm"
        ton={TON_STATUT_VALIDATION[mouvement.statutValidation]}
        libelle={LIBELLE_STATUT_VALIDATION[mouvement.statutValidation]}
      />
    ),
  },
  {
    cle: 'auteur',
    entete: 'Auteur',
    rendu: (mouvement) => mouvement.nomAuteur,
  },
]

function OngletHistorique({ ligne, idMagasin }: { ligne: LigneStock; idMagasin: string }) {
  const etat = useRequete(
    () => listerMouvementsArticle(idMagasin, ligne.idArticle),
    [idMagasin, ligne.idArticle],
  )

  if (etat.statut === 'erreur') {
    return <p className="text-sm text-danger">{etat.erreur}</p>
  }

  return (
    <Table
      intitule={`Historique des mouvements de ${ligne.designation}`}
      colonnes={COLONNES_HISTORIQUE}
      lignes={etat.donnees ?? []}
      cleLigne={(mouvement) => mouvement.uuid}
      chargement={etat.statut === 'chargement'}
      triInitial={{ cle: 'date', sens: 'desc' }}
      messageVide="Aucun mouvement enregistré pour cet article."
      parPage={8}
    />
  )
}
