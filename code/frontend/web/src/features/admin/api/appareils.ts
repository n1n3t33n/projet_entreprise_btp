/*
  Appels réseau du domaine « appareils enrôlés » (EF-ADM-03 superviser,
  EF-AUT-06 révoquer la partie appareil), sur le client axios partagé.

  La révocation est la seule écriture. Elle traduit l'opération
  `Appareil.revoquer()` de CL-1 : côté serveur, SQ-5 (étape 12) précise que la
  révocation entraîne un « blocage serveur immédiat et journalisation », puis
  qu'à la prochaine synchronisation le jeton de l'appareil est refusé (401) et
  la base locale chiffrée est effacée (ET-4, état « Données locales effacées »).
  Le client ne fait qu'émettre l'ordre ; l'effet terrain relève du mobile et du
  backend.
*/

import { http } from '@/lib/api/http'
import type { StatutAppareilDb, AppareilDto } from '@/features/admin/api/appareils-dto'
import type { Appareil, StatutAppareil } from '@/features/admin/types/appareils'

const STATUT_DEPUIS_DB: Record<StatutAppareilDb, StatutAppareil> = {
  ACTIF: 'actif',
  REVOQUE: 'revoque',
  INACTIF: 'inactif',
}

function mapperAppareil(dto: AppareilDto): Appareil {
  return {
    id: dto.id_appareil,
    empreinteMateriel: dto.empreinte_materiel,
    plateforme: dto.plateforme,
    versionApplication: dto.version_application,
    derniereSynchronisation: dto.derniere_synchronisation,
    statut: STATUT_DEPUIS_DB[dto.statut] ?? 'inactif',
    idUtilisateur: dto.utilisateur_id_utilisateur,
    identifiantUtilisateur: dto.identifiant_utilisateur,
    nomUtilisateur: dto.nom_utilisateur,
  }
}

/** Liste des appareils enrôlés, tous comptes confondus (EF-ADM-03). */
export async function listerAppareils(): Promise<Appareil[]> {
  const reponse = await http.get<AppareilDto[]>('/appareils')
  return reponse.data.map(mapperAppareil)
}

/**
 * Révoque un appareil (EF-AUT-06, CL-1 `Appareil.revoquer()`).
 *
 * Action irréversible côté métier : un appareil révoqué devra être ré-enrôlé
 * par une nouvelle connexion en ligne (ET-4). Le serveur journalise la
 * révocation (SQ-5 étape 12, EF-AUT-08).
 */
export async function revoquerAppareil(id: string): Promise<void> {
  await http.post(`/appareils/${id}/revocation`, {})
}
