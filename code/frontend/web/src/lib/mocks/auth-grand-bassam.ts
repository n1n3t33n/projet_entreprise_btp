/*
  Données de démonstration des comptes et de la connexion (CL-1 `Utilisateur`,
  `AffectationRole`, `Perimetre`).

  Cinq comptes nominatifs, un par rôle du poste de pilotage, chacun rattaché à
  un périmètre (EF-AUT-02). La connexion applique le verrouillage temporaire
  après échecs répétés exigé par EF-AUT-04.

  SÉCURITÉ : ce fichier compare un mot de passe en clair, ce qu'un vrai serveur
  ne fait jamais — le cahier des charges impose des mots de passe hachés et une
  limitation des tentatives côté serveur. Il s'agit d'un jeu d'essai local,
  servi uniquement quand la simulation est active ; le mot de passe est commun
  aux cinq comptes et sans valeur hors de cette démonstration.
*/

import type {
  EchecConnexionDto,
  PerimetreDto,
  SessionDto,
  UtilisateurDto,
} from '@/features/auth/api/dto'

/** Mot de passe unique des comptes de démonstration. */
export const MOT_DE_PASSE_DEMONSTRATION = 'Chantier2026!'

/** Nombre d'échecs tolérés avant verrouillage, et durée du verrou (EF-AUT-04). */
const ECHECS_AVANT_VERROU = 5
const DUREE_VERROU_SECONDES = 60

const PERIMETRES: PerimetreDto[] = [
  { id_perimetre: 'PER-PROG', libelle: 'Tout le programme' },
  { id_perimetre: 'PER-CH-GB', libelle: 'Chantier de Grand-Bassam' },
  { id_perimetre: 'PER-MAG-GB', libelle: 'Magasin central de Grand-Bassam' },
  { id_perimetre: 'PER-LOG-A01', libelle: 'Logement A01' },
]

const COMPTES: UtilisateurDto[] = [
  {
    id_utilisateur: 'USR-001',
    identifiant: 'a.kouassi',
    nom: 'Kouassi',
    prenom: 'Affoué',
    fonction: 'Associée, direction générale',
    statut: 'ACTIF',
    date_creation: '2026-09-01',
    role_code_role: 'direction',
    perimetre_id_perimetre: 'PER-PROG',
    libelle_perimetre: 'Tout le programme',
  },
  {
    id_utilisateur: 'USR-002',
    identifiant: 'y.bamba',
    nom: 'Bamba',
    prenom: 'Yacouba',
    fonction: 'Administrateur du système',
    statut: 'ACTIF',
    date_creation: '2026-09-01',
    role_code_role: 'administrateur',
    perimetre_id_perimetre: 'PER-PROG',
    libelle_perimetre: 'Tout le programme',
  },
  {
    id_utilisateur: 'USR-003',
    identifiant: 'k.n-guessan',
    nom: "N'Guessan",
    prenom: 'Koffi',
    fonction: 'Conducteur de travaux',
    statut: 'ACTIF',
    date_creation: '2026-09-05',
    role_code_role: 'responsable_technique',
    perimetre_id_perimetre: 'PER-CH-GB',
    libelle_perimetre: 'Chantier de Grand-Bassam',
  },
  {
    id_utilisateur: 'USR-004',
    identifiant: 's.traore',
    nom: 'Traoré',
    prenom: 'Salimata',
    fonction: 'Chargée de clientèle',
    statut: 'ACTIF',
    date_creation: '2026-09-12',
    role_code_role: 'commercial',
    perimetre_id_perimetre: 'PER-CH-GB',
    libelle_perimetre: 'Chantier de Grand-Bassam',
  },
  {
    id_utilisateur: 'USR-005',
    identifiant: 'm.diallo',
    nom: 'Diallo',
    prenom: 'Mariam',
    fonction: 'Acquéreuse',
    statut: 'ACTIF',
    date_creation: '2026-10-02',
    role_code_role: 'acquereur',
    perimetre_id_perimetre: 'PER-LOG-A01',
    libelle_perimetre: 'Logement A01',
  },
]

/** Tentatives échouées par identifiant, pour le verrouillage temporaire. */
const tentatives = new Map<string, { echecs: number; verrouJusqua: number }>()

let compteurId = COMPTES.length

export function listerPerimetres(): PerimetreDto[] {
  return PERIMETRES
}

export function listerComptes(): UtilisateurDto[] {
  return COMPTES
}

function libellePerimetre(id: string): string {
  return PERIMETRES.find((p) => p.id_perimetre === id)?.libelle ?? ''
}

function texte(valeur: unknown): string {
  return typeof valeur === 'string' ? valeur : ''
}

export type ResultatConnexion =
  { ok: true; session: SessionDto } | { ok: false; statut: number; echec: EchecConnexionDto }

/** Vérifie les identifiants et applique le verrouillage temporaire. */
export function tenterConnexion(corps: Record<string, unknown>): ResultatConnexion {
  const identifiant = texte(corps.identifiant).trim().toLowerCase()
  const motDePasse = texte(corps.mot_de_passe)
  const maintenant = Date.now()
  const suivi = tentatives.get(identifiant) ?? { echecs: 0, verrouJusqua: 0 }

  if (suivi.verrouJusqua > maintenant) {
    return {
      ok: false,
      statut: 429,
      echec: {
        motif: 'VERROUILLE',
        message: 'Trop de tentatives. Le compte est temporairement verrouillé.',
        secondes_restantes: Math.ceil((suivi.verrouJusqua - maintenant) / 1000),
      },
    }
  }

  const compte = COMPTES.find((c) => c.identifiant.toLowerCase() === identifiant)

  if (!compte || motDePasse !== MOT_DE_PASSE_DEMONSTRATION) {
    suivi.echecs += 1

    if (suivi.echecs >= ECHECS_AVANT_VERROU) {
      // Le verrou est annoncé dès la tentative qui le déclenche : laisser
      // l'utilisateur croire à une simple erreur de saisie, puis le bloquer
      // sans explication, serait incompréhensible.
      suivi.echecs = 0
      suivi.verrouJusqua = maintenant + DUREE_VERROU_SECONDES * 1000
      tentatives.set(identifiant, suivi)
      return {
        ok: false,
        statut: 429,
        echec: {
          motif: 'VERROUILLE',
          message: 'Trop de tentatives. Le compte est temporairement verrouillé.',
          secondes_restantes: DUREE_VERROU_SECONDES,
        },
      }
    }

    tentatives.set(identifiant, suivi)
    // Même message qu'un identifiant inconnu : ne pas révéler quels comptes existent.
    return {
      ok: false,
      statut: 401,
      echec: { motif: 'IDENTIFIANTS', message: 'Identifiant ou mot de passe incorrect.' },
    }
  }

  if (compte.statut !== 'ACTIF') {
    return {
      ok: false,
      statut: 403,
      echec: {
        motif: 'COMPTE_INACTIF',
        message: 'Ce compte est désactivé. Contactez un administrateur.',
      },
    }
  }

  tentatives.delete(identifiant)
  return {
    ok: true,
    session: { jeton: `JETON-${compte.id_utilisateur}-${maintenant}`, utilisateur: compte },
  }
}

export function creerCompteMock(corps: Record<string, unknown>): UtilisateurDto {
  compteurId += 1
  const idPerimetre = texte(corps.perimetre_id_perimetre)
  const compte: UtilisateurDto = {
    id_utilisateur: `USR-${String(compteurId).padStart(3, '0')}`,
    identifiant: texte(corps.identifiant),
    nom: texte(corps.nom),
    prenom: texte(corps.prenom),
    fonction: texte(corps.fonction),
    statut: texte(corps.statut) === 'INACTIF' ? 'INACTIF' : 'ACTIF',
    date_creation: new Date().toISOString().slice(0, 10),
    role_code_role: texte(corps.role_code_role),
    perimetre_id_perimetre: idPerimetre,
    libelle_perimetre: libellePerimetre(idPerimetre),
  }
  COMPTES.push(compte)
  return compte
}

export function modifierCompteMock(
  id: string,
  corps: Record<string, unknown>,
): UtilisateurDto | undefined {
  const compte = COMPTES.find((c) => c.id_utilisateur === id)
  if (!compte) {
    return undefined
  }
  compte.identifiant = texte(corps.identifiant)
  compte.nom = texte(corps.nom)
  compte.prenom = texte(corps.prenom)
  compte.fonction = texte(corps.fonction)
  compte.statut = texte(corps.statut) === 'INACTIF' ? 'INACTIF' : 'ACTIF'
  compte.role_code_role = texte(corps.role_code_role)
  compte.perimetre_id_perimetre = texte(corps.perimetre_id_perimetre)
  compte.libelle_perimetre = libellePerimetre(compte.perimetre_id_perimetre)
  return compte
}
