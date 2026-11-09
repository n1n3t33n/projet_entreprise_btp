/*
  Comptes utilisateurs (EF-AUT-01, EF-AUT-02).

  Liste des comptes nominatifs avec leur rôle, leur périmètre et leur statut.
  La désactivation se fait par le formulaire : un compte n'est jamais supprimé,
  conformément à la traçabilité attendue (un compte désactivé reste l'auteur
  des opérations qu'il a enregistrées).
*/

import { useMemo, useState } from 'react'
import { PencilSimple, Plus, UserCircle, UsersThree } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, KpiCard, StatusPill, Table } from '@/components/ui'
import { libelleRole } from '@/app/role-context'
import { useSession } from '@/app/session-context'
import { listerComptes, listerPerimetres } from '@/features/auth/api'
import { FormulaireCompte } from '@/features/admin/pages/FormulaireCompte'
import { formatDate } from '@/lib/format'
import { useRequete } from '@/lib/hooks/useRequete'
import type { Utilisateur } from '@/features/auth/types/domaine'

export type ComptesUtilisateursProps = {
  peutModifier: boolean
}

export function ComptesUtilisateurs({ peutModifier }: ComptesUtilisateursProps) {
  const comptesEtat = useRequete(listerComptes, [])
  const perimetresEtat = useRequete(listerPerimetres, [])
  const { session } = useSession()

  const [modaleOuverte, setModaleOuverte] = useState(false)
  const [compteEdite, setCompteEdite] = useState<Utilisateur | null>(null)

  const comptes = useMemo(() => comptesEtat.donnees ?? [], [comptesEtat.donnees])
  const perimetres = useMemo(() => perimetresEtat.donnees ?? [], [perimetresEtat.donnees])

  const indicateurs = useMemo(() => {
    const actifs = comptes.filter((compte) => compte.statut === 'actif').length
    return { total: comptes.length, actifs }
  }, [comptes])

  const colonnes: ColonneTable<Utilisateur>[] = [
    {
      cle: 'identifiant',
      entete: 'Identifiant',
      largeur: '11rem',
      rendu: (compte) => <span className="font-medium text-marine">{compte.identifiant}</span>,
      triable: true,
      valeurTri: (compte) => compte.identifiant,
    },
    {
      cle: 'nom',
      entete: 'Nom',
      rendu: (compte) => (
        <div className="min-w-0">
          <p className="truncate text-sm text-texte">
            {compte.prenom} {compte.nom}
            {session?.utilisateur.id === compte.id && (
              <span className="ml-2 text-xs text-texte-secondaire">(vous)</span>
            )}
          </p>
          <p className="truncate text-xs text-texte-secondaire">{compte.fonction}</p>
        </div>
      ),
      triable: true,
      valeurTri: (compte) => `${compte.nom} ${compte.prenom}`,
    },
    {
      cle: 'role',
      entete: 'Rôle',
      largeur: '12rem',
      rendu: (compte) => libelleRole(compte.role),
      triable: true,
      valeurTri: (compte) => libelleRole(compte.role),
    },
    {
      cle: 'perimetre',
      entete: 'Périmètre',
      rendu: (compte) => compte.libellePerimetre,
      triable: true,
      valeurTri: (compte) => compte.libellePerimetre,
    },
    {
      cle: 'creation',
      entete: 'Créé le',
      largeur: '8rem',
      rendu: (compte) => formatDate(compte.dateCreation),
      triable: true,
      valeurTri: (compte) => compte.dateCreation,
    },
    {
      cle: 'statut',
      entete: 'Statut',
      alignement: 'centre',
      largeur: '7rem',
      rendu: (compte) => (
        <StatusPill
          ton={compte.statut === 'actif' ? 'succes' : 'neutre'}
          libelle={compte.statut === 'actif' ? 'Actif' : 'Désactivé'}
        />
      ),
      triable: true,
      valeurTri: (compte) => (compte.statut === 'actif' ? 1 : 0),
    },
  ]

  if (peutModifier) {
    colonnes.push({
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '7rem',
      rendu: (compte) => (
        <Button
          variante="discret"
          taille="sm"
          icone={PencilSimple}
          onClick={() => {
            setCompteEdite(compte)
            setModaleOuverte(true)
          }}
        >
          Modifier
        </Button>
      ),
    })
  }

  if (comptesEtat.statut === 'erreur') {
    return (
      <Card titre="Comptes indisponibles">
        <p className="text-sm text-danger">{comptesEtat.erreur}</p>
      </Card>
    )
  }

  return (
    <>
      <Card
        titre="Comptes utilisateurs"
        description="Comptes nominatifs, rôle affecté et périmètre d'exercice"
        actions={
          peutModifier ? (
            <Button
              variante="primaire"
              taille="sm"
              icone={Plus}
              onClick={() => {
                setCompteEdite(null)
                setModaleOuverte(true)
              }}
            >
              Nouveau compte
            </Button>
          ) : (
            <StatusPill ton="neutre" taille="sm" libelle="Lecture seule" />
          )
        }
      >
        <div className="mb-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <KpiCard
            libelle="Comptes"
            valeur={indicateurs.total}
            icone={UsersThree}
            accent="marine"
          />
          <KpiCard
            libelle="Actifs"
            valeur={indicateurs.actifs}
            icone={UserCircle}
            accent="succes"
          />
        </div>

        <Table
          intitule="Comptes du poste de pilotage"
          colonnes={colonnes}
          lignes={comptes}
          cleLigne={(compte) => compte.id}
          chargement={comptesEtat.statut === 'chargement' || comptesEtat.statut === 'attente'}
          triInitial={{ cle: 'identifiant', sens: 'asc' }}
          parPage={12}
          messageVide="Aucun compte enregistré."
        />

        <p className="mt-4 text-xs text-texte-secondaire">
          Le mot de passe ne se définit pas ici : sa réinitialisation fait l&apos;objet d&apos;une
          action dédiée (EF-AUT-09), pour qu&apos;un administrateur ne choisisse jamais le secret
          d&apos;un autre utilisateur. La révocation d&apos;un appareil (EF-AUT-06) relève de
          l&apos;écran de supervision des appareils.
        </p>
      </Card>

      {peutModifier && (
        <FormulaireCompte
          ouvert={modaleOuverte}
          onFermer={() => setModaleOuverte(false)}
          compte={compteEdite}
          perimetres={perimetres}
          onEnregistre={() => comptesEtat.recharger()}
        />
      )}
    </>
  )
}
