/*
  Vues d'affichage et saisies du module référentiels.

  Une « vue » enrichit une entité du domaine avec les libellés résolus dont un
  écran a besoin (le libellé d'une catégorie, d'un chantier), sans que l'écran
  n'ait à croiser lui-même les référentiels. Une « saisie » décrit la charge
  utile d'une création ou d'une modification, telle que la remplit un
  formulaire, avant l'appel d'API.
*/

import type {
  Article,
  Chantier,
  Logement,
  Magasin,
  Zone,
} from '@/features/referentiels/types/domaine'
import type {
  OrigineArticle,
  StatutChantier,
  StatutLogement,
  TypeZone,
} from '@/features/referentiels/types/enums'

/* ----------------------------- Vues catalogue ----------------------------- */

/** Article enrichi des libellés de sa catégorie et de son unité. */
export type ArticleVue = Article & {
  libelleCategorie: string
  libelleUnite: string
}

/* ------------------------------ Vues magasins ----------------------------- */

/** Magasin enrichi du nom de son chantier de rattachement. */
export type MagasinVue = Magasin & {
  libelleChantier: string
}

/* -------------------------- Vues chantiers & zones ------------------------- */

/** Logement enrichi du libellé et de la surface de son type. */
export type LogementVue = Logement & {
  libelleType: string
  surfaceReference: number
}

/** Zone et ses logements, pour l'arbre de structure. */
export type ZoneArbre = {
  zone: Zone
  logements: LogementVue[]
}

/** Chantier, ses zones et leurs logements : l'arbre complet d'un chantier. */
export type ChantierArbre = {
  chantier: Chantier
  zones: ZoneArbre[]
}

/* -------------------------------- Saisies --------------------------------- */

/** Création ou modification d'un article (le formulaire du catalogue). */
export type SaisieArticle = {
  code: string
  designation: string
  origine: OrigineArticle
  codeBarre: string | null
  actif: boolean
  codeCategorie: string
  codeUnite: string
}

/** Création ou modification d'un magasin. */
export type SaisieMagasin = {
  code: string
  nom: string
  actif: boolean
  idChantier: string
}

/** Modification des informations d'un chantier. */
export type SaisieChantier = {
  code: string
  nom: string
  programme: string
  dateDebut: string
  statut: StatutChantier
}

/** Création ou modification d'une zone rattachée à un chantier. */
export type SaisieZone = {
  code: string
  nom: string
  typeZone: TypeZone
  idChantier: string
}

/** Création ou modification d'un logement rattaché à une zone. */
export type SaisieLogement = {
  numero: string
  statut: StatutLogement
  dateLivraisonPrevue: string | null
  idZone: string
  codeTypeLogement: string
}
