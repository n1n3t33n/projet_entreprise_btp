/*
  Appels réseau de l'espace acquéreur (UC-5, EF-ACQ-01/02). Lecture seule.

  La correspondance des statuts d'étape n'est pas redéfinie ici : on réutilise
  celle du module avancement, propriétaire de l'énuméré, pour qu'un statut ait
  le même sens partout (même principe que le module pilotage).
*/

import { http } from '@/lib/api/http'
import { nombreDepuisChaine, statutEtapeDepuisDb } from '@/features/avancement/api/mapping'
import type {
  AvancementLogementDto,
  EtapeAcquereurDto,
  NotificationAcquereurDto,
} from '@/features/acquereur/api/dto'
import type {
  AvancementLogement,
  EtapeAcquereur,
  NotificationAcquereur,
} from '@/features/acquereur/types/domaine'

function mapperEtape(dto: EtapeAcquereurDto): EtapeAcquereur {
  return {
    idEtape: dto.id_etape,
    libelleEtape: dto.libelle_etape,
    libelleCorpsEtat: dto.libelle_corps_etat,
    couleurCorpsEtat: dto.couleur_corps_etat,
    statut: statutEtapeDepuisDb(dto.statut),
    dateFranchissement: dto.date_franchissement,
  }
}

/** Avancement du logement de l'acquéreur connecté (EF-ACQ-01). */
export async function chargerAvancementLogement(): Promise<AvancementLogement> {
  const reponse = await http.get<AvancementLogementDto>('/acquereur/logement')
  const dto = reponse.data
  return {
    numeroLogement: dto.numero_logement,
    libelleZone: dto.libelle_zone,
    libelleTypeLogement: dto.libelle_type_logement,
    pourcentageValide: nombreDepuisChaine(dto.pourcentage_valide),
    pourcentageDeclare: nombreDepuisChaine(dto.pourcentage_declare),
    dateLivraisonPrevue: dto.date_livraison_prevue,
    etapes: dto.etapes.map(mapperEtape),
  }
}

/** Notifications d'étapes franchies adressées à l'acquéreur (EF-ACQ-02). */
export async function chargerNotificationsAcquereur(): Promise<NotificationAcquereur[]> {
  const reponse = await http.get<NotificationAcquereurDto[]>('/acquereur/notifications')
  return reponse.data.map((dto) => ({
    id: dto.id_notification,
    libelleEtape: dto.libelle_etape,
    dateFranchissement: dto.date_franchissement,
    lue: dto.lue,
  }))
}
