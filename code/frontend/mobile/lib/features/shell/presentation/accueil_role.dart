import 'package:flutter/material.dart';

import '../../../core/navigation/acces_par_role.dart';
import '../../../core/navigation/ecran_mobile.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/jetons.dart';

/// Accueil dédié au rôle (wireframes A1–A5). Expose, en tuiles, les fonctions
/// autorisées au rôle ; les fonctions métier non livrées sont marquées.
class AccueilRole extends StatelessWidget {
  const AccueilRole({required this.role, super.key});

  final RoleTerrain role;

  @override
  Widget build(BuildContext context) {
    final fonctions = AccesParRole.ecransAutorises(
      role,
    ).where((ecran) => ecran != EcranMobile.accueil).toList();

    return ListView(
      padding: const EdgeInsets.all(Jetons.margeMobile),
      children: [
        Text(
          role.libelle,
          style: Theme.of(
            context,
          ).textTheme.headlineSmall?.copyWith(color: Jetons.marine),
        ),
        const SizedBox(height: Jetons.espace2),
        const Text(
          'Chantier Grand-Bassam',
          style: TextStyle(color: Jetons.texteSecondaire),
        ),
        const SizedBox(height: Jetons.espace4),
        for (final fonction in fonctions) ...[
          _TuileFonction(fonction: fonction),
          const SizedBox(height: Jetons.espace3),
        ],
      ],
    );
  }
}

class _TuileFonction extends StatelessWidget {
  const _TuileFonction({required this.fonction});

  final EcranMobile fonction;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(fonction.icone, color: Jetons.sarcelle),
        title: Text(fonction.libelle),
        trailing: fonction.reserveJalonSuivant
            ? const _BadgeBientot()
            : const Icon(Icons.chevron_right),
      ),
    );
  }
}

class _BadgeBientot extends StatelessWidget {
  const _BadgeBientot();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: Jetons.espace2,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: Jetons.orClair,
        borderRadius: BorderRadius.circular(999),
      ),
      child: const Text(
        'Bientôt',
        style: TextStyle(color: Jetons.or, fontSize: 12),
      ),
    );
  }
}
