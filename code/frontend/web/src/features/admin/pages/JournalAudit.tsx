/*
  Journal d'audit des actions d'administration (EF-AUT-08). Charte § 9.2,
  écran 13 (onglet d'administration, distinct du journal d'exécution).

  Ce journal est en LECTURE SEULE par construction : il est immuable (MPD-1
  `trg_journal_audit_immuable`, RG-S8), les entrées sont écrites par le serveur
  au moment où il exécute une action (par exemple la révocation d'un appareil,
  SQ-5 étape 12), jamais par cet écran. On ne propose donc ni édition, ni
  suppression, ni création manuelle — seulement la consultation et le filtrage.

  Le filtrage (type d'action, auteur) est transmis au serveur en paramètres de
  requête, comme pour le journal d'exécution : le journal grandit avec l'usage
  et ne doit pas être rapatrié en entier pour être filtré côté navigateur.
*/

import { useMemo, useState } from 'react'
import { Card, type ColonneTable, FilterPill, StatusPill, Table } from '@/components/ui'
import { chargerAudit } from '@/features/admin/api/audit'
import { libelleAction, LIBELLE_ACTION_AUDIT, tonAction } from '@/features/admin/presentation/audit-libelles'
import { formatDateHeure } from '@/lib/format'
import { useRequete } from '@/lib/hooks/useRequete'
import type { EntreeAudit, FiltresAudit } from '@/features/admin/types/audit'
import { FILTRES_AUDIT_VIDES } from '@/features/admin/types/audit'

export function JournalAudit() {
  const [filtres, setFiltres] = useState<FiltresAudit>(FILTRES_AUDIT_VIDES)

  const etat = useRequete(() => chargerAudit(filtres), [filtres.action, filtres.idAuteur])
  const entrees = useMemo(() => etat.donnees ?? [], [etat.donnees])

  // Auteurs proposés au filtre : ceux présents dans le jeu renvoyé. On les
  // dérive des entrées plutôt que d'un appel séparé, le volume étant modeste.
  const auteurs = useMemo(() => {
    const index = new Map<string, string>()
    for (const entree of entrees) {
      index.set(entree.idAuteur, entree.nomAuteur)
    }
    return [...index.entries()].map(([id, nom]) => ({ id, nom }))
  }, [entrees])

  function changerAction(action: string | null) {
    setFiltres((precedent) => ({ ...precedent, action }))
  }

  function changerAuteur(idAuteur: string | null) {
    setFiltres((precedent) => ({ ...precedent, idAuteur }))
  }

  const colonnes: ColonneTable<EntreeAudit>[] = [
    {
      cle: 'horodatage',
      entete: 'Horodatage',
      largeur: '12rem',
      rendu: (entree) => (
        <span className="text-sm text-texte">{formatDateHeure(entree.horodatage)}</span>
      ),
      triable: true,
      valeurTri: (entree) => entree.horodatage,
    },
    {
      cle: 'action',
      entete: 'Action',
      largeur: '13rem',
      rendu: (entree) => (
        <StatusPill ton={tonAction(entree.action)} taille="sm" libelle={libelleAction(entree.action)} />
      ),
      triable: true,
      valeurTri: (entree) => libelleAction(entree.action),
    },
    {
      cle: 'resume',
      entete: 'Détail',
      rendu: (entree) => <span className="text-sm text-texte">{entree.resume}</span>,
    },
    {
      cle: 'auteur',
      entete: 'Auteur',
      largeur: '11rem',
      rendu: (entree) => (
        <div className="min-w-0">
          <p className="truncate text-sm text-texte">{entree.nomAuteur}</p>
          <p className="truncate text-xs text-texte-secondaire">{entree.identifiantAuteur}</p>
        </div>
      ),
      triable: true,
      valeurTri: (entree) => entree.nomAuteur,
    },
    {
      cle: 'ip',
      entete: 'Adresse IP',
      largeur: '9rem',
      rendu: (entree) => <span className="text-xs text-texte-secondaire">{entree.adresseIp}</span>,
    },
  ]

  if (etat.statut === 'erreur') {
    return (
      <Card titre="Journal d'audit indisponible">
        <p className="text-sm text-danger">{etat.erreur}</p>
      </Card>
    )
  }

  return (
    <Card
      titre="Journal d'audit"
      description="Actions d'administration : comptes, droits et appareils. Lecture seule, non modifiable."
    >
      <div className="mb-4 flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-texte-secondaire">
            Action
          </span>
          <FilterPill
            libelle="Toutes"
            actif={filtres.action === null}
            onBasculer={() => changerAction(null)}
          />
          {Object.entries(LIBELLE_ACTION_AUDIT).map(([code, libelle]) => (
            <FilterPill
              key={code}
              libelle={libelle}
              actif={filtres.action === code}
              onBasculer={() => changerAction(code)}
            />
          ))}
        </div>

        {auteurs.length > 1 && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-texte-secondaire">
              Auteur
            </span>
            <FilterPill
              libelle="Tous"
              actif={filtres.idAuteur === null}
              onBasculer={() => changerAuteur(null)}
            />
            {auteurs.map((auteur) => (
              <FilterPill
                key={auteur.id}
                libelle={auteur.nom}
                actif={filtres.idAuteur === auteur.id}
                onBasculer={() => changerAuteur(auteur.id)}
              />
            ))}
          </div>
        )}
      </div>

      <Table
        intitule="Journal d'audit des actions d'administration"
        colonnes={colonnes}
        lignes={entrees}
        cleLigne={(entree) => entree.id}
        chargement={etat.statut === 'chargement' || etat.statut === 'attente'}
        triInitial={{ cle: 'horodatage', sens: 'desc' }}
        parPage={15}
        messageVide="Aucune action enregistrée pour ce filtre."
        lectureSeule
      />

      <p className="mt-4 text-xs text-texte-secondaire">
        Le journal d&apos;audit est immuable&nbsp;: une entrée n&apos;est jamais modifiée ni
        supprimée (RG-S8). Il est distinct du journal d&apos;exécution, qui trace les changements de
        statut des étapes de travaux.
      </p>
    </Card>
  )
}
