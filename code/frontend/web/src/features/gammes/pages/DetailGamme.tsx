/*
  Détail d'une gamme (EF-REF-05, EF-REF-09).

  Tiroir de lecture d'une version de gamme : ses attributs, ses étapes et leur
  poids. Les actions proposées dépendent du statut, conformément au cycle de vie
  (brouillon → active → archivée) :
  - brouillon : modifier les étapes, publier la version ;
  - active : créer une nouvelle version (brouillon), archiver ;
  - archivée : créer une nouvelle version à partir d'elle.

  Toutes les transitions sont appliquées par le serveur. Le tiroir recharge le
  détail après chaque action et prévient le parent, qui recharge la liste.
*/

import { useState } from 'react'
import { Archive, CheckCircle, CopySimple, PencilSimple, SealCheck } from '@phosphor-icons/react'
import { Button, type ColonneTable, Drawer, StatusPill, Table, useToast } from '@/components/ui'
import { archiverGamme, chargerGamme, creerVersion, publierGamme } from '@/features/gammes/api'
import { EditeurEtapes } from '@/features/gammes/pages/EditeurEtapes'
import { LIBELLE_STATUT_GAMME, TON_STATUT_GAMME } from '@/features/gammes/presentation/libelles'
import { useRequete } from '@/lib/hooks/useRequete'
import { formatDate, formatPourcentage } from '@/lib/format'
import type { CorpsEtat, EtapeModele } from '@/features/gammes/types'

export type DetailGammeProps = {
  ouvert: boolean
  onFermer: () => void
  idGamme: string | null
  peutEditer: boolean
  corpsEtat: CorpsEtat[]
  /** Appelé après toute action modifiant la gamme, pour recharger la liste. */
  onAction: () => void
}

export function DetailGamme({
  ouvert,
  onFermer,
  idGamme,
  peutEditer,
  corpsEtat,
  onAction,
}: DetailGammeProps) {
  const { afficherToast } = useToast()
  const detail = useRequete(
    () => (idGamme ? chargerGamme(idGamme) : Promise.resolve(null)),
    [idGamme, ouvert],
  )
  const [editeurOuvert, setEditeurOuvert] = useState(false)
  const [enCours, setEnCours] = useState(false)

  const gamme = detail.donnees?.gamme ?? null
  const etapes = detail.donnees?.etapes ?? []

  async function executer(action: () => Promise<unknown>, succes: string, fermerApres: boolean) {
    setEnCours(true)
    try {
      await action()
      afficherToast({ ton: 'succes', titre: succes })
      onAction()
      if (fermerApres) onFermer()
      else detail.recharger()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "L'action n'a pas pu aboutir",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  const colonnes: ColonneTable<EtapeModele>[] = [
    {
      cle: 'ordre',
      entete: 'N°',
      largeur: '4rem',
      alignement: 'centre',
      rendu: (etape) => <span className="text-texte-secondaire">{etape.ordre}</span>,
    },
    {
      cle: 'libelle',
      entete: 'Étape',
      rendu: (etape) => (
        <div className="flex items-center gap-2">
          <span
            className="h-2.5 w-2.5 shrink-0 rounded-full"
            style={{ backgroundColor: etape.couleurCorpsEtat }}
            aria-hidden
          />
          <div className="min-w-0">
            <p className="truncate text-texte">{etape.libelle}</p>
            <p className="truncate text-xs text-texte-secondaire">{etape.libelleCorpsEtat}</p>
          </div>
        </div>
      ),
    },
    {
      cle: 'poids',
      entete: 'Poids',
      alignement: 'droite',
      largeur: '6rem',
      rendu: (etape) => formatPourcentage(etape.poids),
    },
    {
      cle: 'controle',
      entete: 'Contrôle',
      alignement: 'centre',
      largeur: '7rem',
      rendu: (etape) =>
        etape.controleRequis ? (
          <CheckCircle size={18} weight="fill" className="mx-auto text-succes" aria-label="Oui" />
        ) : (
          <span className="text-texte-secondaire">—</span>
        ),
    },
  ]

  const pied = gamme && peutEditer ? actionsPied() : undefined

  function actionsPied() {
    if (!gamme) return undefined
    if (gamme.statut === 'brouillon') {
      return (
        <div className="flex items-center justify-end gap-2">
          <Button
            variante="secondaire"
            icone={PencilSimple}
            onClick={() => setEditeurOuvert(true)}
            disabled={enCours}
          >
            Modifier les étapes
          </Button>
          <Button
            variante="primaire"
            icone={SealCheck}
            enChargement={enCours}
            onClick={() => executer(() => publierGamme(gamme.id), 'Version publiée', true)}
          >
            Publier la version
          </Button>
        </div>
      )
    }
    if (gamme.statut === 'active') {
      return (
        <div className="flex items-center justify-end gap-2">
          <Button
            variante="secondaire"
            icone={Archive}
            disabled={enCours}
            onClick={() => executer(() => archiverGamme(gamme.id), 'Gamme archivée', true)}
          >
            Archiver
          </Button>
          <Button
            variante="primaire"
            icone={CopySimple}
            enChargement={enCours}
            onClick={() => executer(() => creerVersion(gamme.id), 'Nouvelle version créée', true)}
          >
            Créer une nouvelle version
          </Button>
        </div>
      )
    }
    return (
      <div className="flex items-center justify-end">
        <Button
          variante="secondaire"
          icone={CopySimple}
          enChargement={enCours}
          onClick={() => executer(() => creerVersion(gamme.id), 'Nouvelle version créée', true)}
        >
          Créer une nouvelle version
        </Button>
      </div>
    )
  }

  return (
    <>
      <Drawer
        ouvert={ouvert}
        onFermer={onFermer}
        titre={gamme ? gamme.libelle : 'Gamme'}
        description={gamme ? `${gamme.libelleTypeLogement} · version ${gamme.version}` : undefined}
        largeur="lg"
        pied={pied}
      >
        {detail.statut === 'erreur' ? (
          <p className="text-sm text-danger">{detail.erreur}</p>
        ) : gamme ? (
          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <StatusPill
                libelle={LIBELLE_STATUT_GAMME[gamme.statut]}
                ton={TON_STATUT_GAMME[gamme.statut]}
              />
              <span className="text-sm text-texte-secondaire">
                {gamme.nombreEtapes} étape{gamme.nombreEtapes > 1 ? 's' : ''} · poids total{' '}
                <span className="font-semibold text-texte">
                  {formatPourcentage(gamme.poidsTotal)}
                </span>
              </span>
              {gamme.dateActivation && (
                <span className="text-sm text-texte-secondaire">
                  Activée le {formatDate(gamme.dateActivation)}
                </span>
              )}
            </div>

            {gamme.statut === 'active' && (
              <div className="rounded-lg border border-marine/20 bg-marine/5 p-3">
                <p className="text-sm text-texte-secondaire">
                  Cette version est en service : ses étapes sont figées. Pour la faire évoluer,
                  créez une nouvelle version, modifiez ses étapes, puis publiez-la.
                </p>
              </div>
            )}

            <Table
              intitule={`Étapes de ${gamme.libelle}`}
              colonnes={colonnes}
              lignes={etapes}
              cleLigne={(etape) => etape.id}
              messageVide="Aucune étape. Ajoutez-en avant de publier."
              lectureSeule
            />
          </div>
        ) : (
          <p className="text-sm text-texte-secondaire">Chargement…</p>
        )}
      </Drawer>

      {gamme && (
        <EditeurEtapes
          ouvert={editeurOuvert}
          onFermer={() => setEditeurOuvert(false)}
          idGamme={gamme.id}
          libelleGamme={gamme.libelle}
          etapesInitiales={etapes}
          corpsEtat={corpsEtat}
          onEnregistre={() => {
            detail.recharger()
            onAction()
          }}
        />
      )}
    </>
  )
}
