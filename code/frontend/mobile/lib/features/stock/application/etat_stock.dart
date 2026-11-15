import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../data/depot_stock.dart';
import '../domain/modeles.dart';

final depotStockProvider = Provider<DepotStock>(
  (ref) => DepotStock(
    ref.read(magasinDocumentsProvider),
    ref.read(depotFileEnvoiProvider),
  ),
);

final articlesProvider = FutureProvider<List<ArticleStock>>(
  (ref) => ref.read(depotStockProvider).articles(),
);

final mouvementsProvider = FutureProvider<List<MouvementStock>>(
  (ref) => ref.read(depotStockProvider).mouvements(),
);

final inventaireProvider = FutureProvider<Inventaire>(
  (ref) => ref.read(depotStockProvider).inventaire(),
);

/// Sorties en attente de validation.
final sortiesAValiderProvider = Provider<List<MouvementStock>>((ref) {
  final mouvements = ref.watch(mouvementsProvider).valueOrNull ?? const [];
  return mouvements.where((m) => m.statut == StatutMouvement.aValider).toList();
});

/// Articles sous leur seuil, du plus urgent au moins urgent.
final alertesStockProvider = Provider<List<ArticleStock>>((ref) {
  final articles = ref.watch(articlesProvider).valueOrNull ?? const [];
  return articles.where((a) => a.sousSeuil).toList()
    ..sort((a, b) => a.niveau.index.compareTo(b.niveau.index));
});

/// À appeler après toute écriture : recharge le stock et la file d'envoi.
void rafraichirStock(WidgetRef ref) {
  ref.invalidate(articlesProvider);
  ref.invalidate(mouvementsProvider);
  ref.invalidate(inventaireProvider);
  ref.invalidate(fileEnvoiProvider);
}

/// Droits d'action sur le stock, par rôle (charte § 9.3). Provisoire : à
/// terme, servi par la matrice des droits comme sur le web.
extension DroitsStock on RoleTerrain {
  /// Saisir sorties, réceptions, retours et comptages.
  bool get peutSaisirStock => this == RoleTerrain.magasinier;

  /// Approuver les sorties et valider les écarts d'inventaire.
  bool get peutValiderStock =>
      this == RoleTerrain.gestionnaireStock || this == RoleTerrain.chefChantier;
}
