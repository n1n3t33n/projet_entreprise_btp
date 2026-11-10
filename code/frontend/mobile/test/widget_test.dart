import 'package:chantiersync_mobile/core/db/base_locale.dart';
import 'package:chantiersync_mobile/core/providers.dart';
import 'package:chantiersync_mobile/core/roles/role_terrain.dart';
import 'package:chantiersync_mobile/features/shell/presentation/coquille.dart';
import 'package:chantiersync_mobile/features/sync/data/depot_file_envoi.dart';
import 'package:drift/drift.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

/// File d'envoi factice : ne touche aucune base (l'exécuteur paresseux n'est
/// jamais ouvert), renvoie une file vide.
class _FileVide extends DepotFileEnvoi {
  _FileVide()
    : super(BaseLocale(LazyDatabase(() async => throw UnimplementedError())));

  @override
  Future<int> compterEnAttente() async => 0;
}

void main() {
  testWidgets('la coquille n\'expose que les écrans du rôle', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [depotFileEnvoiProvider.overrideWithValue(_FileVide())],
        child: const MaterialApp(
          home: Coquille(
            role: RoleTerrain.magasinier,
            identifiant: 'magasinier',
          ),
        ),
      ),
    );
    // Laisse les animations d'apparition (timers de cascade) se stabiliser.
    await tester.pumpAndSettle();

    // Magasinier : Accueil, Stock, Mouvements, Synchronisation.
    expect(find.byType(NavigationDestination), findsNWidgets(4));
    expect(find.text('Stock'), findsWidgets);
    expect(find.text('Mouvements'), findsWidgets);
    // Aucune fonction d'un autre rôle n'apparaît.
    expect(find.text('Validation'), findsNothing);
  });
}
