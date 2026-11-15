import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/navigation/onglet_role.dart';
import '../../../core/navigation/transitions.dart';
import '../../../core/roles/role_terrain.dart';
import '../../auth/domain/profil_utilisateur.dart';
import '../../avancement/application/etat_avancement.dart';
import '../../avancement/presentation/accueils_avancement.dart';
import '../../avancement/presentation/ecrans_etapes.dart';
import '../../avancement/presentation/ecrans_suivi.dart';
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
    OngletRole.fiches => switch (role) {
      RoleTerrain.technicien => AccueilTechnicien(profil: profil),
      _ => const EcranFicheRoute(racine: true),
    },
    OngletRole.aValider => switch (role) {
      RoleTerrain.chefChantier => AccueilChef(profil: profil),
      RoleTerrain.responsableTechnique => AccueilResponsable(profil: profil),
      _ => const EcranValidationStock(racine: true),
    },
    OngletRole.historique => switch (role) {
      RoleTerrain.technicien => const EcranJournalEtape(racine: true),
      _ => const EcranJournal(racine: true),
    },
    OngletRole.synchro => const EcranSynchronisation(),
    OngletRole.profil => EcranProfil(profil: profil, role: role),
  };
}

/// Compteurs affichés sur les onglets : ce qui attend une décision du rôle.
Map<OngletRole, int> pastillesOnglets(WidgetRef ref, RoleTerrain role) {
  final sorties = role.peutValiderStock
      ? ref.watch(sortiesAValiderProvider).length
      : 0;
  final etapes = role.peutValiderEtapes
      ? ref.watch(etapesAValiderProvider).length
      : 0;
  return {OngletRole.aValider: sorties + etapes};
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
