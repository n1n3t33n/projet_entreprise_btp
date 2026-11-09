/*
  Contrats de transport du module parametrage, tels que le serveur les expose.

  Convention du projet : `snake_case`, énumérations en `UPPER_SNAKE`, décimaux
  transportés en chaîne. Rien de ce fichier ne sort du dossier `api`.

  Correspondances :
  - `ParametreChantierDto` ← MPD-2 parametre_chantier { id_parametre, cle,
    valeur, type_valeur } ; CL-2 `ParametreChantier`. Le MPD contraint
    type_valeur ∈ {ENTIER, DECIMAL, BOOLEEN, …} ; « TEXTE » complète la liste
    pour les valeurs libres (le « … » de la contrainte laisse cette ouverture).
  - `RegleValidationDto` ← MPD-3 regle_validation { id_regle, type_evenement,
    champ_teste, operateur, valeur_seuil, delai_heures }. Les littéraux de
    type_evenement et operateur sont des varchar(120) non contraints par le MPD :
    les valeurs retenues ici sont un jeu de départ, à confirmer avec le cahier.
*/

export type TypeValeurDb = 'ENTIER' | 'DECIMAL' | 'BOOLEEN' | 'TEXTE'

export type ParametreChantierDto = {
  id_parametre: string
  cle: string
  valeur: string
  type_valeur: TypeValeurDb
  libelle: string | null
}

export type RegleValidationDto = {
  id_regle: string
  type_evenement: string
  champ_teste: string
  operateur: string
  valeur_seuil: string | null
  delai_heures: number | null
}

export type ParametreChantierCorps = {
  cle: string
  valeur: string
  type_valeur: TypeValeurDb
  libelle: string | null
}

export type RegleValidationCorps = {
  type_evenement: string
  champ_teste: string
  operateur: string
  valeur_seuil: string | null
  delai_heures: number | null
}
