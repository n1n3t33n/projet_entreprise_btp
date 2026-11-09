/*
  Appels réseau du module pilotage, sur le client axios partagé.

  Le module est en lecture seule : aucune route n'écrit. C'est une conséquence
  directe de RG-A5 (les événements d'exécution sont immuables) et du rôle des
  écrans concernés — observer, pas agir. Toute correction passe par les écrans
  du module avancement, qui créent un nouvel événement.

  Le filtrage du journal est fait côté serveur, en paramètres de requête : le
  journal grandit avec le chantier et ne doit pas être rapatrié en entier pour
  être filtré dans le navigateur.
*/

import { http } from '@/lib/api/http'
import type {
  AlerteEtapeDto,
  AvancementAgregeDto,
  EvenementJournalDto,
  IntervenantJournalDto,
  MouvementRecentDto,
  SyntheseStockDto,
} from '@/features/pilotage/api/dto'
import {
  mapperAgregat,
  mapperAlerteEtape,
  mapperEvenementJournal,
  mapperIntervenant,
  mapperMouvementRecent,
  mapperSyntheseStock,
} from '@/features/pilotage/api/mapping'
import type {
  AlerteEtape,
  AvancementAgrege,
  EvenementJournal,
  FiltresJournal,
  IntervenantJournal,
  MouvementRecent,
  SyntheseStock,
} from '@/features/pilotage/types/domaine'

/** Avancement du chantier entier (RG-A6, portée CHANTIER). */
export async function chargerAvancementChantier(): Promise<AvancementAgrege> {
  const reponse = await http.get<AvancementAgregeDto>('/pilotage/avancement/chantier')
  return mapperAgregat(reponse.data)
}

/** Avancement par zone (EF-DSH-01). */
export async function chargerAvancementParZone(): Promise<AvancementAgrege[]> {
  const reponse = await http.get<AvancementAgregeDto[]>('/pilotage/avancement/zones')
  return reponse.data.map(mapperAgregat)
}

/** Avancement par logement (EF-DSH-01). */
export async function chargerAvancementParLogement(): Promise<AvancementAgrege[]> {
  const reponse = await http.get<AvancementAgregeDto[]>('/pilotage/avancement/logements')
  return reponse.data.map(mapperAgregat)
}

/** Avancement par corps d'état (EF-DSH-02). */
export async function chargerAvancementParCorpsEtat(): Promise<AvancementAgrege[]> {
  const reponse = await http.get<AvancementAgregeDto[]>('/pilotage/avancement/corps-etat')
  return reponse.data.map(mapperAgregat)
}

/** Étapes en retard ou bloquées (EF-DSH-05, RG-A8). */
export async function chargerAlertesEtapes(): Promise<AlerteEtape[]> {
  const reponse = await http.get<AlerteEtapeDto[]>('/pilotage/alertes-etapes')
  return reponse.data.map(mapperAlerteEtape)
}

/** Compteurs de stock par niveau d'alerte (EF-DSH-04, RG-S5). */
export async function chargerSyntheseStock(): Promise<SyntheseStock> {
  const reponse = await http.get<SyntheseStockDto>('/pilotage/stock/synthese')
  return mapperSyntheseStock(reponse.data)
}

/** Derniers mouvements de stock, tous articles confondus (EF-DSH-04). */
export async function chargerMouvementsRecents(limite = 8): Promise<MouvementRecent[]> {
  const reponse = await http.get<MouvementRecentDto[]>('/pilotage/stock/mouvements-recents', {
    params: { limite },
  })
  return reponse.data.map(mapperMouvementRecent)
}

/** Intervenants ayant produit au moins un événement, pour le filtre du journal. */
export async function listerIntervenants(): Promise<IntervenantJournal[]> {
  const reponse = await http.get<IntervenantJournalDto[]>('/pilotage/journal/intervenants')
  return reponse.data.map(mapperIntervenant)
}

/**
 * Journal d'exécution filtré (EF-DSH-03).
 *
 * Les filtres nuls ne sont pas transmis, pour que la requête reste lisible
 * côté serveur et que le cache HTTP puisse s'appliquer.
 */
export async function chargerJournal(filtres: FiltresJournal): Promise<EvenementJournal[]> {
  const params: Record<string, string> = {}
  if (filtres.idAuteur) params.auteur = filtres.idAuteur
  if (filtres.idZone) params.zone = filtres.idZone
  if (filtres.statutApres) params.statut = filtres.statutApres
  if (filtres.depuis) params.depuis = filtres.depuis
  if (filtres.jusqua) params.jusqua = filtres.jusqua

  const reponse = await http.get<EvenementJournalDto[]>('/pilotage/journal', { params })
  return reponse.data.map(mapperEvenementJournal)
}
