/*
  Données de démonstration de l'espace acquéreur (UC-5, EF-ACQ-01/02).

  Le logement A01 du chantier de Grand-Bassam, tel qu'un acquéreur le verrait :
  quelques étapes à différents stades, un avancement global, et les
  notifications d'étapes franchies. Le serveur scope normalement ces données au
  logement du compte connecté (périmètre PER-LOG-A01 du compte acquéreur du jeu
  d'essai) ; la simulation renvoie directement ce logement, sans paramètre.

  Les statuts et couleurs reprennent le vocabulaire du module avancement, pour
  que l'acquéreur voie les mêmes états que le pilotage, en version simplifiée.
*/

import type {
  AvancementLogementDto,
  NotificationAcquereurDto,
} from '@/features/acquereur/api/dto'

function ilYaJours(jours: number): string {
  return new Date(Date.now() - jours * 86_400_000).toISOString()
}

const LOGEMENT: AvancementLogementDto = {
  numero_logement: 'A01',
  libelle_zone: 'Zone A',
  libelle_type_logement: 'Villa 3 pièces',
  pourcentage_valide: '45.000',
  pourcentage_declare: '58.000',
  date_livraison_prevue: '2027-03-31',
  etapes: [
    {
      id_etape: 'ET-A01-01',
      libelle_etape: 'Fondations',
      libelle_corps_etat: 'Gros œuvre',
      couleur_corps_etat: '#6c8ebf',
      statut: 'VALIDEE',
      date_franchissement: ilYaJours(40),
    },
    {
      id_etape: 'ET-A01-02',
      libelle_etape: 'Élévation des murs',
      libelle_corps_etat: 'Gros œuvre',
      couleur_corps_etat: '#6c8ebf',
      statut: 'VALIDEE',
      date_franchissement: ilYaJours(18),
    },
    {
      id_etape: 'ET-A01-03',
      libelle_etape: 'Dalle de plancher',
      libelle_corps_etat: 'Gros œuvre',
      couleur_corps_etat: '#6c8ebf',
      statut: 'TERMINEE_DECLAREE',
      date_franchissement: null,
    },
    {
      id_etape: 'ET-A01-04',
      libelle_etape: 'Toiture',
      libelle_corps_etat: 'Couverture',
      couleur_corps_etat: '#d79b00',
      statut: 'EN_COURS',
      date_franchissement: null,
    },
    {
      id_etape: 'ET-A01-05',
      libelle_etape: 'Cloisons intérieures',
      libelle_corps_etat: 'Second œuvre',
      couleur_corps_etat: '#82b366',
      statut: 'A_FAIRE',
      date_franchissement: null,
    },
  ],
}

const NOTIFICATIONS: NotificationAcquereurDto[] = [
  {
    id_notification: 'NOT-A01-02',
    libelle_etape: 'Élévation des murs',
    date_franchissement: ilYaJours(18),
    lue: false,
  },
  {
    id_notification: 'NOT-A01-01',
    libelle_etape: 'Fondations',
    date_franchissement: ilYaJours(40),
    lue: true,
  },
]

export function logementAcquereur(): AvancementLogementDto {
  return LOGEMENT
}

export function notificationsAcquereur(): NotificationAcquereurDto[] {
  return NOTIFICATIONS
}
