/*
  Paramètres du chantier — consultation et édition (EF-REF-07).
*/

import { useMemo, useState } from 'react'
import { PencilSimple, Plus, SlidersHorizontal } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, KpiCard, StatusPill, Table } from '@/components/ui'
import { PageListe } from '@/components/templates'
import { listerParametres } from '@/features/parametrage/api'
import { FormulaireParametre } from '@/features/parametrage/pages/FormulaireParametre'
import { LIBELLE_TYPE_VALEUR } from '@/features/parametrage/presentation/libelles'
import { useRequete } from '@/lib/hooks/useRequete'
import type { ParametreChantier } from '@/features/parametrage/types'
import { tr } from '@/i18n/tr'

export type ParametresChantierProps = {
  peutEditer: boolean
}

/** Rend la valeur selon son type (un booléen en Oui/Non lisible). */
function valeurAffichee(parametre: ParametreChantier): string {
  if (parametre.typeValeur === 'booleen') {
    return parametre.valeur === 'true' ? tr('Oui') : tr('Non')
  }
  return parametre.valeur
}

export function ParametresChantier({ peutEditer }: ParametresChantierProps) {
  const parametresEtat = useRequete(listerParametres, [])
  const [ouvert, setOuvert] = useState(false)
  const [edite, setEdite] = useState<ParametreChantier | null>(null)

  const parametres = useMemo(() => parametresEtat.donnees ?? [], [parametresEtat.donnees])

  function ouvrirCreation() {
    setEdite(null)
    setOuvert(true)
  }

  function ouvrirModification(parametre: ParametreChantier) {
    setEdite(parametre)
    setOuvert(true)
  }

  const colonnes: ColonneTable<ParametreChantier>[] = [
    {
      cle: 'cle',
      entete: tr('Clé'),
      triable: true,
      valeurTri: (parametre) => parametre.cle,
      rendu: (parametre) => (
        <div className="min-w-0">
          <p className="truncate font-medium text-marine">{parametre.cle}</p>
          {parametre.libelle && (
            <p className="truncate text-xs text-texte-secondaire">{parametre.libelle}</p>
          )}
        </div>
      ),
    },
    {
      cle: 'valeur',
      entete: tr('Valeur'),
      alignement: 'droite',
      triable: true,
      valeurTri: (parametre) => parametre.valeur,
      rendu: (parametre) => (
        <span className="font-medium text-texte">{valeurAffichee(parametre)}</span>
      ),
    },
    {
      cle: 'type',
      entete: tr('Type'),
      alignement: 'centre',
      largeur: '8rem',
      rendu: (parametre) => (
        <StatusPill libelle={LIBELLE_TYPE_VALEUR[parametre.typeValeur]} ton="neutre" taille="sm" />
      ),
    },
  ]

  if (peutEditer) {
    colonnes.push({
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '7rem',
      rendu: (parametre) => (
        <Button
          variante="discret"
          taille="sm"
          icone={PencilSimple}
          onClick={() => ouvrirModification(parametre)}
        >
          {tr('Modifier')}
        </Button>
      ),
    })
  }

  if (parametresEtat.statut === 'erreur') {
    return (
      <Card>
        <p className="text-sm text-danger">{parametresEtat.erreur}</p>
      </Card>
    )
  }

  const chargement = parametresEtat.statut === 'chargement' || parametresEtat.statut === 'attente'

  return (
    <>
      <PageListe
        titre={tr('Paramètres du chantier')}
        description={tr('Réglages typés, lus par les règles métier du poste de pilotage')}
        lectureSeule={!peutEditer}
        actions={
          peutEditer ? (
            <Button variante="primaire" icone={Plus} onClick={ouvrirCreation}>
              {tr('Nouveau paramètre')}
            </Button>
          ) : undefined
        }
        indicateurs={
          <KpiCard
            libelle={tr('Paramètres')}
            valeur={parametres.length}
            icone={SlidersHorizontal}
            accent="marine"
          />
        }
      >
        <Table
          intitule={tr('Paramètres du chantier')}
          colonnes={colonnes}
          lignes={parametres}
          cleLigne={(parametre) => parametre.id}
          chargement={chargement}
          triInitial={{ cle: 'cle', sens: 'asc' }}
          parPage={12}
          messageVide={tr('Aucun paramètre défini.')}
        />
      </PageListe>

      {peutEditer && (
        <FormulaireParametre
          ouvert={ouvert}
          onFermer={() => setOuvert(false)}
          parametre={edite}
          onEnregistre={() => parametresEtat.recharger()}
        />
      )}
    </>
  )
}
