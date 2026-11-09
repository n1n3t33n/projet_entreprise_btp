/*
  Création et modification d'un compte nominatif (EF-AUT-01), avec son rôle et
  son périmètre (EF-AUT-02).

  Un seul formulaire pour les deux cas. Le mot de passe n'est pas saisi ici :
  EF-AUT-09 prévoit une réinitialisation dédiée, et un compte créé reçoit son
  mot de passe par ce canal — l'administrateur ne choisit jamais le secret d'un
  autre utilisateur.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Button, FormField, Input, Modal, Select, useToast } from '@/components/ui'
import { ROLES, type Role } from '@/app/role-context'
import { creerCompte, modifierCompte } from '@/features/auth/api'
import type {
  Perimetre,
  SaisieCompte,
  StatutCompte,
  Utilisateur,
} from '@/features/auth/types/domaine'

export type FormulaireCompteProps = {
  ouvert: boolean
  onFermer: () => void
  /** Compte à modifier, ou `null` pour une création. */
  compte: Utilisateur | null
  perimetres: Perimetre[]
  onEnregistre: () => void
}

type ErreursCompte = {
  identifiant?: string
  nom?: string
  prenom?: string
  perimetre?: string
}

export function FormulaireCompte({
  ouvert,
  onFermer,
  compte,
  perimetres,
  onEnregistre,
}: FormulaireCompteProps) {
  const { afficherToast } = useToast()
  const modeModification = compte !== null

  const [identifiant, setIdentifiant] = useState('')
  const [nom, setNom] = useState('')
  const [prenom, setPrenom] = useState('')
  const [fonction, setFonction] = useState('')
  const [role, setRole] = useState<Role>('responsable_technique')
  const [idPerimetre, setIdPerimetre] = useState('')
  const [statut, setStatut] = useState<StatutCompte>('actif')
  const [erreurs, setErreurs] = useState<ErreursCompte>({})
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert) {
      return
    }
    setIdentifiant(compte?.identifiant ?? '')
    setNom(compte?.nom ?? '')
    setPrenom(compte?.prenom ?? '')
    setFonction(compte?.fonction ?? '')
    setRole(compte?.role ?? 'responsable_technique')
    setIdPerimetre(compte?.idPerimetre ?? perimetres[0]?.id ?? '')
    setStatut(compte?.statut ?? 'actif')
    setErreurs({})
  }, [ouvert, compte, perimetres])

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()

    const prochaines: ErreursCompte = {}
    if (identifiant.trim() === '') {
      prochaines.identifiant = 'Saisir un identifiant de connexion.'
    }
    if (nom.trim() === '') {
      prochaines.nom = 'Saisir un nom.'
    }
    if (prenom.trim() === '') {
      prochaines.prenom = 'Saisir un prénom.'
    }
    if (idPerimetre === '') {
      prochaines.perimetre = 'Choisir un périmètre.'
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0) {
      return
    }

    const saisie: SaisieCompte = {
      identifiant: identifiant.trim(),
      nom: nom.trim(),
      prenom: prenom.trim(),
      fonction: fonction.trim(),
      role,
      idPerimetre,
      statut,
    }

    setEnCours(true)
    try {
      if (modeModification && compte) {
        await modifierCompte(compte.id, saisie)
      } else {
        await creerCompte(saisie)
      }
      afficherToast({
        ton: 'succes',
        titre: modeModification ? 'Compte modifié' : 'Compte créé',
        message: `${saisie.prenom} ${saisie.nom} · ${saisie.identifiant}`,
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "Le compte n'a pas pu être enregistré",
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
      titre={modeModification ? 'Modifier le compte' : 'Nouveau compte'}
      description="Compte nominatif, rôle et périmètre"
      actions={
        <>
          <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
            Annuler
          </Button>
          <Button variante="primaire" type="submit" form="formulaire-compte" enChargement={enCours}>
            {modeModification ? 'Enregistrer' : 'Créer le compte'}
          </Button>
        </>
      }
    >
      <form id="formulaire-compte" onSubmit={soumettre} className="flex flex-col gap-4" noValidate>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Prénom" requis erreur={erreurs.prenom}>
            {(champ) => (
              <Input
                {...champ}
                invalide={Boolean(erreurs.prenom)}
                value={prenom}
                onChange={(evenement) => setPrenom(evenement.target.value)}
              />
            )}
          </FormField>

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
        </div>

        <FormField
          libelle="Identifiant de connexion"
          requis
          erreur={erreurs.identifiant}
          aide="Unique. Sert à se connecter au poste de pilotage."
        >
          {(champ) => (
            <Input
              {...champ}
              invalide={Boolean(erreurs.identifiant)}
              value={identifiant}
              onChange={(evenement) => setIdentifiant(evenement.target.value)}
              placeholder="ex. k.n-guessan"
            />
          )}
        </FormField>

        <FormField libelle="Fonction" aide="Intitulé du poste, affiché dans les journaux.">
          {(champ) => (
            <Input
              {...champ}
              value={fonction}
              onChange={(evenement) => setFonction(evenement.target.value)}
              placeholder="ex. Conducteur de travaux"
            />
          )}
        </FormField>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField libelle="Rôle" requis aide="Décide des écrans accessibles, via la matrice.">
            {(champ) => (
              <Select
                {...champ}
                value={role}
                onChange={(evenement) => setRole(evenement.target.value as Role)}
              >
                {ROLES.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>

          <FormField libelle="Périmètre" requis erreur={erreurs.perimetre}>
            {(champ) => (
              <Select
                {...champ}
                invalide={Boolean(erreurs.perimetre)}
                value={idPerimetre}
                onChange={(evenement) => setIdPerimetre(evenement.target.value)}
              >
                <option value="">— Choisir —</option>
                {perimetres.map((perimetre) => (
                  <option key={perimetre.id} value={perimetre.id}>
                    {perimetre.libelle}
                  </option>
                ))}
              </Select>
            )}
          </FormField>
        </div>

        <label className="flex items-center gap-2 text-sm text-texte">
          <input
            type="checkbox"
            checked={statut === 'actif'}
            onChange={(evenement) => setStatut(evenement.target.checked ? 'actif' : 'inactif')}
            className="size-4 rounded border-bordure text-marine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
          />
          Compte actif (un compte désactivé ne peut plus se connecter)
        </label>
      </form>
    </Modal>
  )
}
