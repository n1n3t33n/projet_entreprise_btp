import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../core/providers.dart';
import '../theme/jetons.dart';
import '../theme/palette.dart';
import 'boutons.dart';
import 'surfaces.dart';

/// Bandeau de synchronisation (charte § 6) : état simple, sans jargon.
///
/// Deux états : des saisies attendent d'être envoyées (ambre, avec l'accès au
/// centre de synchronisation), ou tout est à jour (vert).
class BandeauSynchro extends ConsumerWidget {
  const BandeauSynchro({required this.onSynchroniser, super.key});

  final VoidCallback onSynchroniser;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final enAttente = ref.watch(nombreEnAttenteProvider);
    final aJour = enAttente == 0;

    return AnimatedSwitcher(
      duration: Jetons.dureeNormale,
      switchInCurve: Jetons.courbe,
      child: Container(
        key: ValueKey(aJour),
        padding: const EdgeInsets.fromLTRB(14, 10, 10, 10),
        decoration: BoxDecoration(
          color: aJour ? p.succesFond : p.orFond,
          borderRadius: BorderRadius.circular(Jetons.rayonBloc),
          border: Border.all(
            color: aJour ? p.succes.withValues(alpha: 0.25) : p.orBordure,
          ),
        ),
        child: Row(
          children: [
            Icon(
              aJour
                  ? PhosphorIconsFill.checkCircle
                  : PhosphorIconsRegular.cloudArrowUp,
              color: aJour ? p.succes : p.or,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    aJour ? t.synchroAJour : t.synchroEnAttente(enAttente),
                    style: TextStyle(
                      color: aJour ? p.succes : p.or,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  Text(
                    t.donneesSurAppareil,
                    style: TextStyle(
                      color: aJour ? p.succes : p.or,
                      fontSize: 12.5,
                    ),
                  ),
                ],
              ),
            ),
            if (!aJour) ...[
              const SizedBox(width: 8),
              BoutonSecondaire(
                libelle: t.synchroniser,
                icone: PhosphorIconsBold.arrowsClockwise,
                ton: Ton.alerte,
                compact: true,
                contour: true,
                onPressed: onSynchroniser,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
