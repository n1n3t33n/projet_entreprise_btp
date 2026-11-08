/*
  Appels réseau des magasins et de l'arborescence magasins / familles.
*/

import { http } from '@/lib/api/http'
import type { Magasin, NoeudStock } from '@/features/stock/types'
import type { MagasinDto } from '@/features/stock/api/dto'

function mapperMagasin(dto: MagasinDto): Magasin {
  return {
    idMagasin: dto.id_magasin,
    code: dto.code,
    libelle: dto.libelle,
    idChantier: dto.id_chantier,
    libelleChantier: dto.libelle_chantier,
  }
}

/** Magasins accessibles (le pilote n'en porte qu'un, Grand-Bassam). */
export async function listerMagasins(): Promise<Magasin[]> {
  const reponse = await http.get<MagasinDto[]>('/magasins')
  return reponse.data.map(mapperMagasin)
}

/**
 * Arborescence chantier → magasins et familles d'articles.
 *
 * Le serveur sert l'arbre déjà construit : l'écran ne fait que l'afficher.
 */
export async function listerArborescenceStock(): Promise<NoeudStock[]> {
  const reponse = await http.get<NoeudStock[]>('/stock/arborescence')
  return reponse.data
}
