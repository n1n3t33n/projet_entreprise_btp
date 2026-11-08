/*
  Appels réseau des magasins et de l'arborescence magasins / familles.
*/

import { http } from '@/lib/api/http'
import type { LogementDestination, Magasin, NoeudStock } from '@/features/stock/types'
import type { LogementDestinationDto, MagasinDto } from '@/features/stock/api/dto'

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

/**
 * Logements du chantier d'un magasin, destinations possibles d'une sortie
 * (EF-STK-01). Remplace la liste codée en dur des premières étapes : une
 * sortie est désormais rattachée à un vrai logement du chantier.
 */
export async function listerLogementsChantier(idChantier: string): Promise<LogementDestination[]> {
  const reponse = await http.get<LogementDestinationDto[]>(`/chantiers/${idChantier}/logements`)
  return reponse.data.map((dto) => ({
    idLogement: dto.id_logement,
    libelle: `${dto.libelle_zone} · ${dto.numero} · ${dto.libelle_type}`,
  }))
}
