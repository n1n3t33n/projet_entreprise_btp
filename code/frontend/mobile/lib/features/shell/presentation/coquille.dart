import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/navigation/onglet_role.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../auth/domain/profil_utilisateur.dart';
import 'barre_navigation.dart';
import 'racines.dart';

/// Accès à la navigation par onglets depuis n'importe quel écran d'un onglet
/// (ex. le bandeau de synchronisation qui ouvre le centre de synchro).
class NavigationOnglets extends InheritedWidget {
  const NavigationOnglets({
    required this.onglets,
    required this.allerVers,
    required super.child,
    super.key,
  });

  final List<OngletRole> onglets;

  /// Affiche l'onglet demandé s'il existe pour ce rôle ; renvoie `false` sinon.
  final bool Function(OngletRole onglet) allerVers;

  static NavigationOnglets of(BuildContext context) {
    final trouve = context
        .dependOnInheritedWidgetOfExactType<NavigationOnglets>();
    assert(trouve != null, 'NavigationOnglets absent du contexte.');
    return trouve!;
  }

  @override
  bool updateShouldNotify(NavigationOnglets ancien) =>
      ancien.onglets != onglets;
}

/// Coquille de navigation unique, filtrée selon le rôle connecté.
///
/// Une action n'apparaît jamais pour un rôle qui n'y a pas droit (charte § 9.3).
class Coquille extends ConsumerStatefulWidget {
  const Coquille({required this.profil, required this.role, super.key});

  final ProfilUtilisateur profil;
  final RoleTerrain role;

  @override
  ConsumerState<Coquille> createState() => _CoquilleState();
}

class _CoquilleState extends ConsumerState<Coquille> {
  late OngletRole _courant = ongletsPour(widget.role).first;

  bool _allerVers(OngletRole onglet) {
    if (!ongletsPour(widget.role).contains(onglet)) return false;
    setState(() => _courant = onglet);
    return true;
  }

  @override
  Widget build(BuildContext context) {
    final onglets = ongletsPour(widget.role);
    final courant = onglets.contains(_courant) ? _courant : onglets.first;

    return NavigationOnglets(
      onglets: onglets,
      allerVers: _allerVers,
      child: Scaffold(
        extendBody: true,
        body: _Fondu(
          cle: courant,
          child: IndexedStack(
            index: onglets.indexOf(courant),
            children: [
              for (final onglet in onglets)
                racineOnglet(
                  onglet: onglet,
                  role: widget.role,
                  profil: widget.profil,
                ),
            ],
          ),
        ),
        bottomNavigationBar: BarreNavigation(
          onglets: onglets,
          courant: courant,
          onSelection: _allerVers,
          pastilles: pastillesOnglets(ref, widget.role),
        ),
      ),
    );
  }
}

/// Fondu bref au changement d'onglet (les onglets gardent leur état).
class _Fondu extends StatelessWidget {
  const _Fondu({required this.cle, required this.child});

  final OngletRole cle;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    if (context.animationsReduites) return child;
    return TweenAnimationBuilder<double>(
      key: ValueKey(cle),
      tween: Tween<double>(begin: 0.4, end: 1),
      duration: Jetons.dureeNormale,
      curve: Jetons.courbe,
      builder: (_, opacite, enfant) => Opacity(opacity: opacite, child: enfant),
      child: child,
    );
  }
}
