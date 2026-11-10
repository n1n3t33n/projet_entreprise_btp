import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../core/navigation/acces_par_role.dart';
import '../../../core/navigation/ecran_mobile.dart';
import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../../sync/presentation/ecran_synchronisation.dart';
import 'accueil_role.dart';
import 'ecran_reserve.dart';

/// Coquille de navigation unique, filtrée selon le rôle connecté.
///
/// Une action n'apparaît jamais pour un rôle qui n'y a pas droit (charte § 9.3).
class Coquille extends ConsumerStatefulWidget {
  const Coquille({required this.role, super.key});

  final RoleTerrain role;

  @override
  ConsumerState<Coquille> createState() => _CoquilleState();
}

class _CoquilleState extends ConsumerState<Coquille> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final ecrans = AccesParRole.ecransAutorises(widget.role);
    final courant = ecrans[_index.clamp(0, ecrans.length - 1)];

    return Scaffold(
      appBar: AppBar(
        title: Text(courant.libelle),
        actions: [
          IconButton(
            tooltip: 'Verrouiller',
            icon: const Icon(PhosphorIconsRegular.lock),
            onPressed: () =>
                ref.read(controleurAuthProvider.notifier).verrouiller(),
          ),
        ],
      ),
      body: _corps(courant),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index.clamp(0, ecrans.length - 1),
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: [
          for (final ecran in ecrans)
            NavigationDestination(
              icon: Icon(ecran.icone),
              label: ecran.libelle,
            ),
        ],
      ),
    );
  }

  Widget _corps(EcranMobile ecran) {
    return switch (ecran) {
      EcranMobile.accueil => AccueilRole(role: widget.role),
      EcranMobile.synchronisation => const EcranSynchronisation(),
      _ => EcranReserve(libelle: ecran.libelle),
    };
  }
}
