/*
  Création et modification d'une règle de validation (EF-REF-08).

  Une règle porte sur un type d'événement, teste un champ avec un opérateur, et
  compare soit à une valeur seuil, soit à un délai en heures. Les deux ne sont
  pas exclusifs côté modèle, mais une règle en renseigne généralement un seul :
  un seuil pour un écart, un délai pour une échéance.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { creerRegle, modifierRegle } from '@/features/parametrage/api'
import { OPERATEURS, TYPES_EVENEMENT } from '@/features/parametrage/presentation/libelles'
import type {
  OperateurRegle,
  RegleValidation,
  SaisieRegle,
  TypeEvenement,
} from '@/features/parametrage/types'

export type FormulaireRegleProps = {
  ouvert: boolean
  onFermer: () => void
  regle: RegleValidation | null
  onEnregistre: () => void
}

type Erreurs = { champTeste?: string; bornes?: string }

export function FormulaireRegle({ ouvert, onFermer, regle, onEnregistre }: FormulaireRegleProps) {
  const { afficherToast } = useToast()
  const modeModification = regle !== null

  const [typeEvenement, setTypeEvenement] = useState<TypeEvenement>('validation_etape')
  const [champTeste, setChampTeste] = useState('')
  const [operateur, setOperateur] = useState<OperateurRegle>('inferieur_egal')
  const [valeurSeuil, setValeurSeuil] = useState('')
  const [delaiHeures, setDelaiHeures] = useState('')
  const [erreurs, setErreurs] = useState<Erreurs>({})
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert) return
    setTypeEvenement(regle?.typeEvenement ?? 'validation_etape')
    setChampTeste(regle?.champTeste ?? '')
    setOperateur(regle?.operateur ?? 'inferieur_egal')
    setValeurSeuil(regle?.valeurSeuil != null ? String(regle.valeurSeuil) : '')
    setDelaiHeures(regle?.delaiHeures != null ? String(regle.delaiHeures) : '')
    setErreurs({})
  }, [ouvert, regle])

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()
    const prochaines: Erreurs = {}
    if (champTeste.trim() === '') prochaines.champTeste = 'Saisir le champ testé.'
    if (valeurSeuil.trim() === '' && delaiHeures.trim() === '') {
      prochaines.bornes = 'Renseigner au moins une valeur seuil ou un délai.'
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) return

    const saisie: SaisieRegle = {
      typeEvenement,
      champTeste: champTeste.trim(),
      operateur,
      valeurSeuil: valeurSeuil.trim() === '' ? null : Number(valeurSeuil),
      delaiHeures: delaiHeures.trim() === '' ? null : Number.parseInt(delaiHeures, 10),
    }

    setEnCours(true)
    try {
      if (modeModification && regle) {
        await modifierRegle(regle.id, saisie)
      } else {
        await creerRegle(saisie)
      }
      afficherToast({
        ton: 'succes',
        titre: modeModification ? 'Règle modifiée' : 'Règle créée',
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "La règle n'a pas pu être enregistrée",
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
      titre={modeModification ? 'Modifier la règle' : 'Nouvelle règle de validation'}
      description="Condition portant sur un événement du système"
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            Annuler
          </Button>
          <Button variante="primaire" type="submit" form="formulaire-regle" enChargement={enCours}>
            {modeModification ? 'Enregistrer' : 'Créer'}
          </Button>
        </>
      }
    >
      <form id="formulaire-regle" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
        <FormField libelle="Type d'événement" requis>
          {(champ) => (
            <Select
              {...champ}
              value={typeEvenement}
              onChange={(evenement) => setTypeEvenement(evenement.target.value as TypeEvenement)}
            >
              {TYPES_EVENEMENT.map((entree) => (
                <option key={entree.valeur} value={entree.valeur}>
                  {entree.libelle}
                </option>
              ))}
            </Select>
          )}
        </FormField>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField
            libelle="Champ testé"
            requis
            erreur={erreurs.champTeste}
            aide="ex. ecart_pourcent, delai_validation"
          >
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.champTeste)}
                value={champTeste}
                onChange={(evenement) => setChampTeste(evenement.target.value)}
              />
            )}
          </FormField>

          <FormField libelle="Opérateur" requis>
            {(champ) => (
              <Select
                {...champ}
                value={operateur}
                onChange={(evenement) => setOperateur(evenement.target.value as OperateurRegle)}
              >
                {OPERATEURS.map((entree) => (
                  <option key={entree.valeur} value={entree.valeur}>
                    {entree.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Valeur seuil" aide="Nombre comparé au champ testé.">
            {(champ) => (
              <Input
                {...champ}
                type="number"
                step="0.001"
                value={valeurSeuil}
                onChange={(evenement) => setValeurSeuil(evenement.target.value)}
              />
            )}
          </FormField>

          <FormField libelle="Délai (heures)" aide="Échéance en heures, pour une règle de délai.">
            {(champ) => (
              <Input
                {...champ}
                type="number"
                min={0}
                value={delaiHeures}
                onChange={(evenement) => setDelaiHeures(evenement.target.value)}
              />
            )}
          </FormField>
        </div>

        {erreurs.bornes && <p className="text-sm text-danger">{erreurs.bornes}</p>}
      </form>
    </Modal>
  )
}
