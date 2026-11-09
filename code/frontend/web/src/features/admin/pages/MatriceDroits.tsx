/*
  Matrice des droits : qui accède à quel écran (charte § 9.2, écran 12).

  Une ligne par écran, une colonne par rôle, une case à cocher par croisement.
  Cocher revient à `Role.accorder(permission)` de CL-1, décocher à
  `Role.retirer(permission)`. Les modifications restent locales jusqu'à
  l'enregistrement, pour qu'une suite de clics forme une seule décision.

  Le croisement « Administration × Administrateur » est verrouillé : le retirer
  rendrait la matrice définitivement non modifiable.
*/

import { useMemo, useState } from 'react'
import { ArrowCounterClockwise, FloppyDisk } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, StatusPill, Table, useToast } from '@/components/ui'
import { useDroits } from '@/app/droits-context'
import { ECRANS, type EntreeNavigation, type IdEcran } from '@/config/navigation'
import { enregistrerDroits } from '@/features/admin/api'
import { ECRAN_VERROUILLE, ROLE_VERROUILLE } from '@/features/admin/config/capacites'
import type { DroitAccorde, EtatDroits } from '@/features/admin/types/domaine'

export type MatriceDroitsProps = {
  etat: EtatDroits
  peutModifier: boolean
}

/** Clé d'une case de la matrice. */
function cle(codeRole: string, codePermission: string): string {
  return `${codeRole}::${codePermission}`
}

export function MatriceDroits({ etat, peutModifier }: MatriceDroitsProps) {
  const { afficherToast } = useToast()
  const { recharger } = useDroits()

  /** Permission de lecture associée à chaque écran (MPD-1 : `action = 'lire'`). */
  const permissionParEcran = useMemo(() => {
    const index = new Map<IdEcran, string>()
    for (const permission of etat.permissions) {
      if (permission.action === 'lire') {
        index.set(permission.idEcran, permission.code)
      }
    }
    return index
  }, [etat.permissions])

  const accordesInitiaux = useMemo(
    () => new Set(etat.accordes.map((droit) => cle(droit.codeRole, droit.codePermission))),
    [etat.accordes],
  )

  const [coches, setCoches] = useState<Set<string>>(accordesInitiaux)
  const [enCours, setEnCours] = useState(false)

  const modifie = useMemo(() => {
    if (coches.size !== accordesInitiaux.size) {
      return true
    }
    for (const valeur of coches) {
      if (!accordesInitiaux.has(valeur)) {
        return true
      }
    }
    return false
  }, [coches, accordesInitiaux])

  const roles = useMemo(() => etat.roles.filter((role) => role.actif), [etat.roles])

  function estVerrouille(idEcran: IdEcran, codeRole: string): boolean {
    return idEcran === ECRAN_VERROUILLE && codeRole === ROLE_VERROUILLE
  }

  function basculer(idEcran: IdEcran, codeRole: string) {
    const codePermission = permissionParEcran.get(idEcran)
    if (!codePermission || estVerrouille(idEcran, codeRole)) {
      return
    }
    setCoches((precedent) => {
      const suivant = new Set(precedent)
      const identifiant = cle(codeRole, codePermission)
      if (suivant.has(identifiant)) {
        suivant.delete(identifiant)
      } else {
        suivant.add(identifiant)
      }
      return suivant
    })
  }

  async function enregistrer() {
    const droits: DroitAccorde[] = []
    for (const identifiant of coches) {
      const [codeRole, codePermission] = identifiant.split('::')
      if (codeRole && codePermission) {
        droits.push({ codeRole, codePermission, portee: 'globale' })
      }
    }

    setEnCours(true)
    try {
      await enregistrerDroits(droits)
      afficherToast({
        ton: 'succes',
        titre: 'Droits enregistrés',
        message: 'Les menus et les accès sont mis à jour immédiatement.',
      })
      recharger()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "Les droits n'ont pas pu être enregistrés",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  const colonnes: ColonneTable<EntreeNavigation>[] = [
    {
      cle: 'ecran',
      entete: 'Écran',
      rendu: (ecran) => <span className="font-medium text-marine">{ecran.libelle}</span>,
    },
    ...roles.map<ColonneTable<EntreeNavigation>>((role) => ({
      cle: role.code,
      entete: role.libelle,
      alignement: 'centre',
      largeur: '9rem',
      rendu: (ecran) => {
        const codePermission = permissionParEcran.get(ecran.id)
        if (!codePermission) {
          return <span className="text-xs text-texte-attenue">—</span>
        }
        const verrouille = estVerrouille(ecran.id, role.code)
        const coche = coches.has(cle(role.code, codePermission))
        return (
          <input
            type="checkbox"
            checked={coche}
            disabled={!peutModifier || verrouille}
            onChange={() => basculer(ecran.id, role.code)}
            aria-label={`${role.libelle} — accès à l'écran ${ecran.libelle}`}
            title={
              verrouille
                ? 'Accès obligatoire : sans lui, plus personne ne pourrait modifier les droits.'
                : undefined
            }
            className="size-4 rounded border-bordure text-marine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle disabled:cursor-not-allowed disabled:opacity-60"
          />
        )
      },
    })),
  ]

  return (
    <Card
      titre="Matrice des droits"
      description="Cochez les écrans ouverts à chaque rôle. Le menu et les accès suivent aussitôt."
      actions={
        peutModifier ? (
          <div className="flex items-center gap-2">
            {modifie && (
              <StatusPill ton="alerte" taille="sm" libelle="Modifications non enregistrées" />
            )}
            <Button
              variante="secondaire"
              taille="sm"
              icone={ArrowCounterClockwise}
              onClick={() => setCoches(accordesInitiaux)}
              disabled={!modifie || enCours}
            >
              Annuler
            </Button>
            <Button
              variante="primaire"
              taille="sm"
              icone={FloppyDisk}
              onClick={enregistrer}
              disabled={!modifie}
              enChargement={enCours}
            >
              Enregistrer
            </Button>
          </div>
        ) : (
          <StatusPill ton="neutre" taille="sm" libelle="Lecture seule" />
        )
      }
    >
      <Table
        intitule="Matrice des droits par écran et par rôle"
        colonnes={colonnes}
        lignes={ECRANS}
        cleLigne={(ecran) => ecran.id}
        parPage={ECRANS.length}
        messageVide="Aucun écran déclaré."
      />
    </Card>
  )
}
