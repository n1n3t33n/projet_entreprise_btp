/*
  Écran /tableau-de-bord : vue de pilotage, en lecture seule.

  Couvre quatre exigences :
  - EF-DSH-01 : avancement global par chantier, zone et logement, en
    pourcentage pondéré déclaré et validé (RG-A6).
  - EF-DSH-02 : détail du même avancement par corps d'état.
  - EF-DSH-04 : vue du stock — niveaux, alertes, mouvements récents (RG-S5).
  - EF-DSH-05 : retards et blocages (RG-A8).

  Aucune action n'est proposée ici, par construction : le tableau de bord
  observe. Une correction se fait dans l'écran d'avancement, qui crée un
  nouvel événement, conformément à RG-A5.

  Chaque section n'est demandée au serveur que si le rôle y a droit : les
  crochets de chargement sont conditionnés par les capacités du rôle, de sorte
  qu'un commercial ne provoque aucun appel vers les données de stock.

  LIMITE CONNUE, assumée et signalée : EF-DSH-04 demande aussi « la dernière
  synchronisation par appareil » (RG-Y7, alerte au-delà de 24 h). Le
  référentiel des appareils n'existe pas encore — il relève d'EF-ADM-03. La
  carte de stock le dit explicitement plutôt que d'afficher une valeur
  inventée.
*/

import { useState } from 'react'
import {
  Buildings,
  ClipboardText,
  Clock,
  HardHat,
  Package,
  Prohibit,
  Warning,
  WarningOctagon,
} from '@phosphor-icons/react'
import { Card, JaugeProgression, KpiCard, StatusPill, Table, Tabs } from '@/components/ui'
import type { ColonneTable } from '@/components/ui'
import { EnTetePage } from '@/components/templates'
import {
  chargerAlertesEtapes,
  chargerAvancementChantier,
  chargerAvancementParCorpsEtat,
  chargerAvancementParLogement,
  chargerAvancementParZone,
  chargerMouvementsRecents,
  chargerSyntheseStock,
} from '@/features/pilotage/api'
import { TableauAgregats } from '@/features/pilotage/components/TableauAgregats'
import { useCapacitesPilotage } from '@/features/pilotage/hooks/useCapacitesPilotage'
import {
  libelleSens,
  LIBELLE_NIVEAU_STOCK,
  LIBELLE_STATUT_ETAPE,
  TON_NIVEAU_STOCK,
  TON_STATUT_ETAPE,
} from '@/features/pilotage/presentation/libelles'
import type { AlerteEtape, MouvementRecent } from '@/features/pilotage/types'
import { useRequete } from '@/lib/hooks/useRequete'
import { formatDate, formatDateHeure, formatQuantite } from '@/lib/format'

type Groupement = 'zone' | 'corpsEtat' | 'logement'

/** Requête vide, utilisée quand le rôle n'a pas accès à une section. */
async function aucuneDonnee<T>(valeur: T): Promise<T> {
  return valeur
}

export function PageTableauDeBord() {
  const capacites = useCapacitesPilotage()
  const [groupement, setGroupement] = useState<Groupement>('zone')

  const chantierEtat = useRequete(
    () => (capacites.peutVoirAvancement ? chargerAvancementChantier() : aucuneDonnee(null)),
    [capacites.peutVoirAvancement],
  )
  const zonesEtat = useRequete(
    () => (capacites.peutVoirAvancement ? chargerAvancementParZone() : aucuneDonnee([])),
    [capacites.peutVoirAvancement],
  )
  const logementsEtat = useRequete(
    () => (capacites.peutVoirAvancement ? chargerAvancementParLogement() : aucuneDonnee([])),
    [capacites.peutVoirAvancement],
  )
  const corpsEtat = useRequete(
    () => (capacites.peutVoirCorpsEtat ? chargerAvancementParCorpsEtat() : aucuneDonnee([])),
    [capacites.peutVoirCorpsEtat],
  )
  const alertesEtat = useRequete(
    () => (capacites.peutVoirAlertes ? chargerAlertesEtapes() : aucuneDonnee([])),
    [capacites.peutVoirAlertes],
  )
  const stockEtat = useRequete(
    () => (capacites.peutVoirStock ? chargerSyntheseStock() : aucuneDonnee(null)),
    [capacites.peutVoirStock],
  )
  const mouvementsEtat = useRequete(
    () => (capacites.peutVoirStock ? chargerMouvementsRecents(8) : aucuneDonnee([])),
    [capacites.peutVoirStock],
  )

  const chantier = chantierEtat.donnees
  const stock = stockEtat.donnees
  const alertes = alertesEtat.donnees ?? []

  if (!capacites.peutVoirAvancement) {
    return (
      <Card titre="Accès non autorisé">
        <p className="text-sm text-texte-secondaire">
          Ce rôle n'a pas accès aux indicateurs de pilotage du chantier.
        </p>
      </Card>
    )
  }

  const onglets = [
    { id: 'zone', libelle: 'Par zone', icone: Buildings },
    ...(capacites.peutVoirCorpsEtat
      ? [{ id: 'corpsEtat', libelle: "Par corps d'état", icone: HardHat }]
      : []),
    { id: 'logement', libelle: 'Par logement', icone: Buildings },
  ]

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <EnTetePage
        titre="Tableau de bord"
        description="Chantier de Grand-Bassam — vue de pilotage, lecture seule"
        niveauTitre={1}
        etiquette={
          chantier ? (
            <StatusPill
              libelle={`Calculé le ${formatDate(chantier.dateCalcul)}`}
              ton="neutre"
              taille="sm"
            />
          ) : undefined
        }
      />

      <Card
        titre="Avancement du chantier"
        description="Pourcentage pondéré par les poids des étapes : part validée au premier plan, part déclarée en arrière-plan."
      >
        {chantierEtat.statut === 'erreur' ? (
          <p className="text-sm text-danger">{chantierEtat.erreur}</p>
        ) : (
          <JaugeProgression
            valeur={chantier?.pourcentageValide ?? 0}
            valeurSecondaire={chantier?.pourcentageDeclare ?? 0}
            libelleValeur="Validé"
            libelleValeurSecondaire="Déclaré"
          />
        )}
      </Card>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard
          libelle="Étapes validées"
          valeur={chantier ? `${chantier.nombreValidees} / ${chantier.nombreEtapes}` : '—'}
          icone={ClipboardText}
          accent="marine"
          chargement={chantierEtat.statut === 'chargement'}
        />
        <KpiCard
          libelle="Reste à contrôler"
          valeur={
            chantier
              ? `${(chantier.pourcentageDeclare - chantier.pourcentageValide).toFixed(1)} %`
              : '—'
          }
          icone={ClipboardText}
          accent="or"
          chargement={chantierEtat.statut === 'chargement'}
        />
        <KpiCard
          libelle="Étapes en retard"
          valeur={chantier?.nombreEnRetard ?? '—'}
          icone={Clock}
          accent="or"
          chargement={chantierEtat.statut === 'chargement'}
        />
        <KpiCard
          libelle="Étapes bloquées"
          valeur={chantier?.nombreBloquees ?? '—'}
          icone={Prohibit}
          accent="danger"
          chargement={chantierEtat.statut === 'chargement'}
        />
      </div>

      <Card
        titre="Avancement détaillé"
        description="Même règle de calcul à chaque niveau : somme des poids des étapes terminées sur la somme des poids du périmètre."
        sansRemplissage
      >
        <Tabs
          intitule="Niveau de regroupement"
          actif={groupement}
          onChanger={(id) => setGroupement(id as Groupement)}
          onglets={onglets}
        >
          {groupement === 'zone' && (
            <TableauAgregats
              intitule="Avancement par zone"
              enteteCible="Zone"
              lignes={zonesEtat.donnees ?? []}
              chargement={zonesEtat.statut === 'chargement'}
              messageVide="Aucune zone déclarée sur ce chantier."
            />
          )}
          {groupement === 'corpsEtat' && (
            <TableauAgregats
              intitule="Avancement par corps d'état"
              enteteCible="Corps d'état"
              lignes={corpsEtat.donnees ?? []}
              chargement={corpsEtat.statut === 'chargement'}
              messageVide="Aucun corps d'état n'a d'étape planifiée."
            />
          )}
          {groupement === 'logement' && (
            <TableauAgregats
              intitule="Avancement par logement"
              enteteCible="Logement"
              lignes={logementsEtat.donnees ?? []}
              chargement={logementsEtat.statut === 'chargement'}
              messageVide="Aucun logement déclaré sur ce chantier."
            />
          )}
        </Tabs>
      </Card>

      {capacites.peutVoirAlertes && (
        <Card
          titre="Retards et blocages"
          description="Une étape dont la date prévue est dépassée sans être terminée est en retard ; un blocage immobilise une équipe et passe en premier."
          icone={Warning}
          sansRemplissage
        >
          {alertesEtat.statut === 'erreur' ? (
            <p className="p-5 text-sm text-danger">{alertesEtat.erreur}</p>
          ) : (
            <TableauAlertes lignes={alertes} chargement={alertesEtat.statut === 'chargement'} />
          )}
        </Card>
      )}

      {capacites.peutVoirStock && (
        <div className="grid gap-4 lg:grid-cols-3">
          <KpiCard
            libelle="Articles suivis"
            valeur={stock?.nombreArticles ?? '—'}
            icone={Package}
            accent="marine"
            chargement={stockEtat.statut === 'chargement'}
          />
          <KpiCard
            libelle="Sous le seuil critique"
            valeur={stock?.nombreCritique ?? '—'}
            icone={Warning}
            accent="danger"
            chargement={stockEtat.statut === 'chargement'}
          />
          <KpiCard
            libelle="Stocks négatifs à corriger"
            valeur={stock?.nombreNegatif ?? '—'}
            icone={WarningOctagon}
            accent="danger"
            chargement={stockEtat.statut === 'chargement'}
          />
        </div>
      )}

      {capacites.peutVoirStock && (
        <Card
          titre="Derniers mouvements de stock"
          description="Huit dernières écritures du magasin, tous articles confondus."
          icone={Package}
          sansRemplissage
          pied={
            <p className="text-xs text-texte-secondaire">
              La dernière synchronisation par appareil, demandée par la même exigence, nécessite le
              référentiel des appareils ; il n'est pas encore implémenté et sera traité avec la
              supervision des appareils.
            </p>
          }
        >
          {mouvementsEtat.statut === 'erreur' ? (
            <p className="p-5 text-sm text-danger">{mouvementsEtat.erreur}</p>
          ) : (
            <TableauMouvements
              lignes={mouvementsEtat.donnees ?? []}
              chargement={mouvementsEtat.statut === 'chargement'}
            />
          )}
        </Card>
      )}
    </div>
  )
}

function TableauAlertes({ lignes, chargement }: { lignes: AlerteEtape[]; chargement: boolean }) {
  const colonnes: ColonneTable<AlerteEtape>[] = [
    {
      cle: 'logement',
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
        <div className="flex min-w-0 items-center gap-2">
          <span
            className="h-2.5 w-2.5 shrink-0 rounded-full"
            style={{ backgroundColor: ligne.couleurCorpsEtat }}
            aria-hidden
          />
          <div className="min-w-0">
            <p className="truncate text-texte">{ligne.libelleEtape}</p>
            <p className="truncate text-xs text-texte-secondaire">{ligne.libelleCorpsEtat}</p>
          </div>
        </div>
      ),
    },
    {
      cle: 'statut',
      entete: 'Statut',
      rendu: (ligne) => (
        <StatusPill
          libelle={LIBELLE_STATUT_ETAPE[ligne.statut]}
          ton={TON_STATUT_ETAPE[ligne.statut]}
          taille="sm"
        />
      ),
    },
    {
      cle: 'prevue',
      entete: 'Date prévue',
      triable: true,
      valeurTri: (ligne) => ligne.datePrevue ?? '',
      rendu: (ligne) => formatDate(ligne.datePrevue),
    },
    {
      cle: 'retard',
      entete: 'Retard',
      alignement: 'droite',
      triable: true,
      valeurTri: (ligne) => ligne.joursDeRetard,
      rendu: (ligne) =>
        ligne.joursDeRetard > 0 ? (
          <span className="font-medium text-danger">{ligne.joursDeRetard} j</span>
        ) : (
          <span className="text-texte-secondaire">—</span>
        ),
    },
    {
      cle: 'motif',
      entete: 'Motif',
      rendu: (ligne) => {
        if (!ligne.libelleMotifBlocage) return <span className="text-texte-secondaire">—</span>
        return (
          <div className="min-w-0">
            <p className="truncate text-texte">{ligne.libelleMotifBlocage}</p>
            {ligne.commentaire && (
              <p className="truncate text-xs text-texte-secondaire">{ligne.commentaire}</p>
            )}
          </div>
        )
      },
    },
  ]

  return (
    <Table
      intitule="Étapes en retard ou bloquées"
      colonnes={colonnes}
      lignes={lignes}
      cleLigne={(ligne) => ligne.idEtape}
      chargement={chargement}
      messageVide="Aucun retard ni blocage à signaler."
      lectureSeule
      parPage={8}
    />
  )
}

function TableauMouvements({
  lignes,
  chargement,
}: {
  lignes: MouvementRecent[]
  chargement: boolean
}) {
  const colonnes: ColonneTable<MouvementRecent>[] = [
    {
      cle: 'article',
      entete: 'Article',
      triable: true,
      valeurTri: (ligne) => ligne.libelleArticle,
      rendu: (ligne) => (
        <div className="min-w-0">
          <p className="truncate font-medium text-texte">{ligne.libelleArticle}</p>
          <p className="truncate text-xs text-texte-secondaire">{ligne.codeArticle}</p>
        </div>
      ),
    },
    {
      cle: 'sens',
      entete: 'Sens',
      rendu: (ligne) => (
        <StatusPill
          libelle={libelleSens(ligne.sens)}
          ton={ligne.sens > 0 ? 'succes' : 'information'}
          taille="sm"
        />
      ),
    },
    {
      cle: 'quantite',
      entete: 'Quantité',
      alignement: 'droite',
      triable: true,
      valeurTri: (ligne) => ligne.quantiteSaisie,
      rendu: (ligne) => formatQuantite(ligne.quantiteSaisie, ligne.codeUnite),
    },
    {
      cle: 'niveau',
      entete: 'Niveau de l’article',
      rendu: (ligne) => (
        <StatusPill
          libelle={LIBELLE_NIVEAU_STOCK[ligne.niveauAlerteArticle]}
          ton={TON_NIVEAU_STOCK[ligne.niveauAlerteArticle]}
          taille="sm"
        />
      ),
    },
    {
      cle: 'date',
      entete: 'Opération',
      triable: true,
      valeurTri: (ligne) => ligne.dateOperation,
      rendu: (ligne) => formatDate(ligne.dateOperation),
    },
    {
      cle: 'serveur',
      entete: 'Reçu le',
      rendu: (ligne) => (
        <span className="text-texte-secondaire">{formatDateHeure(ligne.horodatageServeur)}</span>
      ),
    },
    {
      cle: 'auteur',
      entete: 'Auteur',
      rendu: (ligne) => ligne.nomAuteur,
    },
  ]

  return (
    <Table
      intitule="Derniers mouvements de stock"
      colonnes={colonnes}
      lignes={lignes}
      cleLigne={(ligne) => ligne.uuid}
      chargement={chargement}
      messageVide="Aucun mouvement enregistré."
      lectureSeule
    />
  )
}
