import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/en_tetes.dart';
import '../../../components/surfaces.dart';
import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../shell/presentation/barre_navigation.dart';
import '../data/depot_file_envoi.dart';

/// Centre de synchronisation : état simple et sans jargon (charte § 6, § 8).
///
/// Cette première version montre la file d'attente de l'appareil. L'envoi et
/// la résolution des écarts arrivent avec le module de synchronisation.
class EcranSynchronisation extends ConsumerWidget {
  const EcranSynchronisation({this.autonome = false, super.key});

  /// Vrai quand l'écran est ouvert par-dessus un autre (avec bouton retour).
  final bool autonome;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final file = ref.watch(fileEnvoiProvider);
    final enAttente = ref.watch(nombreEnAttenteProvider);

    return Scaffold(
      appBar: BarreEcran(
        titre: t.synchroTitre,
        sousTitre: t.donneesSurAppareil,
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(
          Jetons.margeMobile,
          Jetons.margeMobile,
          Jetons.margeMobile,
          espaceBarreBasse,
        ),
        children: [
          Apparition(
            child: Carte(
              child: Row(
                children: [
                  TuileIcone(
                    icone: enAttente == 0
                        ? PhosphorIconsRegular.checkCircle
                        : PhosphorIconsRegular.cloudArrowUp,
                    ton: enAttente == 0 ? Ton.succes : Ton.alerte,
                    taille: 52,
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          enAttente == 0
                              ? t.synchroAJour
                              : t.synchroEnAttente(enAttente),
                          style: const TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          t.synchroExplication,
                          style: TextStyle(
                            color: context.palette.texteSecondaire,
                            fontSize: 13,
                            height: 1.35,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: Jetons.espace4),
          TitreSection(t.fileAttenteTitre, icone: PhosphorIconsRegular.tray),
          const SizedBox(height: 12),
          file.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (_, _) => EtatVide(
              icone: PhosphorIconsRegular.warning,
              titre: t.erreurDonneesInaccessibles,
            ),
            data: (evenements) => evenements.isEmpty
                ? EtatVide(
                    icone: PhosphorIconsRegular.tray,
                    titre: t.fileVideTitre,
                    texte: t.fileVideTexte,
                  )
                : Column(
                    children: [
                      for (final (rang, evenement) in evenements.indexed) ...[
                        Apparition(
                          rang: rang + 1,
                          child: _LigneFile(evenement),
                        ),
                        const SizedBox(height: 10),
                      ],
                    ],
                  ),
          ),
        ],
      ),
    );
  }
}

class _LigneFile extends StatelessWidget {
  const _LigneFile(this.evenement);

  final EvenementEnFile evenement;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final langue = Localizations.localeOf(context).toLanguageTag();
    return Carte(
      padding: const EdgeInsets.all(14),
      child: Row(
        children: [
          TuileIcone(
            icone: evenement.enAttente
                ? PhosphorIconsRegular.hourglassMedium
                : PhosphorIconsRegular.check,
            ton: evenement.enAttente ? Ton.alerte : Ton.succes,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  evenement.resume,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                Text(
                  DateFormat.MMMd(langue).add_Hm().format(evenement.creeLe),
                  style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Pastille(
            libelle: evenement.enAttente ? t.etatEnAttenteEnvoi : t.etatEnvoye,
            ton: evenement.enAttente ? Ton.alerte : Ton.succes,
          ),
        ],
      ),
    );
  }
}
