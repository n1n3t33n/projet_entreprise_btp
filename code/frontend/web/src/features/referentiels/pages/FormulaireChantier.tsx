/*
  Modification des informations d'un chantier (EF-REF-01).

  La création d'un chantier relève d'un acte d'ouverture de programme, hors du
  périmètre de cette étape : ce formulaire ne fait que modifier un chantier
  existant.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { modifierChantier } from '@/features/referentiels/api'
import { libelleStatut } from '@/features/referentiels/presentation/libelles'
import type { Chantier, SaisieChantier, StatutChantier } from '@/features/referentiels/types'

export type FormulaireChantierProps = {
  ouvert: boolean
  onFermer: () => void
  chantier: Chantier | null
  onEnregistre: () => void
}

type ErreursChantier = { code?: string; nom?: string; dateDebut?: string }

export function FormulaireChantier({
  ouvert,
  onFermer,
  chantier,
  onEnregistre,
}: FormulaireChantierProps) {
  const { afficherToast } = useToast()

  const [code, setCode] = useState('')
  const [nom, setNom] = useState('')
  const [programme, setProgramme] = useState('')
  const [dateDebut, setDateDebut] = useState('')
  const [statut, setStatut] = useState<StatutChantier>('actif')
  const [erreurs, setErreurs] = useState<ErreursChantier>({})
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert || !chantier) {
      return
    }
    setCode(chantier.code)
    setNom(chantier.nom)
    setProgramme(chantier.programme)
    setDateDebut(chantier.dateDebut)
    setStatut(chantier.statut)
    setErreurs({})
  }, [ouvert, chantier])

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()
    if (!chantier) {
      return
    }

    const prochaines: ErreursChantier = {}
    if (code.trim() === '') {
      prochaines.code = 'Saisir un code chantier.'
    }
    if (nom.trim() === '') {
      prochaines.nom = 'Saisir un nom.'
    }
    if (dateDebut === '') {
      prochaines.dateDebut = 'Choisir une date de début.'
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) {
      return
    }

    const saisie: SaisieChantier = {
      code: code.trim(),
      nom: nom.trim(),
      programme: programme.trim(),
      dateDebut,
      statut,
    }

    setEnCours(true)
    try {
      await modifierChantier(chantier.id, saisie)
      afficherToast({ ton: 'succes', titre: 'Chantier modifié', message: saisie.nom })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "Le chantier n'a pas pu être enregistré",
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
      titre="Modifier le chantier"
      description="Informations générales du chantier"
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            Annuler
          </Button>
          <Button
            variante="primaire"
            type="submit"
            form="formulaire-chantier"
            enChargement={enCours}
          >
            Enregistrer
          </Button>
        </>
      }
    >
      <form
        id="formulaire-chantier"
        onSubmit={soumettre}
        className="flex flex-col gap-4"
        noValidate
      >
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Code chantier" requis erreur={erreurs.code}>
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.code)}
                value={code}
                onChange={(evenement) => setCode(evenement.target.value)}
              />
            )}
          </FormField>

          <FormField libelle="Statut" requis>
            {(champ) => (
              <Select
                {...champ}
                value={statut}
                onChange={(evenement) => setStatut(evenement.target.value as StatutChantier)}
              >
                <option value="actif">{libelleStatut('actif')}</option>
                <option value="inactif">{libelleStatut('inactif')}</option>
              </Select>
            )}
          </FormField>
        </div>

        <FormField libelle="Nom" requis erreur={erreurs.nom}>
          {(champ) => (
            <Input
              {...champ}
              invalide={Boolean(erreurs.nom)}
              value={nom}
              onChange={(evenement) => setNom(evenement.target.value)}
            />
          )}
        </FormField>

        <FormField libelle="Programme" aide="Nom du programme immobilier.">
          {(champ) => (
            <Input
              {...champ}
              value={programme}
              onChange={(evenement) => setProgramme(evenement.target.value)}
            />
          )}
        </FormField>

        <FormField libelle="Date de début" requis erreur={erreurs.dateDebut}>
          {(champ) => (
            <Input
              {...champ}
              type="date"
              invalide={Boolean(erreurs.dateDebut)}
              value={dateDebut}
              onChange={(evenement) => setDateDebut(evenement.target.value)}
            />
          )}
        </FormField>
      </form>
    </Modal>
  )
}
