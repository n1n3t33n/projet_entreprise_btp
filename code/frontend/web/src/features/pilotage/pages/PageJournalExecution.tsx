/*
  Écran /journal : journal d'exécution filtrable (EF-DSH-03).

  RG-A5 fixe la nature de cet écran : « Chaque changement de statut est un
  événement immuable : qui, quand (appareil et serveur), pour le compte de qui,
  statut avant et après, motif. On ne modifie ni ne supprime : on corrige par
  un nouvel événement. » L'écran est donc strictement en lecture, et il affiche
  les deux horodatages : l'écart entre la saisie sur l'appareil et la réception
  par le serveur est la trace du travail fait hors connexion, information que
  le pilotage doit pouvoir constater.

  Les filtres sont transmis au serveur, pas appliqués dans le navigateur : le
  journal grandit avec le chantier et ne doit pas être rapatrié en entier.
  Chaque changement de filtre relance donc la requête.
*/

import { useMemo, useState } from 'react'
import { ArrowRight, FunnelSimple, Repeat } from '@phosphor-icons/react'
import { Button, Card, FormField, Input, Select, StatusPill, Table } from '@/components/ui'
import type { ColonneTable } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import { chargerJournal, listerIntervenants } from '@/features/pilotage/api'
import { listerZones } from '@/features/avancement/api'
import { useCapacitesPilotage } from '@/features/pilotage/hooks/useCapacitesPilotage'
import { LIBELLE_STATUT_ETAPE, TON_STATUT_ETAPE } from '@/features/pilotage/presentation/libelles'
import {
  FILTRES_JOURNAL_VIDES,
  type EvenementJournal,
  type FiltresJournal,
  type StatutEtape,
} from '@/features/pilotage/types'
import { useRequete } from '@/lib/hooks/useRequete'
import { formatDateHeure } from '@/lib/format'

const STATUTS: StatutEtape[] = ['a_faire', 'en_cours', 'terminee_declaree', 'validee', 'bloquee']

/** Écart appareil / serveur en minutes, arrondi. Négatif impossible en pratique. */
function minutesDeDecalage(evenement: EvenementJournal): number {
  const appareil = new Date(evenement.horodatageAppareil).getTime()
  const serveur = new Date(evenement.horodatageServeur).getTime()
  if (!Number.isFinite(appareil) || !Number.isFinite(serveur)) return 0
  return Math.max(0, Math.round((serveur - appareil) / 60_000))
}

function libelleDecalage(minutes: number): string {
  if (minutes < 1) return 'Immédiat'
  if (minutes < 60) return `+${minutes} min`
  const heures = Math.floor(minutes / 60)
  const reste = minutes % 60
  return reste === 0 ? `+${heures} h` : `+${heures} h ${reste} min`
}

export function PageJournalExecution() {
  const capacites = useCapacitesPilotage()
  const [filtres, setFiltres] = useState<FiltresJournal>(FILTRES_JOURNAL_VIDES)

  const intervenantsEtat = useRequete(listerIntervenants, [])
  const zonesEtat = useRequete(listerZones, [])

  // Les filtres sont des dépendances de la requête : la liste se recharge dès
  // qu'un critère change, sans bouton « appliquer ».
  const journalEtat = useRequete(
    () => chargerJournal(filtres),
    [filtres.idAuteur, filtres.idZone, filtres.statutApres, filtres.depuis, filtres.jusqua],
  )

  const evenements = journalEtat.donnees ?? []
  const intervenants = intervenantsEtat.donnees ?? []
  const zones = zonesEtat.donnees ?? []

  const nombreFiltresActifs = useMemo(
    () => Object.values(filtres).filter((valeur) => valeur !== null).length,
    [filtres],
  )

  if (!capacites.peutVoirJournal) {
    return (
      <Card titre="Accès non autorisé">
        <p className="text-sm text-texte-secondaire">
          Ce rôle n'a pas accès au journal d'exécution du chantier.
        </p>
      </Card>
    )
  }

  const colonnes: ColonneTable<EvenementJournal>[] = [
    {
      cle: 'serveur',
      entete: 'Reçu par le serveur',
      triable: true,
      valeurTri: (ligne) => ligne.horodatageServeur,
      largeur: '13rem',
      rendu: (ligne) => (
        <div className="min-w-0">
          <p className="truncate text-texte">{formatDateHeure(ligne.horodatageServeur)}</p>
          <p className="truncate text-xs text-texte-secondaire">
            Saisi {formatDateHeure(ligne.horodatageAppareil)}
          </p>
        </div>
      ),
    },
    {
      cle: 'decalage',
      entete: 'Décalage',
      alignement: 'droite',
      triable: true,
      valeurTri: minutesDeDecalage,
      rendu: (ligne) => {
        const minutes = minutesDeDecalage(ligne)
        return (
          <span className={minutes >= 60 ? 'font-medium text-or' : 'text-texte-secondaire'}>
            {libelleDecalage(minutes)}
          </span>
        )
      },
    },
    {
      cle: 'ou',
      entete: 'Logement',
      triable: true,
      valeurTri: (ligne) => ligne.numeroLogement,
      rendu: (ligne) => (
        <div className="min-w-0">
          <p className="truncate font-medium text-texte">{ligne.numeroLogement}</p>
          <p className="truncate text-xs text-texte-secondaire">{ligne.libelleZone}</p>
        </div>
      ),
    },
    {
      cle: 'etape',
      entete: 'Étape',
      triable: true,
      valeurTri: (ligne) => ligne.libelleEtape,
      rendu: (ligne) => (
        <div className="min-w-0">
          <p className="truncate text-texte">{ligne.libelleEtape}</p>
          <p className="truncate text-xs text-texte-secondaire">{ligne.libelleCorpsEtat}</p>
        </div>
      ),
    },
    {
      cle: 'transition',
      entete: 'Changement de statut',
      largeur: '16rem',
      rendu: (ligne) => (
        <div className="flex flex-wrap items-center gap-1.5">
          {ligne.statutAvant ? (
            <StatusPill
              libelle={LIBELLE_STATUT_ETAPE[ligne.statutAvant]}
              ton={TON_STATUT_ETAPE[ligne.statutAvant]}
              taille="sm"
            />
          ) : (
            <StatusPill libelle="Création" ton="neutre" taille="sm" />
          )}
          <ArrowRight size={14} className="text-texte-secondaire" aria-hidden />
          <StatusPill
            libelle={LIBELLE_STATUT_ETAPE[ligne.statutApres]}
            ton={TON_STATUT_ETAPE[ligne.statutApres]}
            taille="sm"
          />
        </div>
      ),
    },
    {
      cle: 'auteur',
      entete: 'Auteur',
      triable: true,
      valeurTri: (ligne) => ligne.nomAuteur,
      rendu: (ligne) => (
        <div className="min-w-0">
          <p className="truncate text-texte">{ligne.nomAuteur}</p>
          {ligne.estDelegation && (
            <span className="inline-flex items-center gap-1 text-xs text-or">
              <Repeat size={12} aria-hidden />
              Pour le compte d'un tiers
            </span>
          )}
        </div>
      ),
    },
    {
      cle: 'motif',
      entete: 'Motif et commentaire',
      rendu: (ligne) => {
        if (!ligne.libelleMotifBlocage && !ligne.commentaire) {
          return <span className="text-texte-secondaire">—</span>
        }
        return (
          <div className="min-w-0">
            {ligne.libelleMotifBlocage && (
              <p className="truncate text-texte">{ligne.libelleMotifBlocage}</p>
            )}
            {ligne.commentaire && (
              <p className="truncate text-xs text-texte-secondaire">{ligne.commentaire}</p>
            )}
          </div>
        )
      },
    },
  ]

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Journal d'exécution"
        description="Historique immuable des changements de statut : aucune ligne ne peut être modifiée ni supprimée."
        niveauTitre={1}
        etiquette={
          <StatusPill
            libelle={`${evenements.length} événement${evenements.length > 1 ? 's' : ''}`}
            ton="neutre"
            taille="sm"
          />
        }
      />

      <Card
        titre="Filtres"
        icone={FunnelSimple}
        actions={
          nombreFiltresActifs > 0 ? (
            <Button
              variante="discret"
              taille="sm"
              onClick={() => setFiltres(FILTRES_JOURNAL_VIDES)}
            >
              Réinitialiser ({nombreFiltresActifs})
            </Button>
          ) : undefined
        }
      >
        <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-5">
          <FormField libelle="Intervenant">
            {(champ) => (
              <Select
                {...champ}
                value={filtres.idAuteur ?? ''}
                onChange={(evenement) =>
                  setFiltres((precedent) => ({
                    ...precedent,
                    idAuteur: evenement.target.value || null,
                  }))
                }
              >
                <option value="">Tous les intervenants</option>
                {intervenants.map((intervenant) => (
                  <option key={intervenant.idUtilisateur} value={intervenant.idUtilisateur}>
                    {intervenant.nom}
                  </option>
                ))}
              </Select>
            )}
          </FormField>

          <FormField libelle="Zone">
            {(champ) => (
              <Select
                {...champ}
                value={filtres.idZone ?? ''}
                onChange={(evenement) =>
                  setFiltres((precedent) => ({
                    ...precedent,
                    idZone: evenement.target.value || null,
                  }))
                }
              >
                <option value="">Toutes les zones</option>
                {zones.map((zone) => (
                  <option key={zone.idZone} value={zone.idZone}>
                    {zone.nom}
                  </option>
                ))}
              </Select>
            )}
          </FormField>

          <FormField libelle="Statut atteint">
            {(champ) => (
              <Select
                {...champ}
                value={filtres.statutApres ?? ''}
                onChange={(evenement) =>
                  setFiltres((precedent) => ({
                    ...precedent,
                    statutApres: (evenement.target.value || null) as StatutEtape | null,
                  }))
                }
              >
                <option value="">Tous les statuts</option>
                {STATUTS.map((statut) => (
                  <option key={statut} value={statut}>
                    {LIBELLE_STATUT_ETAPE[statut]}
                  </option>
                ))}
              </Select>
            )}
          </FormField>

          <FormField libelle="À partir du">
            {(champ) => (
              <Input
                {...champ}
                type="date"
                value={filtres.depuis ?? ''}
                onChange={(evenement) =>
                  setFiltres((precedent) => ({
                    ...precedent,
                    depuis: evenement.target.value || null,
                  }))
                }
              />
            )}
          </FormField>

          <FormField libelle="Jusqu'au">
            {(champ) => (
              <Input
                {...champ}
                type="date"
                value={filtres.jusqua ?? ''}
                onChange={(evenement) =>
                  setFiltres((precedent) => ({
                    ...precedent,
                    jusqua: evenement.target.value || null,
                  }))
                }
              />
            )}
          </FormField>
        </div>
      </Card>

      <Card sansRemplissage>
        {journalEtat.statut === 'erreur' ? (
          <p className="p-5 text-sm text-danger">{journalEtat.erreur}</p>
        ) : (
          <Table
            intitule="Journal d'exécution du chantier"
            colonnes={colonnes}
            lignes={evenements}
            cleLigne={(ligne) => ligne.uuid}
            triInitial={{ cle: 'serveur', sens: 'desc' }}
            chargement={journalEtat.statut === 'chargement'}
            messageVide="Aucun événement ne correspond à ces filtres."
            lectureSeule
            parPage={20}
          />
        )}
      </Card>
    </div>
  )
}
