import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqlcipher_flutter_libs/sqlcipher_flutter_libs.dart';
import 'package:sqlite3/open.dart';

/// Prépare le chargement de SQLCipher.
///
/// À appeler **une seule fois au démarrage, sur l'isolate principal**, avant
/// d'ouvrir la base. Sous Android, enregistre la bibliothèque SQLCipher
/// (`libsqlcipher.so`) ; sans cela, drift retombe sur `libsqlite3.so`, absent
/// de l'APK, et l'ouverture échoue. iOS/macOS lient SQLCipher statiquement :
/// aucun enregistrement nécessaire.
Future<void> preparerSqlCipher() async {
  if (Platform.isAndroid) {
    await applyWorkaroundToOpenSqlCipherOnOldAndroidVersions();
    open.overrideFor(OperatingSystem.android, openCipherOnAndroid);
  }
}

/// Ouvre la base locale chiffrée par SQLCipher.
///
/// [cle] est la clé de chiffrement, conservée dans le coffre de l'appareil et
/// jamais écrite en clair sur le disque. Ouverture en avant-plan (même isolate
/// que [preparerSqlCipher]) pour que l'enregistrement de la bibliothèque soit
/// pris en compte. Réservé à l'exécution sur appareil (Android/iOS).
QueryExecutor ouvrirBaseChiffree(String cle) {
  return LazyDatabase(() async {
    final dossier = await getApplicationDocumentsDirectory();
    final fichier = File(p.join(dossier.path, 'chantiersync.db'));

    return NativeDatabase(
      fichier,
      setup: (raw) {
        final cleEchappee = cle.replaceAll("'", "''");
        raw.execute("PRAGMA key = '$cleEchappee';");
        // Lecture témoin : échoue si la clé ne déverrouille pas la base.
        raw.execute('SELECT count(*) FROM sqlite_master;');
      },
    );
  });
}
