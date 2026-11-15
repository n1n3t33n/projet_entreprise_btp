import '../../../core/roles/role_terrain.dart';
import '../data/dto_auth.dart';
import 'profil_utilisateur.dart';

/// Raison affichée sur l'écran de connexion. C'est un code, pas un texte :
/// l'écran le traduit dans la langue de l'utilisateur.
enum MotifConnexion {
  identifiants,
  compteInactif,
  verrouille,
  sansAccesTerrain,
  sessionRevoquee,
  sessionExpiree,
  donneesInaccessibles,
  connexionImpossible;

  /// Traduit le motif renvoyé par le serveur (`UPPER_SNAKE`).
  static MotifConnexion depuisServeur(String code) => switch (code) {
    'COMPTE_INACTIF' => MotifConnexion.compteInactif,
    'VERROUILLE' => MotifConnexion.verrouille,
    'RESEAU' => MotifConnexion.connexionImpossible,
    _ => MotifConnexion.identifiants,
  };
}

/// États possibles de l'authentification mobile (EF-AUT-03).
///
/// Hiérarchie scellée : l'interface réagit par `switch` exhaustif.
sealed class EtatAuth {
  const EtatAuth();
}

/// Amorçage : on ne sait pas encore s'il existe une session locale.
final class AuthInitial extends EtatAuth {
  const AuthInitial();
}

/// Aucune session locale utilisable : connexion en ligne requise.
final class AuthNonConnecte extends EtatAuth {
  const AuthNonConnecte({this.motif, this.secondesRestantes});

  final MotifConnexion? motif;

  /// Durée du verrouillage temporaire, si le compte est verrouillé.
  final int? secondesRestantes;
}

/// Connexion en ligne réussie : l'utilisateur doit définir son PIN local.
final class AuthEnrolementPin extends EtatAuth {
  const AuthEnrolementPin(this.session);

  final SessionDto session;
}

/// Session locale présente et valide : déverrouillage par PIN attendu.
final class AuthVerrouille extends EtatAuth {
  const AuthVerrouille({
    required this.profil,
    required this.role,
    this.derniereConnexion,
  });

  final ProfilUtilisateur profil;
  final RoleTerrain role;
  final DateTime? derniereConnexion;
}

/// Accès ouvert : rôle connu, navigation autorisée.
final class AuthDeverrouille extends EtatAuth {
  const AuthDeverrouille({required this.profil, required this.role});

  final ProfilUtilisateur profil;
  final RoleTerrain role;
}
