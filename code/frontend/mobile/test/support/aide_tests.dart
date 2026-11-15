import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:chantiersync_mobile/core/preferences/preferences.dart';
import 'package:chantiersync_mobile/core/providers.dart';
import 'package:chantiersync_mobile/core/roles/role_terrain.dart';
import 'package:chantiersync_mobile/core/stockage/magasin_documents.dart';
import 'package:chantiersync_mobile/features/auth/data/depot_session.dart';
import 'package:chantiersync_mobile/features/auth/domain/etat_auth.dart';
import 'package:chantiersync_mobile/features/auth/domain/profil_utilisateur.dart';
import 'package:chantiersync_mobile/features/auth/application/controleur_auth.dart';
import 'package:chantiersync_mobile/features/sync/data/depot_file_envoi.dart';
import 'package:chantiersync_mobile/l10n/traductions.dart';
import 'package:chantiersync_mobile/theme/theme_app.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

/// Opérateur de démonstration utilisé par les tests.
const ProfilUtilisateur profilMagasinier = ProfilUtilisateur(
  idUtilisateur: 'u-magasinier',
  identifiant: 'magasinier',
  prenom: 'Mamadou',
  nom: 'Koné',
  fonction: 'Magasinier',
  perimetre: 'Chantier de Grand-Bassam',
);

/// Charge les polices de l'application (texte et icônes) dans le moteur de
/// test, pour que les captures ressemblent à l'écran réel.
Future<void> chargerPolices() async {
  final manifeste =
      jsonDecode(await rootBundle.loadString('FontManifest.json'))
          as List<dynamic>;
  for (final entree in manifeste.cast<Map<String, dynamic>>()) {
    final chargeur = FontLoader(entree['family'] as String);
    for (final police
        in (entree['fonts'] as List<dynamic>).cast<Map<String, dynamic>>()) {
      chargeur.addFont(rootBundle.load(police['asset'] as String));
    }
    await chargeur.load();
  }
}

/// Contrôleur d'authentification figé sur un état donné.
class ControleurAuthFige extends ControleurAuth {
  ControleurAuthFige(this._etat);

  final EtatAuth _etat;

  @override
  EtatAuth build() => _etat;

  @override
  Future<void> initialiser() async {}
}

/// Doublures en mémoire des dépôts : aucun test ne touche une vraie base.
List<Override> doublures({
  MagasinDocuments? documents,
  DepotFileEnvoi? file,
  DepotSession? session,
  EtatAuth? etat,
  Preferences preferences = const Preferences(),
}) {
  return [
    magasinDocumentsProvider.overrideWithValue(
      documents ?? MagasinDocumentsMemoire(),
    ),
    depotFileEnvoiProvider.overrideWithValue(file ?? DepotFileEnvoiMemoire()),
    depotSessionProvider.overrideWithValue(session ?? DepotSessionMemoire()),
    idAppareilProvider.overrideWithValue('T-841'),
    preferencesInitialesProvider.overrideWithValue(preferences),
    if (etat != null)
      controleurAuthProvider.overrideWith(() => ControleurAuthFige(etat)),
  ];
}

/// État « accès ouvert » pour un rôle donné.
AuthDeverrouille etatOuvert(
  RoleTerrain role, [
  ProfilUtilisateur profil = profilMagasinier,
]) {
  return AuthDeverrouille(profil: profil, role: role);
}

final GlobalKey _cleCapture = GlobalKey();

/// Monte un écran dans l'application de test (thèmes, langues, doublures).
Widget monter(Widget ecran, {List<Override> overrides = const []}) {
  return ProviderScope(
    overrides: overrides,
    child: Consumer(
      builder: (context, ref, _) {
        final preferences = ref.watch(preferencesProvider);
        return RepaintBoundary(
          key: _cleCapture,
          child: MaterialApp(
            debugShowCheckedModeBanner: false,
            theme: ThemeApp.clair(),
            darkTheme: ThemeApp.sombre(),
            themeMode: preferences.theme,
            locale: preferences.langue,
            supportedLocales: languesDisponibles,
            localizationsDelegates: Traductions.localizationsDelegates,
            home: ecran,
          ),
        );
      },
    ),
  );
}

/// Donne à la fenêtre de test la taille d'un téléphone (en points).
void definirEcran(
  WidgetTester tester, {
  double largeur = 390,
  double hauteur = 844,
}) {
  tester.view.devicePixelRatio = 2;
  tester.view.physicalSize = Size(largeur * 2, hauteur * 2);
  addTearDown(tester.view.reset);
}

/// Enregistre l'écran courant en PNG dans `build/apercus/<nom>.png`.
Future<void> capturer(WidgetTester tester, String nom) async {
  // Laisse le temps aux images vectorielles (logo) de se décoder.
  await tester.runAsync(
    () => Future<void>.delayed(const Duration(milliseconds: 120)),
  );
  await tester.pumpAndSettle();
  final rendu =
      _cleCapture.currentContext!.findRenderObject()! as RenderRepaintBoundary;
  final octets = await tester.runAsync(() async {
    final image = await rendu.toImage(pixelRatio: 2);
    final donnees = await image.toByteData(format: ui.ImageByteFormat.png);
    return donnees!.buffer.asUint8List();
  });
  final fichier = File('build/apercus/$nom.png');
  fichier.parent.createSync(recursive: true);
  fichier.writeAsBytesSync(octets!);
}
