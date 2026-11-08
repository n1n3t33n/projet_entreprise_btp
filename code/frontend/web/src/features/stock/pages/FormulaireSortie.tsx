/*
  Saisie d'une sortie de stock vers un logement (EF-STK-01).

  Formulaire contrôlé. Il refuse une quantité supérieure au stock disponible —
  contrôle de confort côté interface, en attendant la contrainte serveur
  (inscrite au backlog backend). Un stock peut rester négatif par dérive de
  données (anomalie signalée), mais l'interface n'en crée jamais.

  La destination (logement) est obligatoire pour une sortie vers un logement ;
  le motif l'est pour les types qui l'exigent (perte, casse).
*/

import { useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { formatQuantite } from '@/features/stock/presentation/format'
import { enregistrerSortie } from '@/features/stock/api'
import type { LigneStock, TypeMouvement } from '@/features/stock/types'

/** Logements de démonstration du chantier pilote (le référentiel logement est hors périmètre). */
const LOGEMENTS_DEMO: ReadonlyArray<{ id: string; libelle: string }> = [
  { id: 'LOG-A1', libelle: 'Îlot A · Villa 1' },
  { id: 'LOG-A2', libelle: 'Îlot A · Villa 2' },
  { id: 'LOG-B1', libelle: 'Îlot B · Villa 1' },
  { id: 'LOG-B2', libelle: 'Îlot B · Villa 2' },
  { id: 'LOG-C1', libelle: 'Îlot C · Duplex 1' },
]

export type FormulaireSortieProps = {
  ouvert: boolean
  onFermer: () => void
  idMagasin: string
  articles: LigneStock[]
  /** Types de mouvement de sortie disponibles (sortie logement, perte, casse). */
  typesSortie: TypeMouvement[]
  onEnregistre: () => void
}

export function FormulaireSortie({
  ouvert,
  onFermer,
  idMagasin,
  articles,
  typesSortie,
  onEnregistre,
}: FormulaireSortieProps) {
  const { afficherToast } = useToast()

  const [idArticle, setIdArticle] = useState('')
  const [codeType, setCodeType] = useState('')
  const [quantite, setQuantite] = useState('')
  const [idLogement, setIdLogement] = useState('')
  const [corpsEtat, setCorpsEtat] = useState('')
  const [beneficiaire, setBeneficiaire] = useState('')
  const [motif, setMotif] = useState('')
  const [erreurs, setErreurs] = useState<Record<string, string>>({})
  const [enCours, setEnCours] = useState(false)

  const articleChoisi = articles.find((article) => article.idArticle === idArticle) ?? null
  const typeChoisi = typesSortie.find((type) => type.code === codeType) ?? null
  const quantiteNombre = Number.parseFloat(quantite.replace(',', '.'))
  const stockDisponible = articleChoisi?.quantite ?? 0

  function reinitialiser() {
    setIdArticle('')
    setCodeType('')
    setQuantite('')
    setIdLogement('')
    setCorpsEtat('')
    setBeneficiaire('')
    setMotif('')
    setErreurs({})
  }

  function fermer() {
    reinitialiser()
    onFermer()
  }

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()

    const prochainesErreurs: Record<string, string> = {}
    if (!articleChoisi) {
      prochainesErreurs.article = 'Choisir un article.'
    }
    if (!typeChoisi) {
      prochainesErreurs.type = 'Choisir la nature de la sortie.'
    }
    if (!Number.isFinite(quantiteNombre) || quantiteNombre <= 0) {
      prochainesErreurs.quantite = 'Saisir une quantité supérieure à zéro.'
    } else if (articleChoisi && quantiteNombre > stockDisponible) {
      // Contrôle demandé : pas de sortie au-delà du stock disponible.
      prochainesErreurs.quantite = `Quantité supérieure au stock disponible (${formatQuantite(
        stockDisponible,
        articleChoisi.uniteLibelle,
      )}).`
    }
    if (typeChoisi?.destinationObligatoire && !idLogement) {
      prochainesErreurs.logement = 'La destination est obligatoire pour une sortie vers un logement.'
    }
    if (typeChoisi?.motifObligatoire && motif.trim() === '') {
      prochainesErreurs.motif = 'Le motif est obligatoire pour ce type de sortie.'
    }

    setErreurs(prochainesErreurs)
    if (Object.keys(prochainesErreurs).length > 0 || !articleChoisi || !typeChoisi) {
      return
    }

    setEnCours(true)
    try {
      await enregistrerSortie({
        idMagasin,
        idArticle: articleChoisi.idArticle,
        codeTypeMouvement: typeChoisi.code,
        quantite: quantiteNombre,
        codeUnite: articleChoisi.uniteCode,
        idLogement,
        corpsEtat: corpsEtat.trim() === '' ? null : corpsEtat.trim(),
        beneficiaire: beneficiaire.trim() === '' ? null : beneficiaire.trim(),
        motif: motif.trim() === '' ? null : motif.trim(),
      })
      afficherToast({
        ton: 'succes',
        titre: 'Sortie enregistrée',
        message: `${articleChoisi.designation} — mouvement horodaté et tracé.`,
      })
      fermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "La sortie n'a pas pu être enregistrée",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  return (
    <Modal
      ouvert={ouvert}
      onFermer={fermer}
      titre="Nouvelle sortie"
      description="Sortie d'articles vers un logement"
      actions={
        <>
          <Button variante="secondaire" onClick={fermer} disabled={enCours}>
            Annuler
          </Button>
          <Button variante="primaire" type="submit" form="formulaire-sortie" enChargement={enCours}>
            Enregistrer la sortie
          </Button>
        </>
      }
    >
      <form id="formulaire-sortie" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
        <FormField libelle="Article" requis erreur={erreurs.article}>
          {(champ) => (
            <Select
              {...champ}
              invalide={Boolean(erreurs.article)}
              value={idArticle}
              onChange={(evenement) => setIdArticle(evenement.target.value)}
            >
              <option value="">— Choisir un article —</option>
              {articles.map((article) => (
                <option key={article.idArticle} value={article.idArticle}>
                  {article.code} · {article.designation}
                </option>
              ))}
            </Select>
          )}
        </FormField>

        <FormField libelle="Nature de la sortie" requis erreur={erreurs.type}>
          {(champ) => (
            <Select
              {...champ}
              invalide={Boolean(erreurs.type)}
              value={codeType}
              onChange={(evenement) => setCodeType(evenement.target.value)}
            >
              <option value="">— Choisir —</option>
              {typesSortie.map((type) => (
                <option key={type.code} value={type.code}>
                  {type.libelle}
                </option>
              ))}
            </Select>
          )}
        </FormField>

        <FormField
          libelle="Quantité sortie"
          requis
          erreur={erreurs.quantite}
          aide={
            articleChoisi
              ? `Disponible : ${formatQuantite(stockDisponible, articleChoisi.uniteLibelle)}`
              : undefined
          }
        >
          {(champ) => (
            <Input
              {...champ}
              type="number"
              min={0}
              step="0.001"
              inputMode="decimal"
              invalide={Boolean(erreurs.quantite)}
              value={quantite}
              onChange={(evenement) => setQuantite(evenement.target.value)}
            />
          )}
        </FormField>

        {typeChoisi?.destinationObligatoire !== false && (
          <FormField libelle="Logement de destination" requis erreur={erreurs.logement}>
            {(champ) => (
              <Select
                {...champ}
                invalide={Boolean(erreurs.logement)}
                value={idLogement}
                onChange={(evenement) => setIdLogement(evenement.target.value)}
              >
                <option value="">— Choisir un logement —</option>
                {LOGEMENTS_DEMO.map((logement) => (
                  <option key={logement.id} value={logement.id}>
                    {logement.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        )}

        <FormField libelle="Corps d'état" aide="Facultatif.">
          {(champ) => (
            <Input
              {...champ}
              value={corpsEtat}
              onChange={(evenement) => setCorpsEtat(evenement.target.value)}
              placeholder="ex. Maçonnerie"
            />
          )}
        </FormField>

        <FormField libelle="Bénéficiaire" aide="Facultatif.">
          {(champ) => (
            <Input
              {...champ}
              value={beneficiaire}
              onChange={(evenement) => setBeneficiaire(evenement.target.value)}
              placeholder="ex. Équipe gros œuvre"
            />
          )}
        </FormField>

        <FormField
          libelle="Motif"
          requis={typeChoisi?.motifObligatoire === true}
          erreur={erreurs.motif}
          aide={typeChoisi?.motifObligatoire === true ? undefined : 'Facultatif.'}
        >
          {(champ) => (
            <Input
              {...champ}
              invalide={Boolean(erreurs.motif)}
              value={motif}
              onChange={(evenement) => setMotif(evenement.target.value)}
            />
          )}
        </FormField>
      </form>
    </Modal>
  )
}
