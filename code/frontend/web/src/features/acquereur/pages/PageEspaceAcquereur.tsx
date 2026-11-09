/*
  Espace acquéreur (UC-5, EF-ACQ-01/02). Charte § 9.2, phase 2, LECTURE SEULE.

  L'acquéreur voit l'avancement de SON logement (EF-ACQ-01) et les étapes
  franchies qui lui ont été notifiées (EF-ACQ-02). Rien n'est modifiable : le
  rôle consulte sans jamais saisir. La vue est simplifiée (UC-5 : « avancement
  simplifié d'un logement ») — pas de charge de contrôle, pas de détail
  d'exécution, pas de motif de blocage interne.

  Le logement affiché est celui du compte connecté : son périmètre le détermine
  (EF-AUT-02). L'écran ne propose donc aucun choix de logement.
*/

import { useMemo } from 'react'
import { BellRinging, HouseLine } from '@phosphor-icons/react'
import { Card, type ColonneTable, JaugeProgression, StatusPill, Table } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import {
  chargerAvancementLogement,
  chargerNotificationsAcquereur,
} from '@/features/acquereur/api'
import { LIBELLE_STATUT_ETAPE, TON_STATUT_ETAPE } from '@/features/avancement/presentation/libelles'
import { formatDate } from '@/lib/format'
import { useRequete } from '@/lib/hooks/useRequete'
import type { EtapeAcquereur } from '@/features/acquereur/types/domaine'

export function PageEspaceAcquereur() {
  const logementEtat = useRequete(chargerAvancementLogement, [])
  const notificationsEtat = useRequete(chargerNotificationsAcquereur, [])

  const logement = logementEtat.donnees
  const notifications = useMemo(
    () => notificationsEtat.donnees ?? [],
    [notificationsEtat.donnees],
  )

  const colonnes: ColonneTable<EtapeAcquereur>[] = [
    {
      cle: 'etape',
      entete: 'Étape',
      rendu: (etape) => (
        <div className="flex items-center gap-2">
          <span
            className="h-2.5 w-2.5 shrink-0 rounded-full"
            style={{ backgroundColor: etape.couleurCorpsEtat }}
            aria-hidden
          />
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-marine">{etape.libelleEtape}</p>
            <p className="truncate text-xs text-texte-secondaire">{etape.libelleCorpsEtat}</p>
          </div>
        </div>
      ),
    },
    {
      cle: 'statut',
      entete: 'État',
      alignement: 'centre',
      largeur: '11rem',
      rendu: (etape) => (
        <StatusPill ton={TON_STATUT_ETAPE[etape.statut]} libelle={LIBELLE_STATUT_ETAPE[etape.statut]} />
      ),
    },
    {
      cle: 'franchissement',
      entete: 'Franchie le',
      largeur: '9rem',
      rendu: (etape) => formatDate(etape.dateFranchissement),
    },
  ]

  if (logementEtat.statut === 'erreur') {
    return (
      <div className="flex min-w-0 flex-col gap-6">
        <EnTetePage titre="Mon logement" niveauTitre={2} />
        <Card titre="Avancement indisponible">
          <p className="text-sm text-danger">{logementEtat.erreur}</p>
        </Card>
      </div>
    )
  }

  const chargement = logementEtat.statut === 'chargement' || logementEtat.statut === 'attente'

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Mon logement"
        description="Suivez l'avancement de votre logement"
        niveauTitre={2}
        etiquette={
          logement ? (
            <StatusPill
              ton="information"
              taille="sm"
              icone={HouseLine}
              libelle={`${logement.numeroLogement} · ${logement.libelleTypeLogement}`}
            />
          ) : undefined
        }
      />

      <Card
        titre="Avancement global"
        description={
          logement?.dateLivraisonPrevue
            ? `Livraison prévue : ${formatDate(logement.dateLivraisonPrevue)}`
            : undefined
        }
      >
        {chargement || !logement ? (
          <div className="h-6 w-full animate-pulse rounded-full bg-fond-alt" />
        ) : (
          <JaugeProgression
            valeur={logement.pourcentageValide}
            valeurSecondaire={logement.pourcentageDeclare}
            libelleValeur="Validé"
            libelleValeurSecondaire="Annoncé"
          />
        )}
      </Card>

      <Card titre="Les étapes de votre logement" sansRemplissage>
        <div className="px-5 py-5">
          <Table
            intitule="Étapes du logement"
            colonnes={colonnes}
            lignes={logement?.etapes ?? []}
            cleLigne={(etape) => etape.idEtape}
            chargement={chargement}
            messageVide="Aucune étape à afficher pour le moment."
            lectureSeule
          />
        </div>
      </Card>

      <Card
        titre="Étapes franchies"
        description="Les jalons de votre logement, au fur et à mesure (EF-ACQ-02)"
        icone={BellRinging}
      >
        {notifications.length === 0 ? (
          <p className="text-sm text-texte-secondaire">
            Vous serez informé ici à chaque étape franchie de votre logement.
          </p>
        ) : (
          <ul className="flex flex-col gap-3">
            {notifications.map((notification) => (
              <li
                key={notification.id}
                className="flex items-center justify-between gap-3 rounded-controle border border-bordure px-4 py-3"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-texte">
                    {notification.libelleEtape}
                  </p>
                  <p className="text-xs text-texte-secondaire">
                    Franchie le {formatDate(notification.dateFranchissement)}
                  </p>
                </div>
                {!notification.lue && <StatusPill ton="information" taille="sm" libelle="Nouveau" />}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}
