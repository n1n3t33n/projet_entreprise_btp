import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/bandeau_synchro.dart';
import '../../../components/en_tetes.dart';
import '../../../components/surfaces.dart';
import '../../../core/navigation/onglet_role.dart';
import '../../../core/navigation/transitions.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../auth/domain/profil_utilisateur.dart';
import '../../profil/presentation/ecran_profil.dart';
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
    OngletRole.synchro => const EcranSynchronisation(),
    OngletRole.profil => EcranProfil(profil: profil, role: role),
    _ => AccueilEnPreparation(onglet: onglet, role: role, profil: profil),
  };
}

/// Compteurs affichés sur les onglets (éléments à valider…).
Map<OngletRole, int> pastillesOnglets(WidgetRef ref, RoleTerrain role) =>
    const {};

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

/// Accueil provisoire d'un onglet dont le module arrive à l'étape suivante.
class AccueilEnPreparation extends StatelessWidget {
  const AccueilEnPreparation({
    required this.onglet,
    required this.role,
    required this.profil,
    super.key,
  });

  final OngletRole onglet;
  final RoleTerrain role;
  final ProfilUtilisateur profil;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      children: [
        EnTeteRole(
          surTitre: surTitreChantier(profil),
          titre: '${libelleRole(t, role)} · ${profil.nomComplet}',
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(Jetons.margeMobile),
            children: [
              BandeauSynchro(
                onSynchroniser: () => ouvrirSynchronisation(context),
              ),
              const SizedBox(height: Jetons.espace4),
              EtatVide(
                icone: PhosphorIconsRegular.hardHat,
                titre: onglet.libelle(t),
                texte: t.moduleEnPreparation,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
