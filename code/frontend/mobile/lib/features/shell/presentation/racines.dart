import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/surfaces.dart';
import '../../../core/navigation/onglet_role.dart';
import '../../../core/navigation/transitions.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/palette.dart';
import '../../auth/domain/profil_utilisateur.dart';
import '../../profil/presentation/ecran_profil.dart';
import '../../stock/application/etat_stock.dart';
import '../../stock/presentation/accueils_stock.dart';
import '../../stock/presentation/ecran_journal.dart';
import '../../stock/presentation/ecran_registre.dart';
import '../../stock/presentation/ecran_validation_stock.dart';
import '../../sync/presentation/ecran_synchronisation.dart';
import 'coquille.dart';

/// Écran racine de chaque onglet, selon le rôle.
///
/// C'est le seul endroit qui relie la navigation aux modules métier : brancher
/// un nouvel écran revient à compléter cette fonction.
Widget racineOnglet({
  required OngletRole onglet,
  required RoleTerrain role,
  required ProfilUtilisateur profil,
}) {
  return switch (onglet) {
    OngletRole.stock => switch (role) {
      RoleTerrain.magasinier => AccueilMagasinier(profil: profil),
      RoleTerrain.gestionnaireStock => AccueilGestionnaire(profil: profil),
      _ => const EcranRegistre(racine: true),
    },
    OngletRole.historique => const EcranJournal(racine: true),
    OngletRole.aValider => const EcranValidationStock(racine: true),
    OngletRole.synchro => const EcranSynchronisation(),
    OngletRole.profil => EcranProfil(profil: profil, role: role),
    OngletRole.fiches => TableauDeBord(
      profil: profil,
      role: role,
      blocs: const [_EnPreparation()],
    ),
  };
}

/// Compteurs affichés sur les onglets (éléments à valider…).
Map<OngletRole, int> pastillesOnglets(WidgetRef ref, RoleTerrain role) {
  return {
    if (role.peutValiderStock)
      OngletRole.aValider: ref.watch(sortiesAValiderProvider).length,
  };
}

/// Ouvre le centre de synchronisation : l'onglet s'il existe pour ce rôle,
/// sinon l'écran par-dessus.
void ouvrirSynchronisation(BuildContext context) {
  final ouvert = NavigationOnglets.of(context).allerVers(OngletRole.synchro);
  if (!ouvert) {
    ouvrirEcran<void>(context, const EcranSynchronisation(autonome: true));
  }
}

/// Texte de contexte commun aux en-têtes : marque et chantier.
String surTitreChantier(ProfilUtilisateur profil) =>
    'SCHIAVONE GROUP · ${profil.perimetre}';

class _EnPreparation extends StatelessWidget {
  const _EnPreparation();

  @override
  Widget build(BuildContext context) {
    return EtatVide(
      icone: PhosphorIconsRegular.hardHat,
      titre: context.t.ongletFiches,
      texte: context.t.moduleEnPreparation,
    );
  }
}
