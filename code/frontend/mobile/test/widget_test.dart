import 'package:chantiersync_mobile/core/roles/role_terrain.dart';
import 'package:chantiersync_mobile/features/shell/presentation/coquille.dart';
import 'package:flutter_test/flutter_test.dart';

import 'support/aide_tests.dart';

void main() {
  Future<void> ouvrir(WidgetTester tester, RoleTerrain role) async {
    definirEcran(tester);
    await tester.pumpWidget(
      monter(
        Coquille(profil: profilMagasinier, role: role),
        overrides: doublures(etat: etatOuvert(role)),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('la coquille n\'expose que les onglets du rôle', (tester) async {
    await ouvrir(tester, RoleTerrain.magasinier);

    for (final libelle in ['Stock', 'Historique', 'Synchro', 'Profil']) {
      expect(find.text(libelle), findsWidgets);
    }
    // Le magasinier saisit, il ne valide pas (séparation des fonctions).
    expect(find.text('À valider'), findsNothing);
  });

  testWidgets('le gestionnaire de stock voit l\'onglet de validation', (
    tester,
  ) async {
    await ouvrir(tester, RoleTerrain.gestionnaireStock);
    expect(find.text('À valider'), findsWidgets);
  });

  testWidgets('changer de langue traduit aussitôt l\'interface', (
    tester,
  ) async {
    await ouvrir(tester, RoleTerrain.magasinier);
    await tester.tap(find.text('Profil'));
    await tester.pumpAndSettle();
    expect(find.text('Langue'), findsOneWidget);

    await tester.tap(find.text('English'));
    await tester.pumpAndSettle();
    expect(find.text('Language'), findsOneWidget);
    expect(find.text('Profile'), findsWidgets);

    await tester.tap(find.text('Italiano'));
    await tester.pumpAndSettle();
    expect(find.text('Lingua'), findsOneWidget);
  });
}
