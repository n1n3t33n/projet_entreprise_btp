/*
  Appels réseau du module stock, sur le client axios partagé (`lib/api/http`).

  Chaque fonction renvoie des types du domaine : la forme serveur (dto) ne
  franchit pas cette couche. L'adaptateur de simulation (`lib/mocks`) se branche
  sur le même client ; ces fonctions ne savent pas si elles parlent à l'API
  réelle ou aux données de démonstration.
*/

import { http } from '@/lib/api/http'
import type {
  LigneStock,
  MouvementStock,
  SaisieEntree,
  SaisieSortie,
  TypeMouvement,
} from '@/features/stock/types'
import type { LigneStockDto, MouvementStockDto, TypeMouvementDto } from '@/features/stock/api/dto'
import {
  mapperLigneStock,
  mapperMouvement,
  mapperTypeMouvement,
} from '@/features/stock/api/mapping'

/** Formate une quantité pour l'envoi : chaîne à trois décimales (numeric(14,3)). */
function quantiteVersChaine(valeur: number): string {
  return valeur.toFixed(3)
}

/** Stock d'un magasin : une ligne par article (EF-STK-05). */
export async function listerStockMagasin(idMagasin: string): Promise<LigneStock[]> {
  const reponse = await http.get<LigneStockDto[]>(`/magasins/${idMagasin}/stock`)
  return reponse.data.map((ligne) => mapperLigneStock(ligne, idMagasin))
}

/** Historique des mouvements d'un article dans un magasin (EF-STK-10). */
export async function listerMouvementsArticle(
  idMagasin: string,
  idArticle: string,
): Promise<MouvementStock[]> {
  const reponse = await http.get<MouvementStockDto[]>(
    `/magasins/${idMagasin}/articles/${idArticle}/mouvements`,
  )
  return reponse.data.map(mapperMouvement)
}

/** Types de mouvement disponibles (référentiel). */
export async function listerTypesMouvement(): Promise<TypeMouvement[]> {
  const reponse = await http.get<TypeMouvementDto[]>('/types-mouvement')
  return reponse.data.map(mapperTypeMouvement)
}

/** Enregistre une entrée — réception (EF-STK-02). */
export async function enregistrerEntree(saisie: SaisieEntree): Promise<MouvementStock> {
  const reponse = await http.post<MouvementStockDto>('/mouvements', {
    magasin_id_magasin: saisie.idMagasin,
    article_id_article: saisie.idArticle,
    type_mouvement_code_type_mouvement: saisie.codeTypeMouvement,
    quantite_saisie: quantiteVersChaine(saisie.quantite),
    code_unite: saisie.codeUnite,
    reference_externe: saisie.referenceExterne,
  })
  return mapperMouvement(reponse.data)
}

/** Enregistre une sortie vers un logement (EF-STK-01). */
export async function enregistrerSortie(saisie: SaisieSortie): Promise<MouvementStock> {
  const reponse = await http.post<MouvementStockDto>('/mouvements', {
    magasin_id_magasin: saisie.idMagasin,
    article_id_article: saisie.idArticle,
    type_mouvement_code_type_mouvement: saisie.codeTypeMouvement,
    quantite_saisie: quantiteVersChaine(saisie.quantite),
    code_unite: saisie.codeUnite,
    logement_id_logement: saisie.idLogement,
    corps_etat: saisie.corpsEtat,
    beneficiaire: saisie.beneficiaire,
    motif: saisie.motif,
  })
  return mapperMouvement(reponse.data)
}

/** Définit les seuils d'un article dans un magasin (EF-STK-06). */
export async function definirSeuils(
  idMagasin: string,
  idArticle: string,
  seuils: { seuilMinimal: number; seuilCritique: number },
): Promise<void> {
  await http.put(`/magasins/${idMagasin}/articles/${idArticle}/seuil`, {
    seuil_minimal: quantiteVersChaine(seuils.seuilMinimal),
    seuil_critique: quantiteVersChaine(seuils.seuilCritique),
  })
}
