/*
  Création et modification d'une zone rattachée à un chantier (EF-REF-01).

  Le chantier de rattachement est imposé par le contexte (zone créée sous le
  chantier affiché) : il n'est pas choisi dans le formulaire.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { creerZone, modifierZone } from '@/features/referentiels/api'
import { TYPES_ZONE } from '@/features/referentiels/presentation/libelles'
import type { SaisieZone, TypeZone, Zone } from '@/features/referentiels/types'

export type FormulaireZoneProps = {
  ouvert: boolean
  onFermer: () => void
  /** Zone à modifier, ou `null` pour une création. */
  zone: Zone | null
  /** Chantier de rattachement, imposé par le contexte. */
  idChantier: string
  onEnregistre: () => void
}

type ErreursZone = { code?: string; nom?: string }

export function FormulaireZone({
  ouvert,
  onFermer,
  zone,
  idChantier,
  onEnregistre,
}: FormulaireZoneProps) {
  const { afficherToast } = useToast()
  const modeModification = zone !== null

  const [code, setCode] = useState('')
  const [nom, setNom] = useState('')
  const [typeZone, setTypeZone] = useState<TypeZone>('batiment')
  const [erreurs, setErreurs] = useState<ErreursZone>({})
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert) {
      return
    }
    setCode(zone?.code ?? '')
    setNom(zone?.nom ?? '')
    setTypeZone(zone?.typeZone ?? 'batiment')
    setErreurs({})
  }, [ouvert, zone])

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()

    const prochaines: ErreursZone = {}
    if (code.trim() === '') {
      prochaines.code = 'Saisir un code zone.'
    }
    if (nom.trim() === '') {
      prochaines.nom = 'Saisir un nom.'
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) {
      return
    }

    const saisie: SaisieZone = {
      code: code.trim(),
      nom: nom.trim(),
      typeZone,
      idChantier,
    }

    setEnCours(true)
    try {
      if (modeModification && zone) {
        await modifierZone(zone.id, saisie)
      } else {
        await creerZone(saisie)
      }
      afficherToast({
        ton: 'succes',
        titre: modeModification ? 'Zone modifiée' : 'Zone créée',
        message: `${saisie.code} · ${saisie.nom}`,
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "La zone n'a pas pu être enregistrée",
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
      titre={modeModification ? 'Modifier la zone' : 'Nouvelle zone'}
      description="Découpage du chantier"
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            Annuler
          </Button>
          <Button variante="primaire" type="submit" form="formulaire-zone" enChargement={enCours}>
            {modeModification ? 'Enregistrer' : 'Créer la zone'}
          </Button>
        </>
      }
    >
      <form id="formulaire-zone" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Code zone" requis erreur={erreurs.code}>
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.code)}
                value={code}
                onChange={(evenement) => setCode(evenement.target.value)}
                placeholder="ex. BAT-A"
              />
            )}
          </FormField>

          <FormField libelle="Type de zone" requis>
            {(champ) => (
              <Select
                {...champ}
                value={typeZone}
                onChange={(evenement) => setTypeZone(evenement.target.value as TypeZone)}
              >
                {TYPES_ZONE.map((entree) => (
                  <option key={entree.valeur} value={entree.valeur}>
                    {entree.libelle}
                  </option>
                ))}
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
              placeholder="ex. Bâtiment A"
            />
          )}
        </FormField>
      </form>
    </Modal>
  )
}
