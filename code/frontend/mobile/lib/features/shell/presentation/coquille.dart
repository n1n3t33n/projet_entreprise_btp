import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../core/navigation/acces_par_role.dart';
import '../../../core/navigation/ecran_mobile.dart';
import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/jetons.dart';
import '../../sync/presentation/ecran_synchronisation.dart';
import 'accueil_role.dart';
import 'ecran_reserve.dart';

/// Coquille de navigation unique, filtrée selon le rôle connecté.
///
/// Une action n'apparaît jamais pour un rôle qui n'y a pas droit (charte § 9.3).
/// L'en-tête marine et la barre basse reprennent les wireframes (A1–A5).
class Coquille extends ConsumerStatefulWidget {
  const Coquille({required this.role, required this.identifiant, super.key});

  final RoleTerrain role;
  final String identifiant;

  @override
  ConsumerState<Coquille> createState() => _CoquilleState();
}

class _CoquilleState extends ConsumerState<Coquille> {
  int _index = 0;

  /// Bascule sur l'onglet correspondant à [ecran] s'il est autorisé au rôle.
  void _allerVers(EcranMobile ecran) {
    final ecrans = AccesParRole.ecransAutorises(widget.role);
    final cible = ecrans.indexOf(ecran);
    if (cible >= 0) setState(() => _index = cible);
  }

  @override
  Widget build(BuildContext context) {
    final ecrans = AccesParRole.ecransAutorises(widget.role);
    final indexSur = _index.clamp(0, ecrans.length - 1);
    final courant = ecrans[indexSur];

    return Scaffold(
      backgroundColor: Jetons.fond,
      body: Column(
        children: [
          _EnTeteChantier(
            role: widget.role,
            identifiant: widget.identifiant,
            onVerrouiller: () =>
                ref.read(controleurAuthProvider.notifier).verrouiller(),
          ),
          Expanded(child: _corps(courant)),
        ],
      ),
      bottomNavigationBar: _BarreBasse(
        ecrans: ecrans,
        indexCourant: indexSur,
        onSelection: (i) => setState(() => _index = i),
      ),
    );
  }

  Widget _corps(EcranMobile ecran) {
    return switch (ecran) {
      EcranMobile.accueil => AccueilRole(
        role: widget.role,
        onNaviguer: _allerVers,
        onSynchroniser: () => _allerVers(EcranMobile.synchronisation),
      ),
      EcranMobile.synchronisation => const EcranSynchronisation(),
      _ => EcranReserve(libelle: ecran.libelle),
    };
  }
}

/// Bandeau d'en-tête marine : marque Schiavone, chantier, rôle et verrouillage.
class _EnTeteChantier extends StatelessWidget {
  const _EnTeteChantier({
    required this.role,
    required this.identifiant,
    required this.onVerrouiller,
  });

  final RoleTerrain role;
  final String identifiant;
  final VoidCallback onVerrouiller;

  @override
  Widget build(BuildContext context) {
    final initiales = identifiant.isEmpty
        ? '?'
        : identifiant.substring(0, 1).toUpperCase();

    return Material(
      color: Jetons.marine,
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(
            Jetons.espace3,
            Jetons.espace2,
            Jetons.espace2,
            Jetons.espace3,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'SCHIAVONE GROUP',
                          style: TextStyle(
                            color: Jetons.orVif,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.2,
                          ),
                        ),
                        SizedBox(height: 2),
                        Text(
                          'Chantier Grand-Bassam',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    tooltip: 'Verrouiller',
                    onPressed: onVerrouiller,
                    icon: const Icon(
                      PhosphorIconsRegular.lock,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: Jetons.espace2),
              Row(
                children: [
                  CircleAvatar(
                    radius: 16,
                    backgroundColor: Jetons.orVif,
                    child: Text(
                      initiales,
                      style: const TextStyle(
                        color: Jetons.marine,
                        fontWeight: FontWeight.w700,
                        fontSize: 13,
                      ),
                    ),
                  ),
                  const SizedBox(width: Jetons.espace2),
                  Expanded(
                    child: RichText(
                      text: TextSpan(
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 13,
                        ),
                        children: [
                          TextSpan(
                            text: role.libelle,
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          TextSpan(
                            text: ' · $identifiant',
                            style: const TextStyle(color: Colors.white70),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Barre de navigation basse, filtrée par rôle et stylée à la charte
/// (actif marine, pastille de fond douce).
class _BarreBasse extends StatelessWidget {
  const _BarreBasse({
    required this.ecrans,
    required this.indexCourant,
    required this.onSelection,
  });

  final List<EcranMobile> ecrans;
  final int indexCourant;
  final ValueChanged<int> onSelection;

  @override
  Widget build(BuildContext context) {
    Color couleur(Set<WidgetState> etats) =>
        etats.contains(WidgetState.selected)
        ? Jetons.marine
        : Jetons.texteSecondaire;

    return NavigationBarTheme(
      data: NavigationBarThemeData(
        backgroundColor: Jetons.surface,
        indicatorColor: Jetons.fondSection,
        iconTheme: WidgetStateProperty.resolveWith(
          (etats) => IconThemeData(color: couleur(etats)),
        ),
        labelTextStyle: WidgetStateProperty.resolveWith(
          (etats) => TextStyle(
            fontSize: 12,
            color: couleur(etats),
            fontWeight: etats.contains(WidgetState.selected)
                ? FontWeight.w700
                : FontWeight.w500,
          ),
        ),
      ),
      child: NavigationBar(
        selectedIndex: indexCourant,
        onDestinationSelected: onSelection,
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
}
