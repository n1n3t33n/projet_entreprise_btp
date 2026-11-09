/*
  Données de démonstration des appareils enrôlés (MPD-1 table `appareil`,
  CL-1 `Appareil`).

  Chaque appareil appartient à un compte existant du jeu d'essai
  (`auth-grand-bassam`), pour que la colonne « propriétaire » de la supervision
  pointe vers de vrais utilisateurs. Le jeu couvre volontairement les trois
  statuts et les trois fraîcheurs de synchronisation (RG-Y7), afin que l'écran
  exerce tous ses rendus :
  - un appareil actif synchronisé il y a peu (à jour) ;
  - un appareil actif synchronisé il y a plus de 24 h (en retard, RG-Y7) ;
  - un appareil actif jamais synchronisé (enrôlé, pas encore de première remontée) ;
  - un appareil déjà révoqué.

  Les horodatages sont calculés au chargement, relativement à l'heure courante,
  pour que le cas « en retard » le reste quel que soit le jour d'exécution de la
  démonstration. La révocation est appliquée en mémoire, le temps de la session,
  comme le reste des données simulées : un rechargement complet de la page les
  remet à zéro.
*/

import type { AppareilDto, StatutAppareilDb } from '@/features/admin/api/appareils-dto'

/** Propriétaires, repris des comptes de `auth-grand-bassam` (USR-00x). */
const PROPRIETAIRES: Record<string, { identifiant: string; nom: string }> = {
  'USR-003': { identifiant: 'k.n-guessan', nom: "Koffi N'Guessan" },
  'USR-004': { identifiant: 's.traore', nom: 'Salimata Traoré' },
  'USR-005': { identifiant: 'm.diallo', nom: 'Mariam Diallo' },
}

function ilYa(heures: number): string {
  return new Date(Date.now() - heures * 3_600_000).toISOString()
}

function proprietaire(id: string): { identifiant: string; nom: string } {
  return PROPRIETAIRES[id] ?? { identifiant: '—', nom: '—' }
}

function appareil(
  id: string,
  empreinte: string,
  plateforme: string,
  version: string,
  derniereSynchro: string | null,
  statut: StatutAppareilDb,
  idUtilisateur: string,
): AppareilDto {
  const p = proprietaire(idUtilisateur)
  return {
    id_appareil: id,
    empreinte_materiel: empreinte,
    plateforme,
    version_application: version,
    derniere_synchronisation: derniereSynchro,
    statut,
    utilisateur_id_utilisateur: idUtilisateur,
    identifiant_utilisateur: p.identifiant,
    nom_utilisateur: p.nom,
  }
}

let appareils: AppareilDto[] = [
  // Actif, synchronisé il y a 2 h → à jour.
  appareil('APP-001', 'A1B2-C3D4-E5F6', 'Android 14', '1.0.0', ilYa(2), 'ACTIF', 'USR-003'),
  // Actif, synchronisé il y a 40 h → en retard (RG-Y7, > 24 h).
  appareil('APP-002', '77AA-88BB-99CC', 'Android 13', '1.0.0', ilYa(40), 'ACTIF', 'USR-004'),
  // Actif, jamais synchronisé → enrôlé mais pas de première remontée.
  appareil('APP-003', 'DEAD-BEEF-0001', 'iOS 17', '1.0.0', null, 'ACTIF', 'USR-003'),
  // Déjà révoqué (téléphone perdu, SQ-5).
  appareil('APP-004', '1234-5678-9ABC', 'Android 12', '0.9.3', ilYa(170), 'REVOQUE', 'USR-005'),
]

export function listerAppareils(): AppareilDto[] {
  return appareils
}

/**
 * Révoque un appareil (CL-1 `Appareil.revoquer()`).
 *
 * Retourne l'appareil mis à jour, ou `undefined` si l'identifiant est inconnu.
 * Un appareil déjà révoqué le reste : l'opération est idempotente.
 */
export function revoquerAppareilMock(id: string): AppareilDto | undefined {
  const cible = appareils.find((a) => a.id_appareil === id)
  if (!cible) {
    return undefined
  }
  cible.statut = 'REVOQUE'
  return cible
}

/** Réinitialise le jeu d'essai (utilisé par les tests, jamais par l'écran). */
export function reinitialiserAppareils(): void {
  appareils = [
    appareil('APP-001', 'A1B2-C3D4-E5F6', 'Android 14', '1.0.0', ilYa(2), 'ACTIF', 'USR-003'),
    appareil('APP-002', '77AA-88BB-99CC', 'Android 13', '1.0.0', ilYa(40), 'ACTIF', 'USR-004'),
    appareil('APP-003', 'DEAD-BEEF-0001', 'iOS 17', '1.0.0', null, 'ACTIF', 'USR-003'),
    appareil('APP-004', '1234-5678-9ABC', 'Android 12', '0.9.3', ilYa(170), 'REVOQUE', 'USR-005'),
  ]
}
