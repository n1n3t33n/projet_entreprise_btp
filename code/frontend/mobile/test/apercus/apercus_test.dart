// Captures d'écran des principaux écrans, pour contrôler le rendu sans
// émulateur. Désactivées par défaut : lancer avec
//   flutter test test/apercus --dart-define=APERCUS=true
// Les images sont écrites dans build/apercus/ (non versionné).

import 'package:chantiersync_mobile/core/preferences/preferences.dart';
import 'package:chantiersync_mobile/core/roles/role_terrain.dart';
import 'package:chantiersync_mobile/features/auth/domain/etat_auth.dart';
import 'package:chantiersync_mobile/features/auth/presentation/ecran_connexion.dart';
import 'package:chantiersync_mobile/features/auth/presentation/ecran_definition_pin.dart';
import 'package:chantiersync_mobile/features/auth/presentation/ecran_deverrouillage.dart';
import 'package:chantiersync_mobile/features/shell/presentation/coquille.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../support/aide_tests.dart';

const bool _actif = bool.fromEnvironment('APERCUS');

void main() {
  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    await chargerPolices();
  });

  Future<void> apercu(
    WidgetTester tester,
    String nom,
    Widget ecran, {
    double hauteur = 844,
    Preferences preferences = const Preferences(theme: ThemeMode.light),
    EtatAuth? etat,
  }) async {
    // Les ombres sont coupées par défaut en test : on les rétablit le temps
    // de la capture, puis on rend la main dans l'état attendu par le cadre.
    debugDisableShadows = false;
    definirEcran(tester, hauteur: hauteur);
    await tester.pumpWidget(
      monter(
        ecran,
        overrides: doublures(etat: etat, preferences: preferences),
      ),
    );
    await tester.pumpAndSettle();
    await capturer(tester, nom);
    debugDisableShadows = true;
  }

  testWidgets('écran PIN', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'pin_clair',
      EcranDeverrouillage(
        profil: profilMagasinier,
        role: RoleTerrain.magasinier,
        derniereConnexion: DateTime(2026, 11, 14, 6, 30),
      ),
      hauteur: 900,
    );
  });

  testWidgets('écran PIN sombre', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'pin_sombre',
      const EcranDeverrouillage(
        profil: profilMagasinier,
        role: RoleTerrain.magasinier,
      ),
      hauteur: 900,
      preferences: const Preferences(theme: ThemeMode.dark),
    );
  });

  testWidgets('connexion', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'connexion',
      const EcranConnexion(),
      hauteur: 900,
      etat: const AuthNonConnecte(motif: MotifConnexion.sessionExpiree),
    );
  });

  testWidgets('définition du code', skip: !_actif, (tester) async {
    await apercu(tester, 'definition_pin', const EcranDefinitionPin());
  });

  testWidgets('coquille et profil', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'accueil',
      const Coquille(profil: profilMagasinier, role: RoleTerrain.magasinier),
      etat: etatOuvert(RoleTerrain.magasinier),
    );
    await tester.tap(find.text('Profil'));
    await tester.pumpAndSettle();
    debugDisableShadows = false;
    await capturer(tester, 'profil');
    debugDisableShadows = true;
  });

  testWidgets('profil en italien et sombre', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'profil_it_sombre',
      const Coquille(
        profil: profilMagasinier,
        role: RoleTerrain.gestionnaireStock,
      ),
      etat: etatOuvert(RoleTerrain.gestionnaireStock),
      preferences: const Preferences(
        langue: Locale('it'),
        theme: ThemeMode.dark,
      ),
    );
    await tester.tap(find.text('Profilo'));
    await tester.pumpAndSettle();
    debugDisableShadows = false;
    await capturer(tester, 'profil_it_sombre');
    debugDisableShadows = true;
  });
}
