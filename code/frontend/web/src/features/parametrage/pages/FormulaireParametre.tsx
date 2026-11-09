/*
  Création et modification d'un paramètre de chantier (EF-REF-07).

  Le champ de saisie de la valeur s'adapte au type : un nombre pour entier et
  décimal, un choix oui/non pour un booléen, un texte libre sinon. La clé
  identifie le paramètre (CL-2 `Chantier.parametre(cle)`) : elle n'est pas
  modifiable sur un paramètre existant.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { creerParametre, modifierParametre } from '@/features/parametrage/api'
import { TYPES_VALEUR } from '@/features/parametrage/presentation/libelles'
import type { ParametreChantier, SaisieParametre, TypeValeur } from '@/features/parametrage/types'

export type FormulaireParametreProps = {
  ouvert: boolean
  onFermer: () => void
  parametre: ParametreChantier | null
  onEnregistre: () => void
}

type Erreurs = { cle?: string; valeur?: string }

export function FormulaireParametre({
  ouvert,
  onFermer,
  parametre,
  onEnregistre,
}: FormulaireParametreProps) {
  const { afficherToast } = useToast()
  const modeModification = parametre !== null

  const [cle, setCle] = useState('')
  const [typeValeur, setTypeValeur] = useState<TypeValeur>('texte')
  const [valeur, setValeur] = useState('')
  const [libelle, setLibelle] = useState('')
  const [erreurs, setErreurs] = useState<Erreurs>({})
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert) return
    setCle(parametre?.cle ?? '')
    setTypeValeur(parametre?.typeValeur ?? 'texte')
    setValeur(parametre?.valeur ?? '')
    setLibelle(parametre?.libelle ?? '')
    setErreurs({})
  }, [ouvert, parametre])

  // Quand on bascule vers un booléen, on normalise la valeur sur « true ».
  useEffect(() => {
    if (typeValeur === 'booleen' && valeur !== 'true' && valeur !== 'false') {
      setValeur('true')
    }
  }, [typeValeur, valeur])

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()
    const prochaines: Erreurs = {}
    if (!modeModification && cle.trim() === '') prochaines.cle = 'Saisir une clé.'
    if (valeur.trim() === '') prochaines.valeur = 'Saisir une valeur.'
    if ((typeValeur === 'entier' || typeValeur === 'decimal') && Number.isNaN(Number(valeur))) {
      prochaines.valeur = 'Saisir un nombre valide.'
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) return

    const saisie: SaisieParametre = {
      cle: cle.trim(),
      valeur: valeur.trim(),
      typeValeur,
      libelle: libelle.trim() === '' ? null : libelle.trim(),
    }

    setEnCours(true)
    try {
      if (modeModification && parametre) {
        await modifierParametre(parametre.id, saisie)
      } else {
        await creerParametre(saisie)
      }
      afficherToast({
        ton: 'succes',
        titre: modeModification ? 'Paramètre modifié' : 'Paramètre créé',
        message: `${saisie.cle} = ${saisie.valeur}`,
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "Le paramètre n'a pas pu être enregistré",
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
      titre={modeModification ? 'Modifier le paramètre' : 'Nouveau paramètre'}
      description="Réglage du chantier"
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            Annuler
          </Button>
          <Button
            variante="primaire"
            type="submit"
            form="formulaire-parametre"
            enChargement={enCours}
          >
            {modeModification ? 'Enregistrer' : 'Créer'}
          </Button>
        </>
      }
    >
      <form
        id="formulaire-parametre"
        onSubmit={soumettre}
        className="flex flex-col gap-4"
        noValidate
      >
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Clé" requis={!modeModification} erreur={erreurs.cle}>
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.cle)}
                value={cle}
                disabled={modeModification}
                onChange={(evenement) => setCle(evenement.target.value)}
                placeholder="ex. delai_synchro_alerte_h"
              />
            )}
          </FormField>

          <FormField libelle="Type de valeur" requis>
            {(champ) => (
              <Select
                {...champ}
                value={typeValeur}
                onChange={(evenement) => setTypeValeur(evenement.target.value as TypeValeur)}
              >
                {TYPES_VALEUR.map((entree) => (
                  <option key={entree.valeur} value={entree.valeur}>
                    {entree.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        </div>

        <FormField libelle="Valeur" requis erreur={erreurs.valeur}>
          {(champ) =>
            typeValeur === 'booleen' ? (
              <Select {...champ} value={valeur} onChange={(e) => setValeur(e.target.value)}>
                <option value="true">Oui</option>
                <option value="false">Non</option>
              </Select>
            ) : (
              <Input
                {...champ}
                type={typeValeur === 'entier' || typeValeur === 'decimal' ? 'number' : 'text'}
                step={typeValeur === 'decimal' ? '0.01' : typeValeur === 'entier' ? '1' : undefined}
                invalide={Boolean(erreurs.valeur)}
                value={valeur}
                onChange={(evenement) => setValeur(evenement.target.value)}
              />
            )
          }
        </FormField>

        <FormField libelle="Libellé" aide="Description lisible du paramètre (facultatif).">
          {(champ) => (
            <Input
              {...champ}
              value={libelle}
              onChange={(evenement) => setLibelle(evenement.target.value)}
              placeholder="ex. Seuil d'alerte de synchronisation (heures)"
            />
          )}
        </FormField>
      </form>
    </Modal>
  )
}
