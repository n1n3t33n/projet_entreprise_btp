/*
  Création et modification d'un corps d'état (EF-REF-05).

  Le code sert d'identifiant stable (clé primaire côté MPD) : il n'est pas
  modifiable une fois le corps d'état créé, car des étapes-modèles s'y réfèrent.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, useToast } from '@/components/ui'
import { creerCorpsEtat, modifierCorpsEtat } from '@/features/gammes/api'
import type { CorpsEtat, SaisieCorpsEtat } from '@/features/gammes/types'

export type FormulaireCorpsEtatProps = {
  ouvert: boolean
  onFermer: () => void
  /** Corps d'état à modifier, ou `null` pour une création. */
  corpsEtat: CorpsEtat | null
  /** Ordre proposé pour un nouveau corps d'état. */
  ordreSuivant: number
  onEnregistre: () => void
}

type Erreurs = { code?: string; libelle?: string }

export function FormulaireCorpsEtat({
  ouvert,
  onFermer,
  corpsEtat,
  ordreSuivant,
  onEnregistre,
}: FormulaireCorpsEtatProps) {
  const { afficherToast } = useToast()
  const modeModification = corpsEtat !== null

  const [code, setCode] = useState('')
  const [libelle, setLibelle] = useState('')
  const [ordre, setOrdre] = useState(1)
  const [couleur, setCouleur] = useState('#6c8ebf')
  const [erreurs, setErreurs] = useState<Erreurs>({})
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert) return
    setCode(corpsEtat?.code ?? '')
    setLibelle(corpsEtat?.libelle ?? '')
    setOrdre(corpsEtat?.ordre ?? ordreSuivant)
    setCouleur(corpsEtat?.couleur ?? '#6c8ebf')
    setErreurs({})
  }, [ouvert, corpsEtat, ordreSuivant])

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()
    const prochaines: Erreurs = {}
    if (!modeModification && code.trim() === '') prochaines.code = 'Saisir un code.'
    if (libelle.trim() === '') prochaines.libelle = 'Saisir un libellé.'
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) return

    const saisie: SaisieCorpsEtat = {
      code: code.trim().toUpperCase(),
      libelle: libelle.trim(),
      ordre,
      couleur,
    }

    setEnCours(true)
    try {
      if (modeModification && corpsEtat) {
        await modifierCorpsEtat(corpsEtat.code, saisie)
      } else {
        await creerCorpsEtat(saisie)
      }
      afficherToast({
        ton: 'succes',
        titre: modeModification ? "Corps d'état modifié" : "Corps d'état créé",
        message: `${saisie.code} · ${saisie.libelle}`,
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "Le corps d'état n'a pas pu être enregistré",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  return (
    <Modal
      ouvert={ouvert}
      onFermer={onFermer}
      titre={modeModification ? "Modifier le corps d'état" : "Nouveau corps d'état"}
      description="Métier auquel se rattachent les étapes"
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            Annuler
          </Button>
          <Button
            variante="primaire"
            type="submit"
            form="formulaire-corps-etat"
            enChargement={enCours}
          >
            {modeModification ? 'Enregistrer' : 'Créer'}
          </Button>
        </>
      }
    >
      <form
        id="formulaire-corps-etat"
        onSubmit={soumettre}
        className="flex flex-col gap-4"
        noValidate
      >
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Code" requis={!modeModification} erreur={erreurs.code}>
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.code)}
                value={code}
                disabled={modeModification}
                onChange={(evenement) => setCode(evenement.target.value)}
                placeholder="ex. GO"
              />
            )}
          </FormField>

          <FormField libelle="Ordre d'affichage" requis>
            {(champ) => (
              <Input
                {...champ}
                type="number"
                min={1}
                value={ordre}
                onChange={(evenement) => setOrdre(Number(evenement.target.value) || 1)}
              />
            )}
          </FormField>
        </div>

        <FormField libelle="Libellé" requis erreur={erreurs.libelle}>
          {(champ) => (
            <Input
              {...champ}
              invalide={Boolean(erreurs.libelle)}
              value={libelle}
              onChange={(evenement) => setLibelle(evenement.target.value)}
              placeholder="ex. Gros œuvre"
            />
          )}
        </FormField>

        <FormField
          libelle="Couleur"
          aide="Utilisée pour repérer le corps d'état dans les tableaux."
        >
          {(champ) => (
            <div className="flex items-center gap-3">
              <input
                {...champ}
                type="color"
                value={couleur}
                onChange={(evenement) => setCouleur(evenement.target.value)}
                className="h-10 w-16 cursor-pointer rounded-lg border border-bordure bg-fond"
              />
              <span className="text-sm text-texte-secondaire">{couleur}</span>
            </div>
          )}
        </FormField>
      </form>
    </Modal>
  )
}
