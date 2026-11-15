import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../core/securite/empreinte_pin.dart';
import '../data/depot_session.dart';
import '../data/service_auth.dart';
import '../domain/etat_auth.dart';
import '../domain/profil_utilisateur.dart';
import '../domain/verrou_session.dart';

/// Contrôleur d'authentification mobile (EF-AUT-03).
///
/// Enchaîne : connexion en ligne → définition du PIN → déverrouillage
/// hors-ligne (valide 14 jours, AC-1/ET-4) → révocation côté client (SQ-5).
class ControleurAuth extends Notifier<EtatAuth> {
  @override
  EtatAuth build() => const AuthInitial();

  /// Décide de l'état de départ selon la session locale et le verrou 14 jours.
  ///
  /// Une erreur d'ouverture des données n'est jamais avalée : on bascule sur
  /// l'écran de connexion avec son motif, plutôt que de rester en chargement.
  Future<void> initialiser() async {
    try {
      final session = await ref.read(depotSessionProvider).lire();
      if (session == null) {
        state = const AuthNonConnecte();
        return;
      }
      state = _etatVerrouille(session);
    } on Object {
      state = const AuthNonConnecte(motif: MotifConnexion.donneesInaccessibles);
    }
  }

  EtatAuth _etatVerrouille(SessionEnregistree session) {
    final role = RoleTerrain.parCode(session.roleCode);
    if (role == null) {
      return const AuthNonConnecte(motif: MotifConnexion.sansAccesTerrain);
    }
    if (verrouExpire(session.derniereConnexionEnLigne, DateTime.now())) {
      return const AuthNonConnecte(motif: MotifConnexion.sessionExpiree);
    }
    return AuthVerrouille(
      profil: session.profil,
      role: role,
      derniereConnexion: session.derniereConnexionEnLigne,
    );
  }

  /// Première connexion (ou reconnexion après expiration), en ligne.
  Future<void> connexionEnLigne(String identifiant, String motDePasse) async {
    try {
      final session = await ref
          .read(serviceAuthProvider)
          .connexion(identifiant, motDePasse);
      if (RoleTerrain.parCode(session.utilisateur.roleCodeRole) == null) {
        state = const AuthNonConnecte(motif: MotifConnexion.sansAccesTerrain);
        return;
      }
      state = AuthEnrolementPin(session);
    } on EchecConnexionException catch (e) {
      state = AuthNonConnecte(
        motif: MotifConnexion.depuisServeur(e.echec.motif),
        secondesRestantes: e.echec.secondesRestantes,
      );
    }
  }

  /// Abandonne l'enrôlement et revient à l'écran de connexion.
  void annulerEnrolement() {
    if (state is AuthEnrolementPin) state = const AuthNonConnecte();
  }

  /// Définit le PIN local après une connexion en ligne réussie.
  Future<void> definirPin(String pin) async {
    final courant = state;
    if (courant is! AuthEnrolementPin) return;

    final utilisateur = courant.session.utilisateur;
    final role = RoleTerrain.parCode(utilisateur.roleCodeRole);
    if (role == null) {
      state = const AuthNonConnecte(motif: MotifConnexion.sansAccesTerrain);
      return;
    }

    final sel = EmpreintePin.genererSel();
    final empreinte = await EmpreintePin.hacher(pin, sel);
    final profil = ProfilUtilisateur(
      idUtilisateur: utilisateur.idUtilisateur,
      identifiant: utilisateur.identifiant,
      prenom: utilisateur.prenom,
      nom: utilisateur.nom,
      fonction: utilisateur.fonction,
      perimetre: utilisateur.libellePerimetre,
    );

    await ref.read(coffreProvider).ecrireJeton(courant.session.jeton);
    await ref
        .read(depotSessionProvider)
        .enregistrer(
          SessionEnregistree(
            profil: profil,
            roleCode: role.code,
            pinHashLocal: empreinte,
            pinSel: sel,
            derniereConnexionEnLigne: DateTime.now(),
          ),
        );

    state = AuthDeverrouille(profil: profil, role: role);
  }

  /// Vérifie un PIN sans changer l'état : sert à signer une validation
  /// (approbation d'une sortie, visa d'une étape).
  Future<bool> verifierPin(String pin) async {
    final session = await ref.read(depotSessionProvider).lire();
    if (session == null) return false;
    return EmpreintePin.verifier(pin, session.pinSel, session.pinHashLocal);
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

    final suivant = _etatVerrouille(session);
    if (suivant is! AuthVerrouille) {
      state = suivant;
      return false;
    }
    state = AuthDeverrouille(profil: suivant.profil, role: suivant.role);
    return true;
  }

  /// Verrouille sans déconnecter (retour à l'écran PIN).
  Future<void> verrouiller() async {
    final courant = state;
    if (courant is! AuthDeverrouille) return;
    final session = await ref.read(depotSessionProvider).lire();
    state = AuthVerrouille(
      profil: courant.profil,
      role: courant.role,
      derniereConnexion: session?.derniereConnexionEnLigne,
    );
  }

  /// Retire le compte de cet appareil : efface les données locales et le jeton
  /// (SQ-5). La clé de la base est conservée : elle protège un fichier
  /// désormais vide et reste nécessaire pour le rouvrir.
  Future<void> revoquer() async {
    await ref.read(depotSessionProvider).effacerTout();
    await ref.read(coffreProvider).effacerJeton();
    ref.invalidate(fileEnvoiProvider);
    state = const AuthNonConnecte(motif: MotifConnexion.sessionRevoquee);
  }
}
