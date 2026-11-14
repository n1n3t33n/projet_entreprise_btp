import 'package:flutter/material.dart';

import '../../theme/jetons.dart';
import '../../theme/palette.dart';

/// Ouvre un écran par-dessus l'écran courant : fondu et légère montée
/// (charte § 7, ≈ 240 ms). Si l'utilisateur a demandé de réduire les
/// animations, seul un fondu bref est conservé.
Future<T?> ouvrirEcran<T>(BuildContext context, Widget ecran) {
  final reduit = context.animationsReduites;
  return Navigator.of(context).push<T>(
    PageRouteBuilder<T>(
      transitionDuration: Jetons.dureeNormale,
      reverseTransitionDuration: Jetons.dureeMicro,
      pageBuilder: (_, _, _) => ecran,
      transitionsBuilder: (_, animation, _, child) {
        final courbe = CurvedAnimation(parent: animation, curve: Jetons.courbe);
        final fondu = FadeTransition(opacity: courbe, child: child);
        if (reduit) return fondu;
        return SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0, 0.04),
            end: Offset.zero,
          ).animate(courbe),
          child: fondu,
        );
      },
    ),
  );
}
