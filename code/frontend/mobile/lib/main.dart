import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'app.dart';
import 'core/db/base_locale.dart';
import 'core/db/ouverture_chiffree.dart';
import 'core/providers.dart';
import 'core/securite/cle_base.dart';
import 'core/securite/coffre.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Clé de chiffrement de la base : lue dans le coffre, générée au premier
  // lancement puis conservée au coffre matériel. Jamais en clair sur disque.
  const coffre = Coffre(FlutterSecureStorage());
  var cle = await coffre.lireCleBase();
  if (cle == null) {
    cle = genererCleBase();
    await coffre.ecrireCleBase(cle);
  }

  // Enregistre SQLCipher sur l'isolate principal avant toute ouverture.
  await preparerSqlCipher();
  final base = BaseLocale(ouvrirBaseChiffree(cle));

  runApp(
    ProviderScope(
      overrides: [
        coffreProvider.overrideWithValue(coffre),
        baseLocaleProvider.overrideWithValue(base),
      ],
      child: const AppChantierSync(),
    ),
  );
}
