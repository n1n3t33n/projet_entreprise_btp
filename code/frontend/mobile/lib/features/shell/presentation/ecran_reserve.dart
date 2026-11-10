import 'package:flutter/material.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../theme/jetons.dart';

/// Emplacement réservé : écran métier non encore livré en M1 (stock → M2,
/// avancement → M3). Évite tout jargon technique, conformément à la charte.
class EcranReserve extends StatelessWidget {
  const EcranReserve({required this.libelle, super.key});

  final String libelle;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(Jetons.espace4),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              PhosphorIconsRegular.clockCountdown,
              size: 48,
              color: Jetons.texteAttenue,
            ),
            const SizedBox(height: Jetons.espace3),
            Text(
              libelle,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: Jetons.espace2),
            const Text(
              'Disponible à un prochain jalon.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Jetons.texteSecondaire),
            ),
          ],
        ),
      ),
    );
  }
}
