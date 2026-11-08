/*
  Saisie d'une entrée de stock — réception (EF-STK-02).

  Formulaire contrôlé : chaque champ est tenu par un état React, la validation
  est calculée à la soumission et affichée en ligne (jamais de fenêtre système,
  charte § 6). La réception augmente le stock ; aucun contrôle de quantité
  maximale ne s'applique à une entrée.
*/

import { useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { enregistrerEntree } from '@/features/stock/api'
import type { LigneStock, TypeMouvement } from '@/features/stock/types'

export type FormulaireEntreeProps = {
  ouvert: boolean
  onFermer: () => void
  idMagasin: string
  articles: LigneStock[]
  /** Types de mouvement d'entrée disponibles (réception, retour). */
  typesEntree: TypeMouvement[]
  /** Appelé après un enregistrement réussi, pour rafraîchir le stock. */
  onEnregistre: () => void
}

export function FormulaireEntree({
  ouvert,
  onFermer,
  idMagasin,
  articles,
  typesEntree,
  onEnregistre,
}: FormulaireEntreeProps) {
  const { afficherToast } = useToast()

  const [idArticle, setIdArticle] = useState('')
  const [codeType, setCodeType] = useState('')
  const [quantite, setQuantite] = useState('')
  const [reference, setReference] = useState('')
  const [erreurs, setErreurs] = useState<{ article?: string; type?: string; quantite?: string }>({})
  const [enCours, setEnCours] = useState(false)

  const articleChoisi = articles.find((article) => article.idArticle === idArticle) ?? null
  const quantiteNombre = Number.parseFloat(quantite.replace(',', '.'))

  function reinitialiser() {
    setIdArticle('')
    setCodeType('')
    setQuantite('')
    setReference('')
    setErreurs({})
  }

  function fermer() {
    reinitialiser()
    onFermer()
  }

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()

    const prochainesErreurs: typeof erreurs = {}
    if (!articleChoisi) {
      prochainesErreurs.article = 'Choisir un article.'
    }
    if (!codeType) {
      prochainesErreurs.type = "Choisir la nature de l'entrée."
    }
    if (!Number.isFinite(quantiteNombre) || quantiteNombre <= 0) {
      prochainesErreurs.quantite = 'Saisir une quantité supérieure à zéro.'
    }
    setErreurs(prochainesErreurs)
    if (Object.keys(prochainesErreurs).length > 0 || !articleChoisi) {
      return
    }

    setEnCours(true)
    try {
      await enregistrerEntree({
        idMagasin,
        idArticle: articleChoisi.idArticle,
        codeTypeMouvement: codeType,
        quantite: quantiteNombre,
        codeUnite: articleChoisi.uniteCode,
        referenceExterne: reference.trim() === '' ? null : reference.trim(),
      })
      afficherToast({
        ton: 'succes',
        titre: 'Entrée enregistrée',
        message: `${articleChoisi.designation} — mouvement horodaté et tracé.`,
      })
      fermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "L'entrée n'a pas pu être enregistrée",
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
      titre="Nouvelle entrée"
      description="Réception d'articles au magasin"
      actions={
        <>
          <Button variante="secondaire" onClick={fermer} disabled={enCours}>
            Annuler
          </Button>
          <Button variante="primaire" type="submit" form="formulaire-entree" enChargement={enCours}>
            Enregistrer l'entrée
          </Button>
        </>
      }
    >
      <form id="formulaire-entree" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
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

        <FormField libelle="Nature de l'entrée" requis erreur={erreurs.type}>
          {(champ) => (
            <Select
              {...champ}
              invalide={Boolean(erreurs.type)}
              value={codeType}
              onChange={(evenement) => setCodeType(evenement.target.value)}
            >
              <option value="">— Choisir —</option>
              {typesEntree.map((type) => (
                <option key={type.code} value={type.code}>
                  {type.libelle}
                </option>
              ))}
            </Select>
          )}
        </FormField>

        <FormField
          libelle="Quantité reçue"
          requis
          erreur={erreurs.quantite}
          aide={articleChoisi ? `Unité : ${articleChoisi.uniteLibelle}` : undefined}
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

        <FormField
          libelle="Référence de bon de livraison ou de conteneur"
          aide="Texte libre, facultatif."
        >
          {(champ) => (
            <Input
              {...champ}
              value={reference}
              onChange={(evenement) => setReference(evenement.target.value)}
              placeholder="ex. BL-2026-0481"
            />
          )}
        </FormField>
      </form>
    </Modal>
  )
}
