import 'package:drift/drift.dart';

import '../../../core/db/base_locale.dart';
import '../../../core/stockage/magasin_documents.dart';
import '../domain/profil_utilisateur.dart';

/// Session conservée sur l'appareil : empreinte du PIN, rôle, profil et date
/// de la dernière connexion en ligne (ancre du verrou de 14 jours).
class SessionEnregistree {
  const SessionEnregistree({
    required this.profil,
    required this.roleCode,
    required this.pinHashLocal,
    required this.pinSel,
    required this.derniereConnexionEnLigne,
  });

  final ProfilUtilisateur profil;
  final String roleCode;
  final String pinHashLocal;
  final String pinSel;
  final DateTime derniereConnexionEnLigne;
}

/// Persistance de la session locale. Le pilote fonctionne avec une seule
/// session active par appareil.
abstract interface class DepotSession {
  Future<SessionEnregistree?> lire();

  Future<void> enregistrer(SessionEnregistree session);

  /// Efface la session et toutes les données locales (révocation, SQ-5).
  Future<void> effacerTout();
}

/// Implémentation sur la base chiffrée : la ligne `session_locale` porte les
/// éléments de sécurité, le profil affichable est rangé avec les documents.
class DepotSessionDrift implements DepotSession {
  const DepotSessionDrift(this._base, this._documents);

  final BaseLocale _base;
  final MagasinDocuments _documents;

  static const String _idSession = 'session-courante';
  static const String _typeProfil = 'profil';
  static const String _cleProfil = 'courant';

  @override
  Future<SessionEnregistree?> lire() async {
    final ligne = await (_base.select(
      _base.sessionLocale,
    )..limit(1)).getSingleOrNull();
    if (ligne == null) return null;
    final profilJson = await _documents.lireObjet(_typeProfil, _cleProfil);
    final profil = profilJson != null
        ? ProfilUtilisateur.fromJson(profilJson)
        : ProfilUtilisateur(
            idUtilisateur: 'u-${ligne.identifiant}',
            identifiant: ligne.identifiant,
            prenom: ligne.identifiant,
            nom: '',
            fonction: '',
            perimetre: '',
          );
    return SessionEnregistree(
      profil: profil,
      roleCode: ligne.roleCode,
      pinHashLocal: ligne.pinHashLocal,
      pinSel: ligne.pinSel,
      derniereConnexionEnLigne: ligne.derniereConnexionEnLigne,
    );
  }

  @override
  Future<void> enregistrer(SessionEnregistree session) async {
    await _base
        .into(_base.sessionLocale)
        .insertOnConflictUpdate(
          SessionLocaleCompanion.insert(
            idSession: _idSession,
            identifiant: session.profil.identifiant,
            roleCode: session.roleCode,
            jetonChiffre: const Value(null),
            pinHashLocal: session.pinHashLocal,
            pinSel: session.pinSel,
            derniereConnexionEnLigne: session.derniereConnexionEnLigne,
          ),
        );
    await _documents.ecrireObjet(
      _typeProfil,
      _cleProfil,
      session.profil.toJson(),
    );
  }

  @override
  Future<void> effacerTout() {
    return _base.transaction(() async {
      for (final table in _base.allTables) {
        await _base.delete(table).go();
      }
    });
  }
}

/// Implémentation en mémoire, pour les tests.
class DepotSessionMemoire implements DepotSession {
  DepotSessionMemoire([this._session]);

  SessionEnregistree? _session;

  @override
  Future<SessionEnregistree?> lire() async => _session;

  @override
  Future<void> enregistrer(SessionEnregistree session) async =>
      _session = session;

  @override
  Future<void> effacerTout() async => _session = null;
}
