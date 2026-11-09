/*
  Appels réseau de l'import CSV des référentiels (EF-ADM-02).

  Deux appels, qui reprennent le découpage en deux temps du domaine :
  - `analyserImport` envoie le texte brut et la cible, reçoit un rapport
    (validation ligne par ligne) sans rien écrire ;
  - `confirmerImport` applique l'import après que l'administrateur a vu le
    rapport. Le serveur journalise l'import (EF-AUT-08).
*/

import { http } from '@/lib/api/http'
import type {
  RapportImportDto,
  ResultatImportDto,
} from '@/features/admin/api/import-csv-dto'
import type {
  CibleImport,
  RapportImport,
  ResultatImport,
} from '@/features/admin/types/import-csv'

function mapperRapport(dto: RapportImportDto): RapportImport {
  return {
    cible: dto.cible,
    colonnes: dto.colonnes,
    lignes: dto.lignes.map((ligne) => ({
      numero: ligne.numero,
      valeurs: ligne.valeurs,
      erreur: ligne.erreur,
    })),
    nombreValides: dto.nombre_valides,
    nombreErreurs: dto.nombre_erreurs,
  }
}

/** Analyse un fichier CSV sans rien écrire (EF-ADM-02, premier temps). */
export async function analyserImport(cible: CibleImport, contenu: string): Promise<RapportImport> {
  const reponse = await http.post<RapportImportDto>('/import/analyse', { cible, contenu })
  return mapperRapport(reponse.data)
}

/** Confirme un import après analyse (EF-ADM-02, second temps). */
export async function confirmerImport(cible: CibleImport, contenu: string): Promise<ResultatImport> {
  const reponse = await http.post<ResultatImportDto>('/import/confirmation', { cible, contenu })
  return { cible: reponse.data.cible, nombreImportees: reponse.data.nombre_importees }
}
