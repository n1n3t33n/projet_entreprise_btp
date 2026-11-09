/*
  Contrats de transport du module pilotage, tels que le serveur les expose.

  Convention du projet : `snake_case`, énumérations en `UPPER_SNAKE`, décimaux
  transportés en chaîne (`numeric(14,3)` du MPD) et convertis à la frontière de
  l'application. Rien de ce fichier ne sort du dossier `api`.

  Correspondances avec la modélisation :
  - `AvancementAgregeDto` ← CL-5 `AvancementAgrege { portee, pourcentageDeclare,
    pourcentageValide, nombreEtapes, dateCalcul }`, calculé selon RG-A6.
  - `AlerteEtapeDto` ← CL-5 `EtapeTravaux.estEnRetard()` et RG-A8.
  - `EvenementJournalDto` ← CL-5 `EvenementExecution`, enrichi du contexte
    (logement, zone, corps d'état) dont le journal a besoin pour être lisible
    sans appel supplémentaire. RG-A5 impose les deux horodatages.
  - `SyntheseStockDto` ← RG-S5 (deux seuils par article et magasin) et MPD-4
    (`type_alerte = STOCK_NEGATIF`).
*/

import type { MouvementStockDto, NiveauAlerteDb } from '@/features/stock/api/dto'
import type { StatutEtapeDb } from '@/features/avancement/api/dto'

/** Niveau de regroupement d'un agrégat d'avancement (CL-5 `Portee`). */
export type PorteeAgregatDb = 'CHANTIER' | 'ZONE' | 'LOGEMENT' | 'CORPS_ETAT'

export type AvancementAgregeDto = {
  portee: PorteeAgregatDb
  /** Identifiant de la cible agrégée : id de zone, de logement, code de corps d'état. */
  id_cible: string
  libelle_cible: string
  /** Contexte secondaire affiché en sous-titre (la zone d'un logement, par exemple). */
  libelle_secondaire: string | null
  /** Couleur du corps d'état, reprise de la gamme (CL-2). Nulle hors corps d'état. */
  couleur: string | null
  pourcentage_declare: string
  pourcentage_valide: string
  nombre_etapes: number
  nombre_validees: number
  nombre_bloquees: number
  nombre_en_retard: number
  date_calcul: string
}

export type AlerteEtapeDto = {
  id_etape: string
  id_logement: string
  numero_logement: string
  libelle_zone: string
  libelle_etape: string
  libelle_corps_etat: string
  couleur_corps_etat: string
  statut: StatutEtapeDb
  date_prevue: string | null
  /** Entier positif. Zéro pour une étape bloquée mais non encore en retard. */
  jours_de_retard: number
  code_motif_blocage: string | null
  libelle_motif_blocage: string | null
  commentaire: string | null
}

export type EvenementJournalDto = {
  uuid: string
  id_etape: string
  libelle_etape: string
  id_logement: string
  numero_logement: string
  libelle_zone: string
  code_corps_etat: string
  libelle_corps_etat: string
  statut_avant: StatutEtapeDb | null
  statut_apres: StatutEtapeDb
  horodatage_appareil: string
  horodatage_serveur: string
  id_auteur: string
  nom_auteur: string
  est_delegation: boolean
  code_motif_blocage: string | null
  libelle_motif_blocage: string | null
  commentaire: string | null
}

export type SyntheseStockDto = {
  nombre_articles: number
  nombre_critique: number
  nombre_vigilance: number
  /** Articles dont le stock calculé est négatif (anomalie à corriger, MPD-4). */
  nombre_negatif: number
}

/** Mouvement récent enrichi du libellé d'article, pour la vue de pilotage. */
export type MouvementRecentDto = MouvementStockDto & {
  code_article: string
  libelle_article: string
  code_unite: string
  niveau_alerte_article: NiveauAlerteDb
}

/** Intervenant proposé comme filtre du journal (RG-A5 : « qui »). */
export type IntervenantJournalDto = {
  id_utilisateur: string
  nom: string
}
