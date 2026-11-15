/*
  Création et modification d'un article du catalogue (EF-REF-03).

  Un seul formulaire sert les deux cas : sans article fourni il crée, avec un
  article il pré-remplit et modifie. Formulaire contrôlé, validation calculée à
  la soumission et affichée en ligne (jamais de fenêtre système, charte § 6).
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { creerArticle, modifierArticle } from '@/features/referentiels/api'
import { ORIGINES } from '@/features/referentiels/presentation/libelles'
import type {
  ArticleVue,
  Categorie,
  OrigineArticle,
  SaisieArticle,
  UniteMesure,
} from '@/features/referentiels/types'
import { tr } from '@/i18n/tr'

export type FormulaireArticleProps = {
  ouvert: boolean
  onFermer: () => void
  /** Article à modifier, ou `null` pour une création. */
  article: ArticleVue | null
  categories: Categorie[]
  unites: UniteMesure[]
  /** Appelé après un enregistrement réussi, pour rafraîchir la liste. */
  onEnregistre: () => void
}

type ErreursArticle = {
  code?: string
  designation?: string
  categorie?: string
  unite?: string
}

export function FormulaireArticle({
  ouvert,
  onFermer,
  article,
  categories,
  unites,
  onEnregistre,
}: FormulaireArticleProps) {
  const { afficherToast } = useToast()
  const modeModification = article !== null

  const [code, setCode] = useState('')
  const [designation, setDesignation] = useState('')
  const [origine, setOrigine] = useState<OrigineArticle>('achat')
  const [codeBarre, setCodeBarre] = useState('')
  const [codeCategorie, setCodeCategorie] = useState('')
  const [codeUnite, setCodeUnite] = useState('')
  const [actif, setActif] = useState(true)
  const [erreurs, setErreurs] = useState<ErreursArticle>({})
  const [enCours, setEnCours] = useState(false)

  // À l'ouverture, les champs reflètent l'article modifié, ou se vident pour une
  // création. Dépend de `ouvert` pour rejouer la synchronisation à chaque
  // ouverture, y compris sur un même article.
  useEffect(() => {
    if (!ouvert) {
      return
    }
    setCode(article?.code ?? '')
    setDesignation(article?.designation ?? '')
    setOrigine(article?.origine ?? 'achat')
    setCodeBarre(article?.codeBarre ?? '')
    setCodeCategorie(article?.codeCategorie ?? '')
    setCodeUnite(article?.codeUnite ?? '')
    setActif(article?.actif ?? true)
    setErreurs({})
  }, [ouvert, article])

  function fermer() {
    onFermer()
  }

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()

    const prochaines: ErreursArticle = {}
    if (code.trim() === '') {
      prochaines.code = tr('Saisir un code article.')
    }
    if (designation.trim() === '') {
      prochaines.designation = tr('Saisir une désignation.')
    }
    if (codeCategorie === '') {
      prochaines.categorie = tr('Choisir une catégorie.')
    }
    if (codeUnite === '') {
      prochaines.unite = tr('Choisir une unité.')
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) {
      return
    }

    const saisie: SaisieArticle = {
      code: code.trim(),
      designation: designation.trim(),
      origine,
      codeBarre: codeBarre.trim() === '' ? null : codeBarre.trim(),
      actif,
      codeCategorie,
      codeUnite,
    }

    setEnCours(true)
    try {
      if (modeModification && article) {
        await modifierArticle(article.id, saisie)
      } else {
        await creerArticle(saisie)
      }
      afficherToast({
        ton: 'succes',
        titre: modeModification ? tr('Article modifié') : tr('Article créé'),
        message: `${saisie.code} · ${saisie.designation}`,
      })
      fermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: tr("L'article n'a pas pu être enregistré"),
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
      titre={modeModification ? tr("Modifier l'article") : tr('Nouvel article')}
      description={tr('Référentiel du catalogue')}
      actions={
        <>
          <Button variante="secondaire" onClick={fermer} disabled={enCours}>
            {tr('Annuler')}
          </Button>
          <Button
            variante="primaire"
            type="submit"
            form="formulaire-article"
            enChargement={enCours}
          >
            {modeModification ? tr('Enregistrer') : tr("Créer l'article")}
          </Button>
        </>
      }
    >
      <form id="formulaire-article" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle={tr('Code article')} requis erreur={erreurs.code}>
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.code)}
                value={code}
                onChange={(evenement) => setCode(evenement.target.value)}
                placeholder="ex. CIM-42"
              />
            )}
          </FormField>

          <FormField libelle={tr('Origine')} requis>
            {(champ) => (
              <Select
                {...champ}
                value={origine}
                onChange={(evenement) => setOrigine(evenement.target.value as OrigineArticle)}
              >
                {ORIGINES.map((entree) => (
                  <option key={entree.valeur} value={entree.valeur}>
                    {entree.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        </div>

        <FormField libelle={tr('Désignation')} requis erreur={erreurs.designation}>
          {(champ) => (
            <Input
              {...champ}
              invalide={Boolean(erreurs.designation)}
              value={designation}
              onChange={(evenement) => setDesignation(evenement.target.value)}
              placeholder="ex. Ciment CPJ 42,5 — sac 50 kg"
            />
          )}
        </FormField>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle={tr('Catégorie')} requis erreur={erreurs.categorie}>
            {(champ) => (
              <Select
                {...champ}
                invalide={Boolean(erreurs.categorie)}
                value={codeCategorie}
                onChange={(evenement) => setCodeCategorie(evenement.target.value)}
              >
                <option value="">— Choisir —</option>
                {categories.map((categorie) => (
                  <option key={categorie.code} value={categorie.code}>
                    {categorie.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>

          <FormField libelle={tr('Unité de mesure')} requis erreur={erreurs.unite}>
            {(champ) => (
              <Select
                {...champ}
                invalide={Boolean(erreurs.unite)}
                value={codeUnite}
                onChange={(evenement) => setCodeUnite(evenement.target.value)}
              >
                <option value="">— Choisir —</option>
                {unites.map((unite) => (
                  <option key={unite.code} value={unite.code}>
                    {unite.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        </div>

        <FormField libelle="Code-barres" aide={tr("Facultatif. Unique s'il est renseigné.")}>
          {(champ) => (
            <Input
              {...champ}
              value={codeBarre}
              onChange={(evenement) => setCodeBarre(evenement.target.value)}
              placeholder="ex. 3012345000018"
            />
          )}
        </FormField>

        <label className="flex items-center gap-2 text-sm text-texte">
          <input
            type="checkbox"
            checked={actif}
            onChange={(evenement) => setActif(evenement.target.checked)}
            className="size-4 rounded border-bordure text-marine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
          />
          {tr('Article actif (présent dans les listes de saisie)')}
        </label>
      </form>
    </Modal>
  )
}
