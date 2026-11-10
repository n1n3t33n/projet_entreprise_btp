import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../core/securite/empreinte_pin.dart';
import '../data/service_auth.dart';
import '../domain/etat_auth.dart';
import '../domain/verrou_session.dart';

/// Contrôleur d'authentification mobile (EF-AUT-03).
///
/// Enchaîne : connexion en ligne → définition du PIN → déverrouillage
/// hors-ligne (valide 14 jours, AC-1/ET-4) → révocation côté client (SQ-5).
class ControleurAuth extends Notifier<EtatAuth> {
  @override
  EtatAuth build() => const AuthInitial();

  static const _messageSansAccesTerrain =
      "Ce compte n'a pas d'accès terrain sur l'application mobile.";

  /// Décide de l'état de départ selon la session locale et le verrou 14 jours.
  Future<void> initialiser() async {
    final session = await ref.read(depotSessionProvider).lire();
    if (session == null) {
      state = const AuthNonConnecte();
      return;
    }
    if (verrouExpire(session.derniereConnexionEnLigne, DateTime.now())) {
      state = AuthVerrouExpire(session.identifiant);
    } else {
      state = AuthVerrouille(session.identifiant);
    }
  }

  /// Première connexion (ou reconnexion après expiration), en ligne.
  Future<void> connexionEnLigne(String identifiant, String motDePasse) async {
    try {
      final session = await ref
          .read(serviceAuthProvider)
          .connexion(identifiant, motDePasse);
      if (RoleTerrain.parCode(session.utilisateur.roleCodeRole) == null) {
        state = const AuthNonConnecte(message: _messageSansAccesTerrain);
        return;
      }
      state = AuthEnrolementPin(session);
    } on EchecConnexionException catch (e) {
      state = AuthNonConnecte(message: e.echec.message);
    }
  }

  /// Définit le PIN local après une connexion en ligne réussie.
  Future<void> definirPin(String pin) async {
    final courant = state;
    if (courant is! AuthEnrolementPin) return;

    final session = courant.session;
    final role = RoleTerrain.parCode(session.utilisateur.roleCodeRole);
    if (role == null) {
      state = const AuthNonConnecte(message: _messageSansAccesTerrain);
      return;
    }

    final sel = EmpreintePin.genererSel();
    final empreinte = await EmpreintePin.hacher(pin, sel);

    await ref.read(coffreProvider).ecrireJeton(session.jeton);
    await ref
        .read(depotSessionProvider)
        .enregistrer(
          identifiant: session.utilisateur.identifiant,
          roleCode: role.code,
          pinHashLocal: empreinte,
          pinSel: sel,
          derniereConnexion: DateTime.now(),
        );

    state = AuthDeverrouille(
      identifiant: session.utilisateur.identifiant,
      role: role,
    );
  }

  /// Déverrouille hors-ligne par PIN. Renvoie `false` si le PIN est faux
  /// (l'état ne change pas) ; bascule en expiré si le verrou a dépassé 14 jours.
  Future<bool> deverrouiller(String pin) async {
    final session = await ref.read(depotSessionProvider).lire();
    if (session == null) {
      state = const AuthNonConnecte();
      return false;
    }

    final correct = await EmpreintePin.verifier(
      pin,
      session.pinSel,
      session.pinHashLocal,
    );
    if (!correct) return false;

    if (verrouExpire(session.derniereConnexionEnLigne, DateTime.now())) {
      state = AuthVerrouExpire(session.identifiant);
      return false;
    }

    final role = RoleTerrain.parCode(session.roleCode);
    if (role == null) {
      state = const AuthNonConnecte(message: _messageSansAccesTerrain);
      return false;
    }

    state = AuthDeverrouille(identifiant: session.identifiant, role: role);
    return true;
  }

  /// Verrouille sans déconnecter (retour à l'écran PIN).
  void verrouiller() {
    final courant = state;
    if (courant is AuthDeverrouille) {
      state = AuthVerrouille(courant.identifiant);
    }
  }

  /// Révoque la session sur cet appareil : efface la base et le coffre (SQ-5).
  Future<void> revoquer() async {
    await ref.read(depotSessionProvider).effacer();
    await ref.read(coffreProvider).vider();
    state = const AuthNonConnecte(
      message: 'Session révoquée sur cet appareil.',
    );
  }
}
