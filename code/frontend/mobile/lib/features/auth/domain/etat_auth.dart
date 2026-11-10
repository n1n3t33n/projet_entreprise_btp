import '../../../core/roles/role_terrain.dart';
import '../data/dto_auth.dart';

/// États possibles de l'authentification mobile (EF-AUT-03).
///
/// Hiérarchie scellée : le routeur et l'interface réagissent par `switch`
/// exhaustif, sans cas par défaut.
sealed class EtatAuth {
  const EtatAuth();
}

/// Amorçage : on ne sait pas encore s'il existe une session locale.
final class AuthInitial extends EtatAuth {
  const AuthInitial();
}

/// Aucune session locale : connexion en ligne requise.
final class AuthNonConnecte extends EtatAuth {
  const AuthNonConnecte({this.message});

  final String? message;
}

/// Connexion en ligne réussie : l'utilisateur doit définir son PIN local.
final class AuthEnrolementPin extends EtatAuth {
  const AuthEnrolementPin(this.session);

  final SessionDto session;
}

/// Session locale présente et valide : déverrouillage par PIN attendu.
final class AuthVerrouille extends EtatAuth {
  const AuthVerrouille(this.identifiant);

  final String identifiant;
}

/// Session locale dépassant 14 jours : reconnexion en ligne obligatoire.
final class AuthVerrouExpire extends EtatAuth {
  const AuthVerrouExpire(this.identifiant);

  final String identifiant;
}

/// Accès ouvert : rôle connu, navigation autorisée.
final class AuthDeverrouille extends EtatAuth {
  const AuthDeverrouille({required this.identifiant, required this.role});

  final String identifiant;
  final RoleTerrain role;
}
