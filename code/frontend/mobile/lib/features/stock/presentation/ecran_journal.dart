import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/en_tetes.dart';
import '../../../components/saisie.dart';
import '../../../components/surfaces.dart';
import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../shell/presentation/barre_navigation.dart';
import '../application/etat_stock.dart';
import '../domain/modeles.dart';
import 'elements_stock.dart';

enum _Sens { tous, sorties, entrees }

/// Journal des mouvements (écran 10) : recherche, filtre par sens, indicateurs
/// du jour, mouvements regroupés par jour. Le journal est en lecture seule.
class EcranJournal extends ConsumerStatefulWidget {
  const EcranJournal({this.racine = false, this.codeArticle, super.key});

  final bool racine;

  /// Restreint le journal à un article (ouvert depuis sa fiche).
  final String? codeArticle;

  @override
  ConsumerState<EcranJournal> createState() => _EcranJournalState();
}

class _EcranJournalState extends ConsumerState<EcranJournal> {
  _Sens _sens = _Sens.tous;
  String _recherche = '';

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final langue = Localizations.localeOf(context).toLanguageTag();
    final tous =
        (ref.watch(mouvementsProvider).valueOrNull ?? const <MouvementStock>[])
            .where(
              (m) =>
                  widget.codeArticle == null ||
                  m.codeArticle == widget.codeArticle,
            )
            .toList();
    final recherche = _recherche.toLowerCase();
    final visibles = tous.where((m) {
      final sensOk = switch (_sens) {
        _Sens.tous => true,
        _Sens.sorties => m.sens == SensMouvement.sortie,
        _Sens.entrees => m.sens == SensMouvement.entree,
      };
      final texte =
          '${m.numero} ${m.designation} ${m.destination ?? ''} ${m.reference ?? ''} ${m.nomAuteur}'
              .toLowerCase();
      return sensOk && texte.contains(recherche);
    }).toList();

    final maintenant = DateTime.now();
    bool memeJour(DateTime a, DateTime b) =>
        a.year == b.year && a.month == b.month && a.day == b.day;
    final duJour = tous.where((m) => memeJour(m.date, maintenant)).toList();

    String titreJour(DateTime date) {
      if (memeJour(date, maintenant)) return t.aujourdhui;
      if (memeJour(date, maintenant.subtract(const Duration(days: 1)))) {
        return t.hier;
      }
      return DateFormat.yMMMMd(langue).format(date);
    }

    final elements = <Widget>[];
    DateTime? jourCourant;
    var rang = 0;
    for (final mouvement in visibles) {
      if (jourCourant == null || !memeJour(jourCourant, mouvement.date)) {
        jourCourant = mouvement.date;
        elements.add(
          Padding(
            padding: const EdgeInsets.only(top: 8, bottom: 10),
            child: Text(
              titreJour(mouvement.date),
              style: TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 15,
                color: p.sombre ? p.texte : Jetons.marine,
              ),
            ),
          ),
        );
      }
      elements
        ..add(
          Apparition(
            key: ValueKey(mouvement.uuid),
            rang: rang++,
            child: CarteMouvement(mouvement),
          ),
        )
        ..add(const SizedBox(height: 10));
    }

    return Scaffold(
      appBar: BarreEcran(
        titre: t.journalTitre,
        sousTitre: widget.codeArticle ?? t.journalSousTitre,
      ),
      body: ListView(
        padding: EdgeInsets.fromLTRB(
          Jetons.margeMobile,
          Jetons.margeMobile,
          Jetons.margeMobile,
          widget.racine ? espaceBarreBasse : 24,
        ),
        children: [
          TextField(
            onChanged: (v) => setState(() => _recherche = v),
            decoration: InputDecoration(
              hintText: t.journalRecherche,
              prefixIcon: const Icon(PhosphorIconsRegular.magnifyingGlass),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              for (final (sens, libelle, icone) in [
                (_Sens.tous, t.filtreTous, PhosphorIconsRegular.stack),
                (
                  _Sens.sorties,
                  t.filtreSorties,
                  PhosphorIconsRegular.arrowUpRight,
                ),
                (
                  _Sens.entrees,
                  t.filtreEntrees,
                  PhosphorIconsRegular.arrowDownLeft,
                ),
              ]) ...[
                PuceChoix(
                  libelle: libelle,
                  icone: icone,
                  selectionnee: _sens == sens,
                  onTap: () => setState(() => _sens = sens),
                ),
                const SizedBox(width: 8),
              ],
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _Indicateur(
                  valeur: duJour.length,
                  libelle: t.mouvementsDuJour,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _Indicateur(
                  valeur: duJour
                      .where((m) => m.sens == SensMouvement.entree)
                      .length,
                  libelle: t.entreesDuJour,
                  ton: Ton.succes,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _Indicateur(
                  valeur: ref.watch(nombreEnAttenteProvider),
                  libelle: t.etatEnAttenteEnvoi,
                  ton: Ton.alerte,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          if (visibles.isEmpty)
            EtatVide(
              icone: PhosphorIconsRegular.clockCounterClockwise,
              titre: t.aucunMouvement,
              texte: t.aucunMouvementAide,
            ),
          ...elements,
          if (visibles.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    PhosphorIconsRegular.lockSimple,
                    size: 14,
                    color: p.texteAttenue,
                  ),
                  const SizedBox(width: 6),
                  Flexible(
                    child: Text(
                      t.journalNonModifiable,
                      style: TextStyle(
                        color: p.texteSecondaire,
                        fontSize: 12.5,
                      ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _Indicateur extends StatelessWidget {
  const _Indicateur({
    required this.valeur,
    required this.libelle,
    this.ton = Ton.marine,
  });

  final int valeur;
  final String libelle;
  final Ton ton;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Carte(
      padding: const EdgeInsets.all(12),
      rayon: Jetons.rayonBloc,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          NombreAnime(
            valeur: valeur,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w800,
              height: 1.1,
              color: ton.texte(p),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            libelle,
            style: TextStyle(
              color: p.texteSecondaire,
              fontSize: 12,
              height: 1.25,
            ),
          ),
        ],
      ),
    );
  }
}
