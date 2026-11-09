/*
  Supervision des appareils enrôlés (EF-ADM-03) et révocation (EF-AUT-06, partie
  appareil). Charte § 9.2, écran 13.

  L'écran liste les appareils, leur propriétaire, leur plateforme, la version de
  l'application et la dernière synchronisation. La fraîcheur de synchronisation
  applique RG-Y7 (alerte au-delà de 24 h) : c'est cette même lecture qui répond
  à la « dernière synchronisation par appareil » laissée en attente à EF-DSH-04.

  La révocation (CL-1 `Appareil.revoquer()`) est une action irréversible côté
  métier : elle est confirmée par une modale au ton « danger », et SQ-5 (étape
  12) précise qu'elle entraîne côté serveur un blocage immédiat, une
  journalisation (EF-AUT-08) puis, à la prochaine synchronisation, l'effacement
  de la base locale chiffrée (ET-4). L'écran se contente d'émettre l'ordre et de
  recharger la liste.

  Comme pour la matrice des droits, la MODIFICATION (ici la révocation) est
  réservée au rôle système : un rôle à qui l'on ouvrirait l'écran en lecture
  (`peutModifier = false`) voit la liste sans pouvoir révoquer.
*/

import { useMemo, useState } from 'react'
import { DeviceMobile, ShieldSlash, WarningCircle } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, KpiCard, Modal, StatusPill, Table, useToast } from '@/components/ui'
import { listerAppareils, revoquerAppareil } from '@/features/admin/api/appareils'
import {
  fraicheurSynchro,
  LIBELLE_FRAICHEUR,
  LIBELLE_STATUT_APPAREIL,
  TON_FRAICHEUR,
  TON_STATUT_APPAREIL,
} from '@/features/admin/presentation/appareils-libelles'
import { formatDateHeure } from '@/lib/format'
import { useRequete } from '@/lib/hooks/useRequete'
import type { Appareil } from '@/features/admin/types/appareils'

export type SupervisionAppareilsProps = {
  /** Autorise la révocation. Réservé au rôle système, comme la matrice des droits. */
  peutModifier: boolean
}

export function SupervisionAppareils({ peutModifier }: SupervisionAppareilsProps) {
  const etat = useRequete(listerAppareils, [])
  const { afficherToast } = useToast()

  const [aRevoquer, setARevoquer] = useState<Appareil | null>(null)
  const [enCours, setEnCours] = useState(false)

  // Heure de référence figée pour un rendu : tous les calculs de fraîcheur
  // (RG-Y7) et l'affichage partagent le même instant.
  const maintenant = useMemo(() => new Date(), [etat.donnees])
  const appareils = useMemo(() => etat.donnees ?? [], [etat.donnees])

  const indicateurs = useMemo(() => {
    let actifs = 0
    let enRetard = 0
    let revoques = 0
    for (const appareil of appareils) {
      if (appareil.statut === 'revoque') {
        revoques += 1
        continue
      }
      if (appareil.statut === 'actif') {
        actifs += 1
      }
      if (fraicheurSynchro(appareil.derniereSynchronisation, maintenant) === 'en_retard') {
        enRetard += 1
      }
    }
    return { actifs, enRetard, revoques }
  }, [appareils, maintenant])

  async function confirmerRevocation() {
    if (!aRevoquer) {
      return
    }
    setEnCours(true)
    try {
      await revoquerAppareil(aRevoquer.id)
      afficherToast({
        ton: 'succes',
        titre: 'Appareil révoqué',
        message: "L'accès est bloqué immédiatement ; la base locale sera effacée à la prochaine connexion.",
      })
      setARevoquer(null)
      etat.recharger()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "L'appareil n'a pas pu être révoqué",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  const colonnes: ColonneTable<Appareil>[] = [
    {
      cle: 'empreinte',
      entete: 'Appareil',
      rendu: (appareil) => (
        <div className="min-w-0">
          <p className="truncate font-medium text-marine">{appareil.empreinteMateriel}</p>
          <p className="truncate text-xs text-texte-secondaire">
            {appareil.plateforme} · v{appareil.versionApplication}
          </p>
        </div>
      ),
      triable: true,
      valeurTri: (appareil) => appareil.empreinteMateriel,
    },
    {
      cle: 'proprietaire',
      entete: 'Propriétaire',
      rendu: (appareil) => (
        <div className="min-w-0">
          <p className="truncate text-sm text-texte">{appareil.nomUtilisateur}</p>
          <p className="truncate text-xs text-texte-secondaire">{appareil.identifiantUtilisateur}</p>
        </div>
      ),
      triable: true,
      valeurTri: (appareil) => appareil.nomUtilisateur,
    },
    {
      cle: 'synchro',
      entete: 'Dernière synchro',
      largeur: '13rem',
      rendu: (appareil) => {
        const fraicheur = fraicheurSynchro(appareil.derniereSynchronisation, maintenant)
        return (
          <div className="flex flex-col gap-1">
            <span className="text-sm text-texte">
              {formatDateHeure(appareil.derniereSynchronisation)}
            </span>
            <StatusPill
              taille="sm"
              ton={TON_FRAICHEUR[fraicheur]}
              libelle={LIBELLE_FRAICHEUR[fraicheur]}
            />
          </div>
        )
      },
      triable: true,
      // Trie du plus ancien au plus récent ; « jamais » (null) compte comme le plus ancien.
      valeurTri: (appareil) =>
        appareil.derniereSynchronisation
          ? new Date(appareil.derniereSynchronisation).getTime()
          : 0,
    },
    {
      cle: 'statut',
      entete: 'Statut',
      alignement: 'centre',
      largeur: '8rem',
      rendu: (appareil) => (
        <StatusPill
          ton={TON_STATUT_APPAREIL[appareil.statut]}
          libelle={LIBELLE_STATUT_APPAREIL[appareil.statut]}
        />
      ),
      triable: true,
      valeurTri: (appareil) => LIBELLE_STATUT_APPAREIL[appareil.statut],
    },
  ]

  if (peutModifier) {
    colonnes.push({
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '8rem',
      rendu: (appareil) =>
        appareil.statut === 'revoque' ? (
          <span className="text-xs text-texte-attenue">—</span>
        ) : (
          <Button
            variante="discret"
            taille="sm"
            icone={ShieldSlash}
            onClick={() => setARevoquer(appareil)}
          >
            Révoquer
          </Button>
        ),
    })
  }

  if (etat.statut === 'erreur') {
    return (
      <Card titre="Appareils indisponibles">
        <p className="text-sm text-danger">{etat.erreur}</p>
      </Card>
    )
  }

  return (
    <>
      <Card
        titre="Supervision des appareils"
        description="Appareils enrôlés, dernière synchronisation et révocation"
        actions={
          peutModifier ? undefined : (
            <StatusPill ton="neutre" taille="sm" libelle="Lecture seule" />
          )
        }
      >
        <div className="mb-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <KpiCard libelle="Appareils actifs" valeur={indicateurs.actifs} icone={DeviceMobile} accent="succes" />
          <KpiCard
            libelle="Synchro > 24 h"
            valeur={indicateurs.enRetard}
            icone={WarningCircle}
            accent={indicateurs.enRetard > 0 ? 'or' : 'sarcelle'}
          />
          <KpiCard libelle="Révoqués" valeur={indicateurs.revoques} icone={ShieldSlash} accent="danger" />
        </div>

        <Table
          intitule="Appareils enrôlés"
          colonnes={colonnes}
          lignes={appareils}
          cleLigne={(appareil) => appareil.id}
          chargement={etat.statut === 'chargement' || etat.statut === 'attente'}
          triInitial={{ cle: 'synchro', sens: 'asc' }}
          parPage={12}
          messageVide="Aucun appareil enrôlé."
        />

        <p className="mt-4 text-xs text-texte-secondaire">
          Un appareil est signalé « Plus de 24&nbsp;h » quand sa dernière synchronisation dépasse le
          seuil (RG-Y7). La révocation (EF-AUT-06) bloque l&apos;accès immédiatement et efface la base
          locale chiffrée à la prochaine connexion&nbsp;; elle est tracée au journal d&apos;audit.
        </p>
      </Card>

      <Modal
        ouvert={aRevoquer !== null}
        onFermer={() => (enCours ? undefined : setARevoquer(null))}
        titre="Révoquer cet appareil ?"
        description={
          aRevoquer
            ? `${aRevoquer.empreinteMateriel} — ${aRevoquer.nomUtilisateur}`
            : undefined
        }
        ton="danger"
        taille="sm"
        actions={
          <>
            <Button variante="secondaire" onClick={() => setARevoquer(null)} disabled={enCours}>
              Annuler
            </Button>
            <Button variante="danger" icone={ShieldSlash} onClick={confirmerRevocation} enChargement={enCours}>
              Révoquer
            </Button>
          </>
        }
      >
        <p className="text-sm text-texte">
          L&apos;appareil perdra l&apos;accès immédiatement. Sa base locale chiffrée sera effacée à sa
          prochaine tentative de connexion, et il devra être ré-enrôlé par une nouvelle connexion en
          ligne. Cette action est tracée au journal d&apos;audit.
        </p>
      </Modal>
    </>
  )
}
