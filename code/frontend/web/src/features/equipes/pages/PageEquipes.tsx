/*
  Écran /equipes : équipes, membres et affectation du travail (EF-REF-06).
  Charte § 9.2, écran 15.

  Deux onglets :
  - Équipes et membres — les équipes du chantier et leurs membres (MPD-1
    `equipe` / `membre_equipe` : code, libellé, chef d'équipe, dates). Lecture.
  - Affectation — affecter des étapes à un membre au moyen d'une fiche de route
    (MPD-5 `fiche_route` + `ligne_fiche_route`). C'est le seul rattachement du
    travail à une personne que le modèle permet : une fiche appartient à UN
    utilisateur. Réservé au responsable technique (tableau des profils).

  La gestion des équipes et des membres est présentée en lecture dans cet écran :
  la création et l'édition d'équipes et de membres (CRUD complet d'EF-REF-06) ne
  sont pas encore outillées côté API dans le périmètre de l'étape ; l'écran
  affiche l'état et prépare l'affectation, qui est la fonction attendue ici.
*/

import { useMemo, useState } from 'react'
import { UsersThree } from '@phosphor-icons/react'
import { Card, type ColonneTable, FilterPill, StatusPill, Table, Tabs } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import { listerEquipes, listerMembres } from '@/features/equipes/api'
import { useCapacitesEquipes } from '@/features/equipes/hooks/useCapacitesEquipes'
import { AffectationPanneau } from '@/features/equipes/pages/AffectationPanneau'
import { formatDate } from '@/lib/format'
import { useRequete } from '@/lib/hooks/useRequete'
import type { Equipe, MembreEquipe } from '@/features/equipes/types/domaine'

function MembresEquipe() {
  const equipesEtat = useRequete(listerEquipes, [])
  const equipes = useMemo(() => equipesEtat.donnees ?? [], [equipesEtat.donnees])
  const [idEquipe, setIdEquipe] = useState<string | null>(null)

  // Sélection par défaut : la première équipe dès que la liste arrive.
  const equipeActive = idEquipe ?? equipes[0]?.id ?? null

  const membresEtat = useRequete(
    () => (equipeActive ? listerMembres(equipeActive) : Promise.resolve<MembreEquipe[]>([])),
    [equipeActive],
  )
  const membres = useMemo(() => membresEtat.donnees ?? [], [membresEtat.donnees])

  const colonnes: ColonneTable<MembreEquipe>[] = [
    {
      cle: 'nom',
      entete: 'Membre',
      rendu: (membre) => (
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-marine">{membre.nom}</p>
          <p className="truncate text-xs text-texte-secondaire">{membre.fonction}</p>
        </div>
      ),
      triable: true,
      valeurTri: (membre) => membre.nom,
    },
    {
      cle: 'role',
      entete: "Rôle dans l'équipe",
      largeur: '11rem',
      rendu: (membre) =>
        membre.estChefEquipe ? (
          <StatusPill ton="information" taille="sm" libelle="Chef d'équipe" />
        ) : (
          <span className="text-sm text-texte-secondaire">Membre</span>
        ),
      triable: true,
      valeurTri: (membre) => (membre.estChefEquipe ? 0 : 1),
    },
    {
      cle: 'debut',
      entete: 'Depuis le',
      largeur: '8rem',
      rendu: (membre) => formatDate(membre.dateDebut),
      triable: true,
      valeurTri: (membre) => membre.dateDebut,
    },
    {
      cle: 'fin',
      entete: 'Jusqu\'au',
      largeur: '8rem',
      rendu: (membre) => formatDate(membre.dateFin),
    },
  ]

  if (equipesEtat.statut === 'erreur') {
    return (
      <Card titre="Équipes indisponibles">
        <p className="text-sm text-danger">{equipesEtat.erreur}</p>
      </Card>
    )
  }

  return (
    <Card
      titre="Équipes et membres"
      description="Équipes du chantier et composition (MPD-1 : équipe, membre d'équipe)"
    >
      <div className="mb-4 flex flex-wrap items-center gap-2">
        {equipes.map((equipe: Equipe) => (
          <FilterPill
            key={equipe.id}
            libelle={equipe.libelle}
            valeur={equipe.code}
            actif={equipe.id === equipeActive}
            onBasculer={() => setIdEquipe(equipe.id)}
          />
        ))}
      </div>

      <Table
        intitule="Membres de l'équipe sélectionnée"
        colonnes={colonnes}
        lignes={membres}
        cleLigne={(membre) => membre.idUtilisateur}
        chargement={membresEtat.statut === 'chargement' || membresEtat.statut === 'attente'}
        triInitial={{ cle: 'role', sens: 'asc' }}
        parPage={10}
        messageVide="Aucun membre dans cette équipe."
        lectureSeule
      />
    </Card>
  )
}

export function PageEquipes() {
  const capacites = useCapacitesEquipes()
  const [onglet, setOnglet] = useState('membres')

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Équipes et affectation"
        description="Composition des équipes et affectation des étapes par fiche de route"
        niveauTitre={2}
      />

      <Tabs
        intitule="Équipes"
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'membres', libelle: 'Équipes et membres', icone: UsersThree },
          { id: 'affectation', libelle: 'Affectation' },
        ]}
      >
        {onglet === 'membres' && <MembresEquipe />}
        {onglet === 'affectation' && <AffectationPanneau peutAffecter={capacites.peutAffecter} />}
      </Tabs>
    </div>
  )
}
