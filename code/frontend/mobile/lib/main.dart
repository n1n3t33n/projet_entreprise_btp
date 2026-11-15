import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'app.dart';
import 'core/db/base_locale.dart';
import 'core/db/ouverture_chiffree.dart';
import 'core/outils/identifiants.dart';
import 'core/preferences/depot_preferences_coffre.dart';
import 'core/preferences/preferences.dart';
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

  // Identifiant court de l'appareil, attribué une fois pour toutes.
  var idAppareil = await coffre.lireIdAppareil();
  if (idAppareil == null) {
    idAppareil = genererIdAppareil();
    await coffre.ecrireIdAppareil(idAppareil);
  }

  // Langue et thème lus avant le premier affichage : pas de clignotement.
  const depotPreferences = DepotPreferencesCoffre(coffre);
  final preferences = await depotPreferences.lire();

  // Enregistre SQLCipher sur l'isolate principal avant toute ouverture.
  await preparerSqlCipher();
  final base = BaseLocale(ouvrirBaseChiffree(cle));

  runApp(
    ProviderScope(
      overrides: [
        coffreProvider.overrideWithValue(coffre),
        baseLocaleProvider.overrideWithValue(base),
        idAppareilProvider.overrideWithValue(idAppareil),
        depotPreferencesProvider.overrideWithValue(depotPreferences),
        preferencesInitialesProvider.overrideWithValue(preferences),
      ],
      child: const AppChantierSync(),
    ),
  );
}
