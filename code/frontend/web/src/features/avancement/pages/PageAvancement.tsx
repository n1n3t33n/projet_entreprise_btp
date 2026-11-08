/*
  Écran /avancement du poste de pilotage : point d'entrée du module.

  Orchestre les trois écrans de l'étape : le suivi de l'avancement par logement,
  le détail et la validation d'une étape (en tiroir), et la déclaration de
  blocage (en ligne dans le détail). Porte l'état partagé — données chargées,
  filtre, onglet, logement ouvert — et applique le filtrage par rôle.
*/

import { useState } from 'react'
import { Buildings, ClipboardText, Clock, Prohibit } from '@phosphor-icons/react'
import { Card, KpiCard, Tabs } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import {
  listerEtapesAValider,
  listerLogements,
  listerMotifsBlocage,
  listerZones,
  obtenirSynthese,
} from '@/features/avancement/api'
import { BarreAvancement } from '@/features/avancement/components/BarreAvancement'
import { useCapacitesAvancement } from '@/features/avancement/hooks/useCapacitesAvancement'
import { useRequete } from '@/features/avancement/hooks/useRequete'
import { EtapesAValider } from '@/features/avancement/pages/EtapesAValider'
import {
  FicheLogementTiroir,
  type CibleLogement,
} from '@/features/avancement/pages/FicheLogementTiroir'
import { SuiviLogements } from '@/features/avancement/pages/SuiviLogements'
import type { FiltreAvancement } from '@/features/avancement/types'

const FILTRE_INITIAL: FiltreAvancement = { recherche: '', idZone: 'toutes' }

export function PageAvancement() {
  const capacites = useCapacitesAvancement()

  const [onglet, setOnglet] = useState('suivi')
  const [filtre, setFiltre] = useState<FiltreAvancement>(FILTRE_INITIAL)
  const [cible, setCible] = useState<CibleLogement | null>(null)

  const syntheseEtat = useRequete(obtenirSynthese, [])
  const zonesEtat = useRequete(listerZones, [])
  const logementsEtat = useRequete(listerLogements, [])
  const aValiderEtat = useRequete(listerEtapesAValider, [])
  const motifsEtat = useRequete(listerMotifsBlocage, [])

  const synthese = syntheseEtat.donnees
  const logements = logementsEtat.donnees ?? []
  const zones = zonesEtat.donnees ?? []
  const aValider = aValiderEtat.donnees ?? []
  const motifs = motifsEtat.donnees ?? []

  function rafraichir() {
    syntheseEtat.recharger()
    logementsEtat.recharger()
    aValiderEtat.recharger()
  }

  if (!capacites.peutConsulter) {
    return (
      <Card titre="Accès non autorisé">
        <p className="text-sm text-texte-secondaire">
          Ce rôle n'a pas accès au suivi de l'avancement.
        </p>
      </Card>
    )
  }

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Avancement des travaux"
        description="Chantier de Grand-Bassam — poste de pilotage"
        niveauTitre={1}
      />

      <Card titre="Avancement du chantier">
        <BarreAvancement
          pourcentageDeclare={synthese?.pourcentageDeclare ?? 0}
          pourcentageValide={synthese?.pourcentageValide ?? 0}
        />
      </Card>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard
          libelle="Logements"
          valeur={synthese?.nombreLogements ?? '—'}
          icone={Buildings}
          accent="marine"
        />
        <KpiCard
          libelle="À valider"
          valeur={synthese?.nombreEtapesAValider ?? '—'}
          icone={ClipboardText}
          accent="or"
        />
        <KpiCard
          libelle="Étapes bloquées"
          valeur={synthese?.nombreEtapesBloquees ?? '—'}
          icone={Prohibit}
          accent="danger"
        />
        <KpiCard
          libelle="Étapes en retard"
          valeur={synthese?.nombreEtapesEnRetard ?? '—'}
          icone={Clock}
          accent="or"
        />
      </div>

      <Tabs
        intitule="Vues de l'avancement"
        actif={onglet}
        onChanger={setOnglet}
        onglets={[
          { id: 'suivi', libelle: 'Suivi par logement', icone: Buildings },
          {
            id: 'a-valider',
            libelle:
              aValider.length > 0 ? `À valider (${aValider.length})` : 'À valider',
            icone: ClipboardText,
          },
        ]}
      >
        {onglet === 'suivi' ? (
          logementsEtat.statut === 'erreur' ? (
            <Card>
              <p className="text-sm text-danger">{logementsEtat.erreur}</p>
            </Card>
          ) : (
            <SuiviLogements
              lignes={logements}
              chargement={logementsEtat.statut === 'chargement'}
              zones={zones}
              filtre={filtre}
              onFiltre={setFiltre}
              onVoirLogement={(ligne) =>
                setCible({ idLogement: ligne.idLogement, numero: ligne.numero, idEtapeInitiale: null })
              }
            />
          )
        ) : (
          <EtapesAValider
            etapes={aValider}
            chargement={aValiderEtat.statut === 'chargement'}
            onExaminer={(etape) =>
              setCible({
                idLogement: etape.idLogement,
                numero: etape.numeroLogement,
                idEtapeInitiale: etape.idEtape,
              })
            }
          />
        )}
      </Tabs>

      <FicheLogementTiroir
        cible={cible}
        capacites={capacites}
        motifs={motifs}
        onFermer={() => setCible(null)}
        onChangement={rafraichir}
      />
    </div>
  )
}
