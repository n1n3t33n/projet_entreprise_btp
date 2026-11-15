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
import { tr } from '@/i18n/tr'

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
      prochaines.code = tr('Saisir un code zone.')
    }
    if (nom.trim() === '') {
      prochaines.nom = tr('Saisir un nom.')
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
        titre: modeModification ? tr('Zone modifiée') : tr('Zone créée'),
        message: `${saisie.code} · ${saisie.nom}`,
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: tr("La zone n'a pas pu être enregistrée"),
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
      titre={modeModification ? tr('Modifier la zone') : tr('Nouvelle zone')}
      description={tr('Découpage du chantier')}
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            {tr('Annuler')}
          </Button>
          <Button variante="primaire" type="submit" form="formulaire-zone" enChargement={enCours}>
            {modeModification ? tr('Enregistrer') : tr('Créer la zone')}
          </Button>
        </>
      }
    >
      <form id="formulaire-zone" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle={tr('Code zone')} requis erreur={erreurs.code}>
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

          <FormField libelle={tr('Type de zone')} requis>
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

        <FormField libelle={tr('Nom')} requis erreur={erreurs.nom}>
          {(champ) => (
            <Input
              {...champ}
              invalide={Boolean(erreurs.nom)}
              value={nom}
              onChange={(evenement) => setNom(evenement.target.value)}
              placeholder={tr('ex. Bâtiment A')}
            />
          )}
        </FormField>
      </form>
    </Modal>
  )
}
