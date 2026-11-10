import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../core/providers.dart';
import '../../../theme/jetons.dart';

/// Centre de synchronisation : état simple et sans jargon (charte § 6, § 8).
///
/// En M1, aucun envoi réseau n'a lieu : on affiche seulement l'état de la file
/// locale. L'envoi effectif des lots viendra avec les écrans métier.
class EcranSynchronisation extends ConsumerWidget {
  const EcranSynchronisation({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final enAttente = ref.read(depotFileEnvoiProvider).compterEnAttente();

    return ListView(
      padding: const EdgeInsets.all(Jetons.margeMobile),
      children: [
        FutureBuilder<int>(
          future: enAttente,
          builder: (context, snapshot) {
            final nombre = snapshot.data ?? 0;
            return _Ligne(
              icone: PhosphorIconsRegular.tray,
              titre: 'En attente d\'envoi',
              valeur: snapshot.connectionState == ConnectionState.waiting
                  ? '…'
                  : '$nombre',
            );
          },
        ),
        const _Ligne(
          icone: PhosphorIconsRegular.clockCounterClockwise,
          titre: 'Dernière synchronisation',
          valeur: '—',
        ),
        const _Ligne(
          icone: PhosphorIconsRegular.wifiSlash,
          titre: 'Connexion',
          valeur: 'Hors-ligne (démonstration)',
        ),
      ],
    );
  }
}

class _Ligne extends StatelessWidget {
  const _Ligne({
    required this.icone,
    required this.titre,
    required this.valeur,
  });

  final IconData icone;
  final String titre;
  final String valeur;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(icone, color: Jetons.sarcelle),
        title: Text(titre),
        trailing: Text(
          valeur,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
    );
  }
}
