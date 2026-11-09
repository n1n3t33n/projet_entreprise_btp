/*
  Règles de validation — consultation et édition (EF-REF-08).

  Chaque règle est rendue sous forme lisible : « <événement> : <champ>
  <opérateur> <seuil> » et, le cas échéant, le délai associé.
*/

import { useMemo, useState } from 'react'
import { PencilSimple, Plus, ShieldCheck } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, KpiCard, StatusPill, Table } from '@/components/ui'
import { PageListe } from '@/components/templates'
import { listerRegles } from '@/features/parametrage/api'
import { FormulaireRegle } from '@/features/parametrage/pages/FormulaireRegle'
import { LIBELLE_EVENEMENT, SYMBOLE_OPERATEUR } from '@/features/parametrage/presentation/libelles'
import { useRequete } from '@/lib/hooks/useRequete'
import type { RegleValidation } from '@/features/parametrage/types'

export type ReglesValidationProps = {
  peutEditer: boolean
}

/** Expression lisible de la condition d'une règle. */
function conditionLisible(regle: RegleValidation): string {
  const parties: string[] = [regle.champTeste]
  if (regle.valeurSeuil !== null) {
    parties.push(SYMBOLE_OPERATEUR[regle.operateur], String(regle.valeurSeuil))
  }
  if (regle.delaiHeures !== null) {
    parties.push(`· délai ${regle.delaiHeures} h`)
  }
  return parties.join(' ')
}

export function ReglesValidation({ peutEditer }: ReglesValidationProps) {
  const reglesEtat = useRequete(listerRegles, [])
  const [ouvert, setOuvert] = useState(false)
  const [editee, setEditee] = useState<RegleValidation | null>(null)

  const regles = useMemo(() => reglesEtat.donnees ?? [], [reglesEtat.donnees])

  function ouvrirCreation() {
    setEditee(null)
    setOuvert(true)
  }

  function ouvrirModification(regle: RegleValidation) {
    setEditee(regle)
    setOuvert(true)
  }

  const colonnes: ColonneTable<RegleValidation>[] = [
    {
      cle: 'evenement',
      entete: 'Événement',
      triable: true,
      valeurTri: (regle) => LIBELLE_EVENEMENT[regle.typeEvenement],
      rendu: (regle) => (
        <StatusPill
          libelle={LIBELLE_EVENEMENT[regle.typeEvenement]}
          ton="information"
          taille="sm"
        />
      ),
    },
    {
      cle: 'condition',
      entete: 'Condition',
      rendu: (regle) => <span className="font-medium text-texte">{conditionLisible(regle)}</span>,
    },
  ]

  if (peutEditer) {
    colonnes.push({
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '7rem',
      rendu: (regle) => (
        <Button
          variante="discret"
          taille="sm"
          icone={PencilSimple}
          onClick={() => ouvrirModification(regle)}
        >
          Modifier
        </Button>
      ),
    })
  }

  if (reglesEtat.statut === 'erreur') {
    return (
      <Card>
        <p className="text-sm text-danger">{reglesEtat.erreur}</p>
      </Card>
    )
  }

  const chargement = reglesEtat.statut === 'chargement' || reglesEtat.statut === 'attente'

  return (
    <>
      <PageListe
        titre="Règles de validation"
        description="Conditions appliquées aux événements du chantier"
        lectureSeule={!peutEditer}
        actions={
          peutEditer ? (
            <Button variante="primaire" icone={Plus} onClick={ouvrirCreation}>
              Nouvelle règle
            </Button>
          ) : undefined
        }
        indicateurs={
          <KpiCard libelle="Règles" valeur={regles.length} icone={ShieldCheck} accent="marine" />
        }
      >
        <Table
          intitule="Règles de validation"
          colonnes={colonnes}
          lignes={regles}
          cleLigne={(regle) => regle.id}
          chargement={chargement}
          parPage={12}
          messageVide="Aucune règle de validation définie."
        />
      </PageListe>

      {peutEditer && (
        <FormulaireRegle
          ouvert={ouvert}
          onFermer={() => setOuvert(false)}
          regle={editee}
          onEnregistre={() => reglesEtat.recharger()}
        />
      )}
    </>
  )
}
