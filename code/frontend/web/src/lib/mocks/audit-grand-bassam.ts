/*
  Données de démonstration du journal d'audit des actions d'administration
  (MPD-1 table `journal_audit`, CL-1 `JournalAudit`).

  Ce journal est DISTINCT du journal d'exécution (RG-A5, module pilotage) : il
  trace les actions d'ADMINISTRATION (création de compte, révocation d'appareil,
  modification de la matrice des droits…), là où le journal d'exécution trace
  les changements de statut des étapes de travaux. Les deux partagent le même
  principe d'immuabilité : MPD-1 pose sur `journal_audit` le déclencheur
  `trg_journal_audit_immuable` qui rejette tout UPDATE et tout DELETE (RG-S8).
  La simulation respecte ce principe : on n'expose qu'une lecture et un ajout,
  jamais de modification ni de suppression.

  `consignerAudit` est appelée par les autres routes de simulation au moment où
  elles effectuent une action d'administration (la révocation d'un appareil, par
  exemple), exactement comme le serveur journalise l'action qu'il vient
  d'exécuter (SQ-5 étape 12). L'auteur et l'adresse IP sont ceux du contexte de
  démonstration : le poste de l'administrateur de la session.
*/

import type { EntreeAuditDto } from '@/features/admin/api/audit-dto'

/** Auteur par défaut des entrées consignées pendant la démonstration. */
const AUTEUR_DEMO = {
  id: 'USR-002',
  identifiant: 'y.bamba',
  nom: 'Yacouba Bamba',
}
const ADRESSE_IP_DEMO = '197.234.12.8'

function ilYa(heures: number): string {
  return new Date(Date.now() - heures * 3_600_000).toISOString()
}

let compteur = 0

function nouvelId(): string {
  compteur += 1
  return `AUD-${String(compteur).padStart(4, '0')}`
}

/** Entrées de départ, antérieures à la session, pour que l'écran ne soit pas vide. */
let entrees: EntreeAuditDto[] = [
  {
    id_entree: nouvelId(),
    action: 'CREATION_COMPTE',
    type_objet: 'utilisateur',
    id_objet: 'USR-004',
    resume: 'Création du compte s.traore (Salimata Traoré), rôle Commercial',
    horodatage: ilYa(72),
    adresse_ip: ADRESSE_IP_DEMO,
    utilisateur_id_utilisateur: AUTEUR_DEMO.id,
    identifiant_utilisateur: AUTEUR_DEMO.identifiant,
    nom_utilisateur: AUTEUR_DEMO.nom,
  },
  {
    id_entree: nouvelId(),
    action: 'MODIFICATION_DROITS',
    type_objet: 'matrice_droits',
    id_objet: null,
    resume: "Ouverture de l'écran « Avancement » au rôle Commercial",
    horodatage: ilYa(50),
    adresse_ip: ADRESSE_IP_DEMO,
    utilisateur_id_utilisateur: AUTEUR_DEMO.id,
    identifiant_utilisateur: AUTEUR_DEMO.identifiant,
    nom_utilisateur: AUTEUR_DEMO.nom,
  },
  {
    id_entree: nouvelId(),
    action: 'REVOCATION_APPAREIL',
    type_objet: 'appareil',
    id_objet: 'APP-004',
    resume: "Révocation de l'appareil 1234-5678-9ABC (Mariam Diallo)",
    horodatage: ilYa(26),
    adresse_ip: ADRESSE_IP_DEMO,
    utilisateur_id_utilisateur: AUTEUR_DEMO.id,
    identifiant_utilisateur: AUTEUR_DEMO.identifiant,
    nom_utilisateur: AUTEUR_DEMO.nom,
  },
]

export function listerAudit(): EntreeAuditDto[] {
  // Du plus récent au plus ancien : l'écran veut la dernière action en haut.
  return [...entrees].sort((a, b) => b.horodatage.localeCompare(a.horodatage))
}

export type SaisieAudit = {
  action: string
  typeObjet: string
  idObjet?: string | null
  resume: string
}

/**
 * Consigne une action d'administration (CL-1 `JournalAudit.consigner`).
 *
 * Ajout seul : conforme à l'immuabilité du journal (RG-S8). Retourne l'entrée
 * créée. L'auteur et l'adresse IP sont ceux du contexte de démonstration.
 */
export function consignerAudit(saisie: SaisieAudit): EntreeAuditDto {
  const entree: EntreeAuditDto = {
    id_entree: nouvelId(),
    action: saisie.action,
    type_objet: saisie.typeObjet,
    id_objet: saisie.idObjet ?? null,
    resume: saisie.resume,
    horodatage: new Date().toISOString(),
    adresse_ip: ADRESSE_IP_DEMO,
    utilisateur_id_utilisateur: AUTEUR_DEMO.id,
    identifiant_utilisateur: AUTEUR_DEMO.identifiant,
    nom_utilisateur: AUTEUR_DEMO.nom,
  }
  entrees.push(entree)
  return entree
}

/** Réinitialise le jeu d'essai (tests uniquement). */
export function reinitialiserAudit(): void {
  compteur = 0
  entrees = []
}
