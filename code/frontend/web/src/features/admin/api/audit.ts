/*
  Appels réseau du journal d'audit (EF-AUT-08), sur le client axios partagé.

  Le module est en LECTURE SEULE : le journal est immuable (RG-S8), les entrées
  sont écrites par le serveur au moment où il exécute une action
  d'administration, jamais par cet écran. Le filtrage est fait côté serveur, en
  paramètres de requête, pour la même raison que le journal d'exécution : le
  journal grandit et ne doit pas être rapatrié en entier pour être filtré dans
  le navigateur.
*/

import { http } from '@/lib/api/http'
import type { EntreeAuditDto } from '@/features/admin/api/audit-dto'
import type { EntreeAudit, FiltresAudit } from '@/features/admin/types/audit'

/** Passe une action `UPPER_SNAKE` du transport en forme domaine `minuscule`. */
function actionDepuisDb(valeur: string): string {
  return valeur.toLowerCase()
}

function mapperEntree(dto: EntreeAuditDto): EntreeAudit {
  return {
    id: dto.id_entree,
    action: actionDepuisDb(dto.action),
    typeObjet: dto.type_objet,
    idObjet: dto.id_objet,
    resume: dto.resume,
    horodatage: dto.horodatage,
    adresseIp: dto.adresse_ip,
    idAuteur: dto.utilisateur_id_utilisateur,
    identifiantAuteur: dto.identifiant_utilisateur,
    nomAuteur: dto.nom_utilisateur,
  }
}

/**
 * Journal d'audit filtré (EF-AUT-08).
 *
 * Les filtres nuls ne sont pas transmis, pour que la requête reste lisible
 * côté serveur. `action` est renvoyée en `UPPER_SNAKE`, forme du transport.
 */
export async function chargerAudit(filtres: FiltresAudit): Promise<EntreeAudit[]> {
  const params: Record<string, string> = {}
  if (filtres.action) params.action = filtres.action.toUpperCase()
  if (filtres.idAuteur) params.auteur = filtres.idAuteur

  const reponse = await http.get<EntreeAuditDto[]>('/audit', { params })
  return reponse.data.map(mapperEntree)
}
