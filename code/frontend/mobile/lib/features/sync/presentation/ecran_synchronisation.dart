import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/boutons.dart';
import '../../../components/en_tetes.dart';
import '../../../components/saisie.dart';
import '../../../components/surfaces.dart';
import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../shell/presentation/barre_navigation.dart';
import '../data/depot_file_envoi.dart';
import '../data/moteur_synchronisation.dart';

/// Centre de synchronisation (écran 17) : état simple et sans jargon (charte
/// § 6, § 8). Envoi de la file d'attente, écarts à arbitrer, détail des envois.
class EcranSynchronisation extends ConsumerStatefulWidget {
  const EcranSynchronisation({this.autonome = false, super.key});

  /// Vrai quand l'écran est ouvert par-dessus un autre (avec bouton retour).
  final bool autonome;

  @override
  ConsumerState<EcranSynchronisation> createState() =>
      _EcranSynchronisationState();
}

class _EcranSynchronisationState extends ConsumerState<EcranSynchronisation> {
  bool _enCours = false;

  Future<void> _synchroniser() async {
    setState(() => _enCours = true);
    // Délai court : l'opérateur doit voir que l'envoi a bien eu lieu.
    await Future<void>.delayed(const Duration(milliseconds: 600));
    final envoyes = await ref
        .read(moteurSynchronisationProvider)
        .synchroniser();
    ref
      ..invalidate(fileEnvoiProvider)
      ..invalidate(etatSynchronisationProvider);
    HapticFeedback.mediumImpact();
    if (!mounted) return;
    setState(() => _enCours = false);
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(content: Text(context.t.synchroTerminee(envoyes))),
      );
  }

  Future<void> _resoudre(String id, ResolutionConflit resolution) async {
    await ref.read(moteurSynchronisationProvider).resoudre(id, resolution);
    ref
      ..invalidate(fileEnvoiProvider)
      ..invalidate(etatSynchronisationProvider);
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final langue = Localizations.localeOf(context).toLanguageTag();
    final file =
        ref.watch(fileEnvoiProvider).valueOrNull ?? const <EvenementEnFile>[];
    final enAttente = ref.watch(nombreEnAttenteProvider);
    final etat = ref.watch(etatSynchronisationProvider).valueOrNull;
    final derniere = etat?.derniere;
    final conflits = etat?.conflits ?? const <ConflitSynchronisation>[];

    return Scaffold(
      appBar: BarreEcran(
        titre: t.synchroTitre,
        sousTitre: t.donneesSurAppareil,
      ),
      body: ListView(
        padding: EdgeInsets.fromLTRB(
          Jetons.margeMobile,
          Jetons.margeMobile,
          Jetons.margeMobile,
          widget.autonome ? 24 : espaceBarreBasse,
        ),
        children: [
          Apparition(
            child: Carte(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      const TuileIcone(
                        icone: PhosphorIconsRegular.shieldCheck,
                        ton: Ton.marine,
                        taille: 48,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              t.donneesSurAppareil,
                              style: TextStyle(
                                fontWeight: FontWeight.w800,
                                fontSize: 17,
                                color: p.sombre ? p.texte : Jetons.marine,
                              ),
                            ),
                            Text(
                              t.synchroExplication,
                              style: TextStyle(
                                color: p.texteSecondaire,
                                fontSize: 13,
                                height: 1.35,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        child: Bloc(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                t.derniereSynchro,
                                style: TextStyle(
                                  color: p.texteSecondaire,
                                  fontSize: 12.5,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                derniere == null
                                    ? t.jamais
                                    : DateFormat.MMMd(
                                        langue,
                                      ).add_Hm().format(derniere),
                                style: TextStyle(
                                  fontWeight: FontWeight.w800,
                                  color: p.texte,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Bloc(
                          couleur: enAttente > 0 ? p.orFond : p.succesFond,
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                t.etatEnAttenteEnvoi,
                                style: TextStyle(
                                  color: p.texteSecondaire,
                                  fontSize: 12.5,
                                ),
                              ),
                              const SizedBox(height: 2),
                              NombreAnime(
                                valeur: enAttente,
                                style: TextStyle(
                                  fontWeight: FontWeight.w800,
                                  fontSize: 18,
                                  color: enAttente > 0 ? p.or : p.succes,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  BoutonPrincipal(
                    libelle: enAttente > 0
                        ? t.synchroniserMaintenant
                        : t.synchroAJour,
                    icone: PhosphorIconsBold.arrowsClockwise,
                    enChargement: _enCours,
                    onPressed: enAttente > 0 ? _synchroniser : null,
                  ),
                ],
              ),
            ),
          ),
          if (conflits.isNotEmpty) ...[
            const SizedBox(height: Jetons.espace4),
            TitreSection(
              t.conflitsTitre,
              icone: PhosphorIconsRegular.warningOctagon,
              complement: Pastille(
                libelle: '${conflits.length}',
                ton: Ton.danger,
              ),
            ),
            const SizedBox(height: 10),
            for (final conflit in conflits)
              Apparition(
                rang: 1,
                child: Carte(
                  bordure: p.danger.withValues(alpha: 0.4),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        conflit.article,
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 16,
                          color: p.texte,
                        ),
                      ),
                      Text(
                        t.conflitExplication,
                        style: TextStyle(
                          color: p.danger,
                          fontSize: 13,
                          height: 1.35,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: _Version(
                              icone: PhosphorIconsRegular.deviceMobile,
                              libelle: t.cetAppareil,
                              valeur: conflit.valeurAppareil,
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: _Version(
                              icone: PhosphorIconsRegular.buildings,
                              libelle: t.serveur,
                              valeur: conflit.valeurServeur,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      CarteOption(
                        titre: t.resolutionServeur,
                        detail: t.resolutionServeurDetail,
                        icone: PhosphorIconsRegular.buildings,
                        selectionnee: false,
                        onTap: () => _resoudre(
                          conflit.id,
                          ResolutionConflit.prioriteServeur,
                        ),
                      ),
                      const SizedBox(height: 8),
                      CarteOption(
                        titre: t.resolutionLocale,
                        detail: t.resolutionLocaleDetail,
                        icone: PhosphorIconsRegular.deviceMobile,
                        ton: Ton.alerte,
                        selectionnee: false,
                        onTap: () => _resoudre(
                          conflit.id,
                          ResolutionConflit.versionLocale,
                        ),
                      ),
                      const SizedBox(height: 8),
                      CarteOption(
                        titre: t.resolutionArbitrage,
                        detail: t.resolutionArbitrageDetail,
                        icone: PhosphorIconsRegular.scales,
                        ton: Ton.neutre,
                        selectionnee: false,
                        onTap: () =>
                            _resoudre(conflit.id, ResolutionConflit.arbitrage),
                      ),
                    ],
                  ),
                ),
              ),
          ],
          const SizedBox(height: Jetons.espace4),
          TitreSection(
            t.fileAttenteTitre,
            icone: PhosphorIconsRegular.tray,
            complement: file.isEmpty
                ? null
                : Pastille(libelle: '${file.length}'),
          ),
          const SizedBox(height: 10),
          if (file.isEmpty)
            EtatVide(
              icone: PhosphorIconsRegular.tray,
              titre: t.fileVideTitre,
              texte: t.fileVideTexte,
            ),
          for (final (rang, evenement) in file.take(30).indexed) ...[
            Apparition(
              key: ValueKey(evenement.uuid),
              rang: rang + 2,
              child: Carte(
                padding: const EdgeInsets.all(12),
                rayon: Jetons.rayonBloc,
                avecOmbre: false,
                child: Row(
                  children: [
                    TuileIcone(
                      icone: evenement.enAttente
                          ? PhosphorIconsRegular.hourglassMedium
                          : PhosphorIconsRegular.check,
                      ton: evenement.enAttente ? Ton.alerte : Ton.succes,
                      taille: 40,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            evenement.resume,
                            style: TextStyle(
                              fontWeight: FontWeight.w700,
                              fontSize: 13.5,
                              color: p.texte,
                            ),
                          ),
                          Text(
                            DateFormat.MMMd(
                              langue,
                            ).add_Hm().format(evenement.creeLe),
                            style: TextStyle(
                              color: p.texteSecondaire,
                              fontSize: 12.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Pastille(
                      libelle: evenement.enAttente
                          ? t.etatEnAttenteEnvoi
                          : t.etatEnvoye,
                      ton: evenement.enAttente ? Ton.alerte : Ton.succes,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
          ],
        ],
      ),
    );
  }
}

class _Version extends StatelessWidget {
  const _Version({
    required this.icone,
    required this.libelle,
    required this.valeur,
  });

  final IconData icone;
  final String libelle;
  final String valeur;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Bloc(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icone, size: 16, color: p.accent),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  libelle,
                  style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            valeur,
            style: TextStyle(
              fontWeight: FontWeight.w800,
              fontSize: 16,
              color: p.texte,
            ),
          ),
        ],
      ),
    );
  }
}
