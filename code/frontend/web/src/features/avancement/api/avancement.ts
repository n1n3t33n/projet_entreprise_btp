/*
  Appels réseau du module avancement, sur le client axios partagé. Chaque
  fonction renvoie des types du domaine ; l'adaptateur de simulation se branche
  sur le même client.
*/

import { http } from '@/lib/api/http'
import type {
  DeclarationBlocage,
  DecisionValidationEtape,
  EvenementExecution,
  LigneEtape,
  LigneLogement,
  MotifBlocage,
  SyntheseAvancement,
  Zone,
} from '@/features/avancement/types'
import type {
  EvenementExecutionDto,
  LigneEtapeDto,
  LigneLogementDto,
  MotifBlocageDto,
  SyntheseAvancementDto,
  ZoneDto,
} from '@/features/avancement/api/dto'
import {
  mapperEvenement,
  mapperLigneEtape,
  mapperLigneLogement,
  mapperMotifBlocage,
  mapperSynthese,
  mapperZone,
} from '@/features/avancement/api/mapping'

/** Zones du chantier (pour le filtre du suivi). */
export async function listerZones(): Promise<Zone[]> {
  const reponse = await http.get<ZoneDto[]>('/avancement/zones')
  return reponse.data.map(mapperZone)
}

/** Synthèse d'avancement du chantier (indicateurs d'en-tête). */
export async function obtenirSynthese(): Promise<SyntheseAvancement> {
  const reponse = await http.get<SyntheseAvancementDto>('/avancement/synthese')
  return mapperSynthese(reponse.data)
}

/** Avancement par logement (EF-DSH-05, suivi). */
export async function listerLogements(): Promise<LigneLogement[]> {
  const reponse = await http.get<LigneLogementDto[]>('/avancement/logements')
  return reponse.data.map(mapperLigneLogement)
}

/** Étapes d'un logement, ordonnées. */
export async function listerEtapesLogement(idLogement: string): Promise<LigneEtape[]> {
  const reponse = await http.get<LigneEtapeDto[]>(`/logements/${idLogement}/etapes`)
  return reponse.data.map(mapperLigneEtape)
}

/** Étapes à contrôle en attente de validation (EF-AVA-06), toutes zones confondues. */
export async function listerEtapesAValider(): Promise<LigneEtape[]> {
  const reponse = await http.get<LigneEtapeDto[]>('/avancement/etapes-a-valider')
  return reponse.data.map(mapperLigneEtape)
}

/** Historique complet d'une étape (EF-AVA-10). */
export async function listerEvenementsEtape(idEtape: string): Promise<EvenementExecution[]> {
  const reponse = await http.get<EvenementExecutionDto[]>(`/etapes/${idEtape}/evenements`)
  return reponse.data.map(mapperEvenement)
}

/** Motifs de blocage disponibles (référentiel). */
export async function listerMotifsBlocage(): Promise<MotifBlocage[]> {
  const reponse = await http.get<MotifBlocageDto[]>('/motifs-blocage')
  return reponse.data.map(mapperMotifBlocage)
}

/** Valide ou rejette une étape à contrôle (EF-AVA-06). Renvoie l'événement créé. */
export async function validerEtape(decision: DecisionValidationEtape): Promise<EvenementExecution> {
  const reponse = await http.post<EvenementExecutionDto>(
    `/etapes/${decision.idEtape}/validation`,
    { decision: decision.decision, motif: decision.motif },
  )
  return mapperEvenement(reponse.data)
}

/** Déclare une étape bloquée avec motif (EF-AVA-05). Renvoie l'événement créé. */
export async function declarerBlocage(declaration: DeclarationBlocage): Promise<EvenementExecution> {
  const reponse = await http.post<EvenementExecutionDto>(
    `/etapes/${declaration.idEtape}/blocage`,
    { code_motif: declaration.codeMotif, commentaire: declaration.commentaire },
  )
  return mapperEvenement(reponse.data)
}
