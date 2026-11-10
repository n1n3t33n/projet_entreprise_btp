import 'package:drift/drift.dart';

import '../../../core/db/base_locale.dart';
import '../domain/statut_envoi.dart';

/// Dépôt de la file d'envoi (ET-3).
///
/// L'enfilement est idempotent : la clé primaire étant l'UUID d'événement,
/// réinsérer le même événement est ignoré (`insertOrIgnore`). Aucun envoi
/// réseau n'est déclenché au jalon M1 — seule la file locale est gérée.
class DepotFileEnvoi {
  const DepotFileEnvoi(this._base);

  final BaseLocale _base;

  /// Enfile un événement. Renvoie `true` s'il a été ajouté, `false` s'il était
  /// déjà présent (idempotence).
  Future<bool> enfiler({
    required String uuidEvenement,
    required String typeEvenement,
    required String chargeUtileJson,
    String? sessionLocaleId,
  }) async {
    final lignes = await _base
        .into(_base.fileEnvoi)
        .insert(
          FileEnvoiCompanion.insert(
            uuidEvenement: uuidEvenement,
            typeEvenement: typeEvenement,
            chargeUtile: chargeUtileJson,
            statut: StatutEnvoi.enAttente.code,
            sessionLocaleId: Value(sessionLocaleId),
          ),
          mode: InsertMode.insertOrIgnore,
        );
    return lignes > 0;
  }

  Future<List<FileEnvoiRow>> enAttente() {
    return (_base.select(
      _base.fileEnvoi,
    )..where((t) => t.statut.equals(StatutEnvoi.enAttente.code))).get();
  }

  Future<int> compterEnAttente() async {
    final lignes = await enAttente();
    return lignes.length;
  }

  Future<List<FileEnvoiRow>> toutes() => _base.select(_base.fileEnvoi).get();
}
