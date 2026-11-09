/*
  Types du domaine « import CSV des référentiels » (EF-ADM-02, UC-4
  « Importer les données initiales en CSV », acteur Administrateur).

  NOTE SUR LA RÉFÉRENCE DE L'EXIGENCE : le backlog de l'étape 11 citait cet
  import sous le code EF-REF-10. La source de modélisation (UC-4) le rattache à
  l'acteur Administrateur sous le code EF-ADM-02. On retient le code du modèle,
  EF-ADM-02 ; EF-REF-10 était une référence croisée du cahier côté
  référentiels. Décision prise avec le porteur du projet.

  L'import se fait en deux temps, pour qu'une erreur de fichier ne touche jamais
  les données : d'abord une ANALYSE qui valide le contenu ligne par ligne et
  renvoie un rapport (lignes valides, lignes en erreur avec leur motif), ensuite
  une CONFIRMATION qui applique uniquement si l'analyse est exploitable. Ce
  découpage reprend la prudence du cahier : les données initiales sont
  importées une fois, leur contrôle doit être lisible avant d'écrire.
*/

/** Référentiel ciblé par un import. */
export type CibleImport = 'articles' | 'magasins' | 'chantiers'

/** Résultat de l'analyse d'une ligne du CSV. */
export type LigneImport = {
  /** Numéro de ligne dans le fichier (1 = première ligne de données, en-tête exclu). */
  numero: number
  /** Valeurs de la ligne, dans l'ordre des colonnes attendues. */
  valeurs: string[]
  /** Motif d'erreur, ou `null` si la ligne est valide. */
  erreur: string | null
}

/** Rapport d'analyse d'un fichier CSV avant import. */
export type RapportImport = {
  cible: CibleImport
  /** Colonnes attendues pour cette cible, dans l'ordre. */
  colonnes: string[]
  lignes: LigneImport[]
  nombreValides: number
  nombreErreurs: number
}

/** Résultat d'un import confirmé. */
export type ResultatImport = {
  cible: CibleImport
  nombreImportees: number
}
