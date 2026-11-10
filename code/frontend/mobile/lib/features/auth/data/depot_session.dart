import 'package:drift/drift.dart';

import '../../../core/db/base_locale.dart';

/// Persistance de la session locale (table `session_locale`).
///
/// Le pilote fonctionne avec une seule session active par appareil : on garde
/// donc une ligne unique, de clé fixe. La dernière connexion en ligne sert
/// d'ancre au verrou de 14 jours.
class DepotSession {
  const DepotSession(this._base);

  final BaseLocale _base;

  static const String idSessionCourante = 'session-courante';

  Future<SessionLocaleRow?> lire() {
    return (_base.select(_base.sessionLocale)..limit(1)).getSingleOrNull();
  }

  Future<void> enregistrer({
    required String identifiant,
    required String roleCode,
    required String pinHashLocal,
    required String pinSel,
    required DateTime derniereConnexion,
    String? jetonChiffre,
  }) {
    return _base
        .into(_base.sessionLocale)
        .insertOnConflictUpdate(
          SessionLocaleCompanion.insert(
            idSession: idSessionCourante,
            identifiant: identifiant,
            roleCode: roleCode,
            jetonChiffre: Value(jetonChiffre),
            pinHashLocal: pinHashLocal,
            pinSel: pinSel,
            derniereConnexionEnLigne: derniereConnexion,
          ),
        );
  }

  Future<void> effacer() => _base.delete(_base.sessionLocale).go();
}
