/*
  Simulation de l'analyse et de l'import CSV des référentiels (EF-ADM-02).

  La validation reproduit ce que ferait le serveur : pour chaque cible, un jeu
  de colonnes attendues et des règles simples par colonne (présence, format
  numérique). On ne touche à aucun référentiel réel : l'import simulé se
  contente de compter les lignes valides. C'est cohérent avec la nature du
  pilote (données fictives) et suffisant pour que l'écran exerce ses états :
  aperçu, rapport d'erreurs, confirmation.

  Séparateur accepté : point-virgule ou virgule (les tableurs francophones
  exportent en général avec « ; »). La première ligne est l'en-tête et n'est
  pas importée.
*/

import type { CibleImport } from '@/features/admin/types/import-csv'
import type { LigneImportDto, RapportImportDto } from '@/features/admin/api/import-csv-dto'

type RegleColonne = {
  nom: string
  /** Valide une valeur de cellule ; retourne un motif d'erreur ou `null`. */
  valider: (valeur: string) => string | null
}

function requis(nom: string): RegleColonne {
  return {
    nom,
    valider: (valeur) => (valeur.trim() === '' ? `« ${nom} » est obligatoire` : null),
  }
}

function nombrePositif(nom: string): RegleColonne {
  return {
    nom,
    valider: (valeur) => {
      if (valeur.trim() === '') {
        return `« ${nom} » est obligatoire`
      }
      const n = Number.parseFloat(valeur.replace(',', '.'))
      if (Number.isNaN(n)) {
        return `« ${nom} » doit être un nombre`
      }
      if (n < 0) {
        return `« ${nom} » ne peut pas être négatif`
      }
      return null
    },
  }
}

/** Schéma de colonnes attendu par cible (ordre significatif). */
const SCHEMAS: Record<CibleImport, RegleColonne[]> = {
  articles: [
    requis('code'),
    requis('libelle'),
    requis('unite'),
    nombrePositif('seuil_minimal'),
    nombrePositif('seuil_critique'),
  ],
  magasins: [requis('code'), requis('libelle'), requis('chantier')],
  chantiers: [requis('code'), requis('libelle'), requis('ville')],
}

function separer(ligne: string): string[] {
  const separateur = ligne.includes(';') ? ';' : ','
  return ligne.split(separateur).map((cellule) => cellule.trim())
}

/** Analyse le contenu CSV pour une cible et produit le rapport de validation. */
export function analyserImportMock(cible: CibleImport, contenu: string): RapportImportDto {
  const regles = SCHEMAS[cible]
  const colonnes = regles.map((regle) => regle.nom)

  const lignesBrutes = contenu
    .split(/\r?\n/)
    .map((ligne) => ligne.trimEnd())
    .filter((ligne) => ligne.trim() !== '')

  // La première ligne non vide est l'en-tête : on l'ignore pour les données.
  const donnees = lignesBrutes.slice(1)

  const lignes: LigneImportDto[] = donnees.map((brute, index) => {
    const valeurs = separer(brute)
    let erreur: string | null = null

    if (valeurs.length !== regles.length) {
      erreur = `${valeurs.length} colonne(s) au lieu de ${regles.length} attendue(s)`
    } else {
      for (let i = 0; i < regles.length; i += 1) {
        const motif = regles[i]!.valider(valeurs[i] ?? '')
        if (motif) {
          erreur = motif
          break
        }
      }
    }

    return { numero: index + 1, valeurs, erreur }
  })

  const nombreErreurs = lignes.filter((ligne) => ligne.erreur !== null).length

  return {
    cible,
    colonnes,
    lignes,
    nombre_valides: lignes.length - nombreErreurs,
    nombre_erreurs: nombreErreurs,
  }
}

/** Confirme l'import : compte les lignes valides (aucune écriture réelle en simulation). */
export function confirmerImportMock(cible: CibleImport, contenu: string): number {
  return analyserImportMock(cible, contenu).nombre_valides
}
