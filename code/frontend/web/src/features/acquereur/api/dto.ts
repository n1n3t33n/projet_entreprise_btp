/*
  Contrats de transport de l'espace acquéreur (UC-5). `snake_case`,
  énumérations `UPPER_SNAKE`, décimaux en chaîne (`numeric(14,3)`). Le serveur
  scope la réponse au logement du compte connecté (EF-AUT-02) : aucun
  identifiant de logement n'est transmis par le client.
*/

import type { StatutEtapeDb } from '@/features/avancement/api/dto'

export type EtapeAcquereurDto = {
  id_etape: string
  libelle_etape: string
  libelle_corps_etat: string
  couleur_corps_etat: string
  statut: StatutEtapeDb
  date_franchissement: string | null
}

export type AvancementLogementDto = {
  numero_logement: string
  libelle_zone: string
  libelle_type_logement: string
  pourcentage_valide: string
  pourcentage_declare: string
  date_livraison_prevue: string | null
  etapes: EtapeAcquereurDto[]
}

export type NotificationAcquereurDto = {
  id_notification: string
  libelle_etape: string
  date_franchissement: string
  lue: boolean
}
