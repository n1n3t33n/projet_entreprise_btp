/*
  Création et modification d'un logement rattaché à une zone (EF-REF-01).

  La zone de rattachement est imposée par le contexte. Le statut est
  administratif (actif / inactif) : l'avancement des travaux est porté par les
  étapes du module avancement, pas par cet attribut.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { creerLogement, modifierLogement } from '@/features/referentiels/api'
import { libelleStatut } from '@/features/referentiels/presentation/libelles'
import type {
  Logement,
  SaisieLogement,
  StatutLogement,
  TypeLogement,
} from '@/features/referentiels/types'

export type FormulaireLogementProps = {
  ouvert: boolean
  onFermer: () => void
  /** Logement à modifier, ou `null` pour une création. */
  logement: Logement | null
  /** Zone de rattachement, imposée par le contexte. */
  idZone: string
  typesLogement: TypeLogement[]
  onEnregistre: () => void
}

type ErreursLogement = { numero?: string; type?: string }

export function FormulaireLogement({
  ouvert,
  onFermer,
  logement,
  idZone,
  typesLogement,
  onEnregistre,
}: FormulaireLogementProps) {
  const { afficherToast } = useToast()
  const modeModification = logement !== null

  const [numero, setNumero] = useState('')
  const [codeType, setCodeType] = useState('')
  const [statut, setStatut] = useState<StatutLogement>('actif')
  const [dateLivraison, setDateLivraison] = useState('')
  const [erreurs, setErreurs] = useState<ErreursLogement>({})
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert) {
      return
    }
    setNumero(logement?.numero ?? '')
    setCodeType(logement?.codeTypeLogement ?? '')
    setStatut(logement?.statut ?? 'actif')
    setDateLivraison(logement?.dateLivraisonPrevue ?? '')
    setErreurs({})
  }, [ouvert, logement])

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()

    const prochaines: ErreursLogement = {}
    if (numero.trim() === '') {
      prochaines.numero = 'Saisir un numéro de logement.'
    }
    if (codeType === '') {
      prochaines.type = 'Choisir un type de logement.'
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) {
      return
    }

    const saisie: SaisieLogement = {
      numero: numero.trim(),
      statut,
      dateLivraisonPrevue: dateLivraison === '' ? null : dateLivraison,
      idZone,
      codeTypeLogement: codeType,
    }

    setEnCours(true)
    try {
      if (modeModification && logement) {
        await modifierLogement(logement.id, saisie)
      } else {
        await creerLogement(saisie)
      }
      afficherToast({
        ton: 'succes',
        titre: modeModification ? 'Logement modifié' : 'Logement créé',
        message: saisie.numero,
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "Le logement n'a pas pu être enregistré",
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
      titre={modeModification ? 'Modifier le logement' : 'Nouveau logement'}
      description="Logement de la zone"
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            Annuler
          </Button>
          <Button variante="primaire" type="submit" form="formulaire-logement" enChargement={enCours}>
            {modeModification ? 'Enregistrer' : 'Créer le logement'}
          </Button>
        </>
      }
    >
      <form id="formulaire-logement" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Numéro" requis erreur={erreurs.numero}>
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.numero)}
                value={numero}
                onChange={(evenement) => setNumero(evenement.target.value)}
                placeholder="ex. A-101"
              />
            )}
          </FormField>

          <FormField libelle="Type de logement" requis erreur={erreurs.type}>
            {(champ) => (
              <Select
                {...champ}
                invalide={Boolean(erreurs.type)}
                value={codeType}
                onChange={(evenement) => setCodeType(evenement.target.value)}
              >
                <option value="">— Choisir —</option>
                {typesLogement.map((type) => (
                  <option key={type.code} value={type.code}>
                    {type.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Statut" requis>
            {(champ) => (
              <Select
                {...champ}
                value={statut}
                onChange={(evenement) => setStatut(evenement.target.value as StatutLogement)}
              >
                <option value="actif">{libelleStatut('actif')}</option>
                <option value="inactif">{libelleStatut('inactif')}</option>
              </Select>
            )}
          </FormField>

          <FormField libelle="Livraison prévue" aide="Facultatif.">
            {(champ) => (
              <Input
                {...champ}
                type="date"
                value={dateLivraison}
                onChange={(evenement) => setDateLivraison(evenement.target.value)}
              />
            )}
          </FormField>
        </div>
      </form>
    </Modal>
  )
}
