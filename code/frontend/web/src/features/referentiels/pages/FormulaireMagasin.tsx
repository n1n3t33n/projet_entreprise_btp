/*
  Création et modification d'un magasin (EF-REF-02).

  Un seul formulaire pour les deux cas, sur le modèle du formulaire d'article.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { creerMagasin, modifierMagasin } from '@/features/referentiels/api'
import type { Chantier, MagasinVue, SaisieMagasin } from '@/features/referentiels/types'

export type FormulaireMagasinProps = {
  ouvert: boolean
  onFermer: () => void
  /** Magasin à modifier, ou `null` pour une création. */
  magasin: MagasinVue | null
  chantiers: Chantier[]
  onEnregistre: () => void
}

type ErreursMagasin = { code?: string; nom?: string; chantier?: string }

export function FormulaireMagasin({
  ouvert,
  onFermer,
  magasin,
  chantiers,
  onEnregistre,
}: FormulaireMagasinProps) {
  const { afficherToast } = useToast()
  const modeModification = magasin !== null

  const [code, setCode] = useState('')
  const [nom, setNom] = useState('')
  const [idChantier, setIdChantier] = useState('')
  const [actif, setActif] = useState(true)
  const [erreurs, setErreurs] = useState<ErreursMagasin>({})
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert) {
      return
    }
    setCode(magasin?.code ?? '')
    setNom(magasin?.nom ?? '')
    setIdChantier(magasin?.idChantier ?? chantiers[0]?.id ?? '')
    setActif(magasin?.actif ?? true)
    setErreurs({})
  }, [ouvert, magasin, chantiers])

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()

    const prochaines: ErreursMagasin = {}
    if (code.trim() === '') {
      prochaines.code = 'Saisir un code magasin.'
    }
    if (nom.trim() === '') {
      prochaines.nom = 'Saisir un nom.'
    }
    if (idChantier === '') {
      prochaines.chantier = 'Choisir un chantier de rattachement.'
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) {
      return
    }

    const saisie: SaisieMagasin = {
      code: code.trim(),
      nom: nom.trim(),
      actif,
      idChantier,
    }

    setEnCours(true)
    try {
      if (modeModification && magasin) {
        await modifierMagasin(magasin.id, saisie)
      } else {
        await creerMagasin(saisie)
      }
      afficherToast({
        ton: 'succes',
        titre: modeModification ? 'Magasin modifié' : 'Magasin créé',
        message: `${saisie.code} · ${saisie.nom}`,
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "Le magasin n'a pas pu être enregistré",
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
      titre={modeModification ? 'Modifier le magasin' : 'Nouveau magasin'}
      description="Référentiel des magasins"
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            Annuler
          </Button>
          <Button
            variante="primaire"
            type="submit"
            form="formulaire-magasin"
            enChargement={enCours}
          >
            {modeModification ? 'Enregistrer' : 'Créer le magasin'}
          </Button>
        </>
      }
    >
      <form id="formulaire-magasin" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Code magasin" requis erreur={erreurs.code}>
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.code)}
                value={code}
                onChange={(evenement) => setCode(evenement.target.value)}
                placeholder="ex. MAG-GB"
              />
            )}
          </FormField>

          <FormField libelle="Chantier de rattachement" requis erreur={erreurs.chantier}>
            {(champ) => (
              <Select
                {...champ}
                invalide={Boolean(erreurs.chantier)}
                value={idChantier}
                onChange={(evenement) => setIdChantier(evenement.target.value)}
              >
                <option value="">— Choisir —</option>
                {chantiers.map((chantier) => (
                  <option key={chantier.id} value={chantier.id}>
                    {chantier.nom}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        </div>

        <FormField libelle="Nom du magasin" requis erreur={erreurs.nom}>
          {(champ) => (
            <Input
              {...champ}
              invalide={Boolean(erreurs.nom)}
              value={nom}
              onChange={(evenement) => setNom(evenement.target.value)}
              placeholder="ex. Magasin central"
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
          Magasin actif
        </label>
      </form>
    </Modal>
  )
}
