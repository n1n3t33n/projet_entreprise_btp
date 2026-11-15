import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../data/depot_avancement.dart';
import '../domain/modeles.dart';

final depotAvancementProvider = Provider<DepotAvancement>(
  (ref) => DepotAvancement(
    ref.read(magasinDocumentsProvider),
    ref.read(depotFileEnvoiProvider),
  ),
);

final toutesEtapesProvider = FutureProvider<List<EtapeTravaux>>(
  (ref) => ref.read(depotAvancementProvider).etapes(),
);

final evenementsProvider = FutureProvider<List<EvenementEtape>>(
  (ref) => ref.read(depotAvancementProvider).evenements(),
);

/// Étapes visibles de l'opérateur : un technicien ne voit que sa fiche de
/// route ; ceux qui encadrent voient tout le chantier.
final etapesProvider = Provider<List<EtapeTravaux>>((ref) {
  final toutes = ref.watch(toutesEtapesProvider).valueOrNull ?? const [];
  final operateur = ref.watch(operateurProvider);
  if (operateur == null) return const [];
  if (operateur.role != RoleTerrain.technicien) return toutes;
  return toutes
      .where((e) => e.idResponsable == operateur.profil.idUtilisateur)
      .toList();
});

/// Étapes déclarées terminées, en attente de validation.
final etapesAValiderProvider = Provider<List<EtapeTravaux>>((ref) {
  final toutes = ref.watch(toutesEtapesProvider).valueOrNull ?? const [];
  return toutes.where((e) => e.statut == StatutEtape.termineeDeclaree).toList();
});

/// À appeler après toute action : recharge les étapes, le journal et la file.
void rafraichirAvancement(WidgetRef ref) {
  ref.invalidate(toutesEtapesProvider);
  ref.invalidate(evenementsProvider);
  ref.invalidate(fileEnvoiProvider);
}

/// Droits d'action sur l'avancement, par rôle (charte § 9.3). Provisoire : à
/// terme, servi par la matrice des droits comme sur le web.
extension DroitsAvancement on RoleTerrain {
  /// Démarrer, pointer, terminer une étape et signaler un blocage.
  bool get peutExecuterEtapes =>
      this == RoleTerrain.technicien || this == RoleTerrain.chefChantier;

  /// Valider ou refuser une étape déclarée terminée.
  bool get peutValiderEtapes =>
      this == RoleTerrain.chefChantier ||
      this == RoleTerrain.responsableTechnique;

  /// Confier une étape à une autre équipe.
  bool get peutReaffecter => this == RoleTerrain.chefChantier;
}
