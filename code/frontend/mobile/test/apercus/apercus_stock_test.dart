// Captures d'écran du module Stock. Voir apercus_test.dart pour le lancement.

import 'package:chantiersync_mobile/core/preferences/preferences.dart';
import 'package:chantiersync_mobile/core/roles/role_terrain.dart';
import 'package:chantiersync_mobile/features/shell/presentation/coquille.dart';
import 'package:chantiersync_mobile/features/stock/presentation/ecran_inventaire.dart';
import 'package:chantiersync_mobile/features/stock/presentation/ecran_mouvement.dart';
import 'package:chantiersync_mobile/features/stock/presentation/ecran_registre.dart';
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
    RoleTerrain role = RoleTerrain.magasinier,
    double hauteur = 1500,
    Preferences preferences = const Preferences(theme: ThemeMode.light),
    Future<void> Function()? avant,
  }) async {
    debugDisableShadows = false;
    definirEcran(tester, hauteur: hauteur);
    await tester.pumpWidget(
      monter(
        ecran,
        overrides: doublures(etat: etatOuvert(role), preferences: preferences),
      ),
    );
    await tester.pumpAndSettle();
    if (avant != null) await avant();
    await capturer(tester, nom);
    debugDisableShadows = true;
  }

  testWidgets('accueil magasinier', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'a1_magasinier',
      const Coquille(profil: profilMagasinier, role: RoleTerrain.magasinier),
    );
  });

  testWidgets('accueil gestionnaire', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'a4_gestionnaire',
      const Coquille(
        profil: profilMagasinier,
        role: RoleTerrain.gestionnaireStock,
      ),
      role: RoleTerrain.gestionnaireStock,
      hauteur: 1700,
    );
  });

  testWidgets('validation', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e9_validation',
      const Coquille(
        profil: profilMagasinier,
        role: RoleTerrain.gestionnaireStock,
      ),
      role: RoleTerrain.gestionnaireStock,
      hauteur: 1700,
      avant: () async {
        await tester.tap(find.text('À valider').last);
        await tester.pumpAndSettle();
      },
    );
  });

  testWidgets('registre', skip: !_actif, (tester) async {
    await apercu(tester, 'e3_registre', const EcranRegistre());
  });

  testWidgets('registre sombre', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e3_registre_sombre',
      const EcranRegistre(),
      preferences: const Preferences(theme: ThemeMode.dark),
    );
  });

  testWidgets('fiche article', skip: !_actif, (tester) async {
    await apercu(tester, 'e4_fiche', const EcranFicheArticle(code: 'CIM-045'));
  });

  testWidgets('sortie rapide', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e5_sortie',
      const EcranMouvement(mode: ModeSaisie.sortie),
      avant: () async {
        await tester.tap(find.text('Choisir un article'));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Ciment CPJ 45 — sac 50 kg'));
        await tester.pumpAndSettle();
        await tester.tap(find.text('+5'));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Îlot B · Logement B2'));
        await tester.pumpAndSettle();
      },
    );
  });

  testWidgets('historique', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e10_journal',
      const Coquille(profil: profilMagasinier, role: RoleTerrain.magasinier),
      avant: () async {
        await tester.tap(find.text('Historique'));
        await tester.pumpAndSettle();
      },
    );
  });

  testWidgets('inventaire', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e8_inventaire',
      const EcranInventaire(),
      avant: () async {
        await tester.tap(find.bySemanticsLabel('Diminuer'));
        await tester.pumpAndSettle();
      },
    );
  });
}
