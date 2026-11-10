import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqlcipher_flutter_libs/sqlcipher_flutter_libs.dart';
import 'package:sqlite3/open.dart';
import 'package:sqlite3/sqlite3.dart';

/// Ouvre la base locale chiffrée par SQLCipher.
///
/// [cle] est la clé de chiffrement de la base, conservée dans le coffre de
/// l'appareil (Keystore/Keychain via flutter_secure_storage) et jamais écrite
/// en clair sur le disque. Le PIN débloque l'accès à l'application ; la clé de
/// base, elle, vit dans le coffre matériel.
///
/// Réservé à l'exécution sur appareil (Android/iOS). Les tests utilisent une
/// base en mémoire, sans chiffrement.
QueryExecutor ouvrirBaseChiffree(String cle) {
  return LazyDatabase(() async {
    if (Platform.isAndroid) {
      await applyWorkaroundToOpenSqlCipherOnOldAndroidVersions();
      open.overrideFor(OperatingSystem.android, openCipherOnAndroid);
    }

    final dossier = await getApplicationDocumentsDirectory();
    final fichier = File(p.join(dossier.path, 'chantiersync.db'));

    final cacheTemp = await getTemporaryDirectory();
    sqlite3.tempDirectory = cacheTemp.path;

    return NativeDatabase.createInBackground(
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
