import 'package:drift/drift.dart';

import 'tables.dart';

part 'base_locale.g.dart';

/// Base de données locale chiffrée de ChantierSync (CL-6 / MPD-6).
///
/// L'exécuteur ([QueryExecutor]) est injecté : l'application fournit une base
/// SQLCipher (voir `ouverture_chiffree.dart`), les tests fournissent une base
/// en mémoire. La base elle-même ne connaît donc ni le chiffrement ni le
/// système de fichiers — couche de données testable et modulable.
@DriftDatabase(
  tables: [
    SessionLocale,
    FileEnvoi,
    CacheReference,
    JournalLocal,
    LotSynchronisation,
    ResultatEvenement,
  ],
)
class BaseLocale extends _$BaseLocale {
  BaseLocale(super.executor);

  @override
  int get schemaVersion => 1;
}
