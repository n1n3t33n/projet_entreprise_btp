/*
  Appels réseau de la connexion et des comptes.

  La couche traduit les erreurs HTTP de connexion en un échec typé
  (`EchecConnexion`) plutôt qu'en exception brute : l'écran doit distinguer un
  mot de passe erroné d'un compte désactivé ou d'un verrouillage temporaire
  (EF-AUT-04), et afficher l'attente restante.
*/

import axios from 'axios'
import { http } from '@/lib/api/http'
import { ROLES, type Role } from '@/app/role-context'
import type {
  EchecConnexion,
  IdentifiantsConnexion,
  Perimetre,
  SaisieCompte,
  Session,
  StatutCompte,
  Utilisateur,
} from '@/features/auth/types/domaine'
import type {
  EchecConnexionDto,
  PerimetreDto,
  SessionDto,
  UtilisateurDto,
} from '@/features/auth/api/dto'

/** Erreur de connexion portant le motif qualifié par le serveur. */
export class ErreurConnexion extends Error {
  readonly echec: EchecConnexion

  constructor(echec: EchecConnexion) {
    super(echec.message)
    this.name = 'ErreurConnexion'
    this.echec = echec
  }
}

function estRole(valeur: string): valeur is Role {
  return ROLES.some((item) => item.value === valeur)
}

function statutDepuisDb(valeur: string): StatutCompte {
  return valeur === 'INACTIF' ? 'inactif' : 'actif'
}

export function mapperUtilisateur(dto: UtilisateurDto): Utilisateur {
  return {
    id: dto.id_utilisateur,
    identifiant: dto.identifiant,
    nom: dto.nom,
    prenom: dto.prenom,
    fonction: dto.fonction,
    statut: statutDepuisDb(dto.statut),
    dateCreation: dto.date_creation,
    // Un rôle inconnu du poste de pilotage ne doit pas ouvrir de session :
    // on retombe sur le rôle le plus restreint plutôt que d'élargir des accès.
    role: estRole(dto.role_code_role) ? dto.role_code_role : 'acquereur',
    idPerimetre: dto.perimetre_id_perimetre,
    libellePerimetre: dto.libelle_perimetre,
  }
}

function corpsSaisie(saisie: SaisieCompte): Record<string, unknown> {
  return {
    identifiant: saisie.identifiant,
    nom: saisie.nom,
    prenom: saisie.prenom,
    fonction: saisie.fonction,
    statut: saisie.statut.toUpperCase(),
    role_code_role: saisie.role,
    perimetre_id_perimetre: saisie.idPerimetre,
  }
}

const MOTIFS: Record<string, EchecConnexion['motif']> = {
  IDENTIFIANTS: 'identifiants',
  COMPTE_INACTIF: 'compte_inactif',
  VERROUILLE: 'verrouille',
}

/** Ouvre une session (EF-AUT-04). Lève `ErreurConnexion` en cas d'échec. */
export async function seConnecter(identifiants: IdentifiantsConnexion): Promise<Session> {
  try {
    const reponse = await http.post<SessionDto>('/auth/connexion', {
      identifiant: identifiants.identifiant,
      mot_de_passe: identifiants.motDePasse,
    })
    return { jeton: reponse.data.jeton, utilisateur: mapperUtilisateur(reponse.data.utilisateur) }
  } catch (erreur) {
    // `isAxiosError` plutôt qu'un `instanceof` : l'adaptateur de simulation
    // rejette avec un objet porteur du drapeau, sans être une instance.
    const donnees = axios.isAxiosError(erreur)
      ? (erreur.response?.data as EchecConnexionDto | undefined)
      : undefined

    if (donnees?.motif) {
      throw new ErreurConnexion({
        motif: MOTIFS[donnees.motif] ?? 'identifiants',
        message: donnees.message,
        secondesRestantes: donnees.secondes_restantes,
      })
    }
    throw new ErreurConnexion({
      motif: 'identifiants',
      message: 'La connexion a échoué. Réessayez dans un instant.',
    })
  }
}

/** Ferme la session côté serveur. L'échec n'empêche pas la déconnexion locale. */
export async function seDeconnecter(): Promise<void> {
  await http.post('/auth/deconnexion', {})
}

/* ----------------------------- Comptes (EF-AUT-01/02) --------------------- */

export async function listerComptes(): Promise<Utilisateur[]> {
  const reponse = await http.get<UtilisateurDto[]>('/auth/comptes')
  return reponse.data.map(mapperUtilisateur)
}

export async function listerPerimetres(): Promise<Perimetre[]> {
  const reponse = await http.get<PerimetreDto[]>('/auth/perimetres')
  return reponse.data.map((dto) => ({ id: dto.id_perimetre, libelle: dto.libelle }))
}

export async function creerCompte(saisie: SaisieCompte): Promise<void> {
  await http.post('/auth/comptes', corpsSaisie(saisie))
}

export async function modifierCompte(id: string, saisie: SaisieCompte): Promise<void> {
  await http.put(`/auth/comptes/${id}`, corpsSaisie(saisie))
}
