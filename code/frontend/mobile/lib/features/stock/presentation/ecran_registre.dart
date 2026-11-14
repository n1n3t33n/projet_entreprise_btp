import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/boutons.dart';
import '../../../components/en_tetes.dart';
import '../../../components/saisie.dart';
import '../../../components/surfaces.dart';
import '../../../core/navigation/transitions.dart';
import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../shell/presentation/barre_navigation.dart';
import '../application/etat_stock.dart';
import '../data/donnees_demo.dart';
import '../domain/modeles.dart';
import 'ecran_journal.dart';
import 'ecran_mouvement.dart';
import 'elements_stock.dart';

enum _Filtre { tous, sousSeuil, critique, negatif }

/// Propose les trois saisies possibles (sortie, réception, retour ou perte).
Future<void> ouvrirNouveauMouvement(
  BuildContext context, {
  ArticleStock? article,
}) async {
  final t = context.t;
  final mode = await showModalBottomSheet<ModeSaisie>(
    context: context,
    builder: (contexte) => SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          Jetons.espace3,
          0,
          Jetons.espace3,
          Jetons.espace3,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            for (final (mode, titre, detail, icone, ton) in [
              (
                ModeSaisie.sortie,
                t.sortieTitre,
                t.sortieAide,
                PhosphorIconsRegular.signOut,
                Ton.marine,
              ),
              (
                ModeSaisie.reception,
                t.receptionTitre,
                t.receptionAide,
                PhosphorIconsRegular.truck,
                Ton.info,
              ),
              (
                ModeSaisie.retour,
                t.retourTitre,
                t.retourAide,
                PhosphorIconsRegular.arrowUUpLeft,
                Ton.alerte,
              ),
            ]) ...[
              CarteOption(
                titre: titre,
                detail: detail,
                icone: icone,
                ton: ton,
                selectionnee: false,
                onTap: () => Navigator.of(contexte).pop(mode),
              ),
              const SizedBox(height: 8),
            ],
          ],
        ),
      ),
    ),
  );
  if (mode != null && context.mounted) {
    await ouvrirEcran<void>(
      context,
      EcranMouvement(mode: mode, article: article),
    );
  }
}

/// Registre du stock (écran 3) : recherche, filtres par niveau, cartes article.
class EcranRegistre extends ConsumerStatefulWidget {
  const EcranRegistre({
    this.racine = false,
    this.filtreAlertes = false,
    super.key,
  });

  /// Vrai quand l'écran est la racine d'un onglet (barre basse visible).
  final bool racine;

  /// Vrai pour ouvrir directement sur les articles sous seuil.
  final bool filtreAlertes;

  @override
  ConsumerState<EcranRegistre> createState() => _EcranRegistreState();
}

class _EcranRegistreState extends ConsumerState<EcranRegistre> {
  late _Filtre _filtre = widget.filtreAlertes
      ? _Filtre.sousSeuil
      : _Filtre.tous;
  String _recherche = '';

  bool _correspond(ArticleStock a, _Filtre filtre) => switch (filtre) {
    _Filtre.tous => true,
    _Filtre.sousSeuil => a.sousSeuil,
    _Filtre.critique =>
      a.niveau == NiveauStock.critique || a.niveau == NiveauStock.vide,
    _Filtre.negatif => a.estNegatif,
  };

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final role = ref.watch(operateurProvider)?.role;
    final articles =
        ref.watch(articlesProvider).valueOrNull ?? const <ArticleStock>[];
    final recherche = _recherche.toLowerCase();
    final visibles = articles
        .where((a) => _correspond(a, _filtre))
        .where(
          (a) =>
              a.designation.toLowerCase().contains(recherche) ||
              a.code.toLowerCase().contains(recherche) ||
              a.famille.toLowerCase().contains(recherche),
        )
        .toList();
    final peutSaisir = role?.peutSaisirStock ?? false;

    return Scaffold(
      appBar: BarreEcran(titre: t.registreTitre, sousTitre: magasinPilote),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: peutSaisir
          ? Padding(
              padding: EdgeInsets.only(
                left: Jetons.espace3,
                right: Jetons.espace3,
                bottom: widget.racine ? 84 : 0,
              ),
              child: BoutonPrincipal(
                libelle: t.nouveauMouvement,
                icone: PhosphorIconsBold.plus,
                onPressed: () => ouvrirNouveauMouvement(context),
              ),
            )
          : null,
      body: ListView(
        padding: EdgeInsets.fromLTRB(
          Jetons.margeMobile,
          Jetons.margeMobile,
          Jetons.margeMobile,
          (widget.racine ? espaceBarreBasse : 24) + (peutSaisir ? 72 : 0),
        ),
        children: [
          Carte(
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        t.registreTitre,
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w800,
                          color: p.sombre ? p.texte : Jetons.marine,
                        ),
                      ),
                      Text(
                        t.registreSousTitre,
                        style: TextStyle(
                          color: p.texteSecondaire,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    NombreAnime(
                      valeur: articles.length,
                      style: TextStyle(
                        fontSize: 30,
                        fontWeight: FontWeight.w800,
                        height: 1,
                        color: p.sombre ? p.texte : Jetons.marine,
                      ),
                    ),
                    Text(
                      t.references,
                      style: TextStyle(
                        color: p.texteSecondaire,
                        fontSize: 12.5,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            onChanged: (v) => setState(() => _recherche = v),
            decoration: InputDecoration(
              hintText: t.rechercherArticle,
              prefixIcon: const Icon(PhosphorIconsRegular.magnifyingGlass),
            ),
          ),
          const SizedBox(height: 12),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                for (final (filtre, libelle, ton) in [
                  (_Filtre.tous, t.filtreTous, Ton.marine),
                  (_Filtre.sousSeuil, t.filtreSousSeuil, Ton.alerte),
                  (_Filtre.critique, t.niveauCritique, Ton.danger),
                  (_Filtre.negatif, t.stockNegatif, Ton.danger),
                ]) ...[
                  PuceChoix(
                    libelle: libelle,
                    ton: ton,
                    compteur: articles
                        .where((a) => _correspond(a, filtre))
                        .length,
                    selectionnee: _filtre == filtre,
                    onTap: () => setState(() => _filtre = filtre),
                  ),
                  const SizedBox(width: 8),
                ],
              ],
            ),
          ),
          const SizedBox(height: 12),
          if (visibles.isEmpty)
            EtatVide(
              icone: PhosphorIconsRegular.magnifyingGlass,
              titre: t.aucunResultat,
              texte: t.aucunResultatAide,
            ),
          for (final (rang, article) in visibles.indexed) ...[
            Apparition(
              key: ValueKey(article.code),
              rang: rang,
              child: _CarteArticle(article),
            ),
            const SizedBox(height: 10),
          ],
        ],
      ),
    );
  }
}

class _CarteArticle extends StatelessWidget {
  const _CarteArticle(this.article);

  final ArticleStock article;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final ton = tonNiveau(article.niveau);
    final ecart = article.quantite - article.seuilMinimal;
    return Carte(
      onTap: () =>
          ouvrirEcran<void>(context, EcranFicheArticle(code: article.code)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  '${article.code} · ${article.famille}',
                  style: TextStyle(
                    color: p.accent,
                    fontWeight: FontWeight.w700,
                    fontSize: 12.5,
                  ),
                ),
              ),
              PastilleNiveau(article),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            article.designation,
            style: TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 16,
              color: p.texte,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                formaterQuantite(article.quantite),
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  height: 1,
                  color: article.sousSeuil
                      ? ton.texte(p)
                      : (p.sombre ? p.texte : Jetons.marine),
                  fontFeatures: const [FontFeature.tabularFigures()],
                ),
              ),
              const SizedBox(width: 6),
              Padding(
                padding: const EdgeInsets.only(bottom: 2),
                child: Text(
                  article.unite,
                  style: TextStyle(color: p.texteSecondaire),
                ),
              ),
              const Spacer(),
              Icon(PhosphorIconsRegular.clock, size: 13, color: p.texteAttenue),
              const SizedBox(width: 4),
              Text(
                tempsRelatif(context, article.majLe),
                style: TextStyle(color: p.texteSecondaire, fontSize: 12),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            article.sousSeuil
                ? t.seuilMiniEcart(
                    formaterQuantite(article.seuilMinimal, article.unite),
                    formaterQuantite(ecart),
                  )
                : t.stockConforme(formaterQuantite(article.seuilMinimal)),
            style: TextStyle(
              color: ton.texte(p),
              fontWeight: FontWeight.w600,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }
}

/// Fiche d'un article (écran 4) : quantité, jauge de seuils, actions, journal.
class EcranFicheArticle extends ConsumerWidget {
  const EcranFicheArticle({required this.code, super.key});

  final String code;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final articles =
        ref.watch(articlesProvider).valueOrNull ?? const <ArticleStock>[];
    final article = articles.where((a) => a.code == code).firstOrNull;
    final role = ref.watch(operateurProvider)?.role;
    final mouvements =
        (ref.watch(mouvementsProvider).valueOrNull ?? const <MouvementStock>[])
            .where((m) => m.codeArticle == code)
            .take(4)
            .toList();
    final enAttente = (ref.watch(fileEnvoiProvider).valueOrNull ?? const [])
        .where((e) => e.enAttente && e.chargeUtile['code_article'] == code)
        .length;

    if (article == null) {
      return Scaffold(
        appBar: BarreEcran(titre: t.ficheArticleTitre),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    void saisir(ModeSaisie mode) => ouvrirEcran<void>(
      context,
      EcranMouvement(mode: mode, article: article),
    );

    return Scaffold(
      appBar: BarreEcran(titre: t.ficheArticleTitre, sousTitre: magasinPilote),
      body: ListView(
        padding: const EdgeInsets.all(Jetons.margeMobile),
        children: [
          Apparition(
            child: Carte(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: [
                      Pastille(
                        libelle: article.code,
                        ton: Ton.marine,
                        pleine: true,
                      ),
                      Pastille(libelle: article.famille, ton: Ton.info),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    article.designation,
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      height: 1.2,
                      color: p.sombre ? p.texte : Jetons.marine,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        PhosphorIconsRegular.mapPin,
                        size: 15,
                        color: p.texteSecondaire,
                      ),
                      const SizedBox(width: 5),
                      Expanded(
                        child: Text(
                          article.emplacement,
                          style: TextStyle(
                            color: p.texteSecondaire,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: Jetons.espace3),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      NombreAnime(
                        valeur: article.quantite,
                        style: TextStyle(
                          fontSize: 44,
                          fontWeight: FontWeight.w800,
                          height: 1,
                          color: tonNiveau(article.niveau).texte(p),
                          fontFeatures: const [FontFeature.tabularFigures()],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.only(bottom: 5),
                          child: Text(
                            t.disponibles(article.unite),
                            style: TextStyle(
                              color: p.texteSecondaire,
                              fontSize: 15,
                            ),
                          ),
                        ),
                      ),
                      PastilleNiveau(article),
                    ],
                  ),
                  const SizedBox(height: Jetons.espace3),
                  JaugeSeuils(article),
                  if (enAttente > 0) ...[
                    const SizedBox(height: 12),
                    Bloc(
                      couleur: p.orFond,
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          Icon(
                            PhosphorIconsRegular.cloudArrowUp,
                            color: p.or,
                            size: 20,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              t.synchroEnAttente(enAttente),
                              style: TextStyle(
                                color: p.or,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          if (role?.peutSaisirStock ?? false) ...[
            const SizedBox(height: 12),
            Apparition(
              rang: 1,
              child: Row(
                children: [
                  Expanded(
                    child: TuileAction(
                      icone: PhosphorIconsRegular.signOut,
                      libelle: t.typeSortie,
                      ton: Ton.marine,
                      onTap: () => saisir(ModeSaisie.sortie),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TuileAction(
                      icone: PhosphorIconsRegular.truck,
                      libelle: t.typeReception,
                      onTap: () => saisir(ModeSaisie.reception),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TuileAction(
                      icone: PhosphorIconsRegular.arrowUUpLeft,
                      libelle: t.retourCourt,
                      ton: Ton.alerte,
                      onTap: () => saisir(ModeSaisie.retour),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: Jetons.espace4),
          TitreSection(
            t.mouvementsRecents,
            icone: PhosphorIconsRegular.clockCounterClockwise,
            complement: TextButton(
              onPressed: () =>
                  ouvrirEcran<void>(context, EcranJournal(codeArticle: code)),
              child: Text(t.journalComplet),
            ),
          ),
          const SizedBox(height: 8),
          if (mouvements.isEmpty)
            EtatVide(
              icone: PhosphorIconsRegular.clockCounterClockwise,
              titre: t.aucunMouvement,
            ),
          for (final (rang, mouvement) in mouvements.indexed) ...[
            Apparition(
              rang: rang + 2,
              child: CarteMouvement(mouvement, afficherArticle: false),
            ),
            const SizedBox(height: 10),
          ],
          const SizedBox(height: 6),
          Bloc(
            child: Row(
              children: [
                const TuileIcone(
                  icone: PhosphorIconsRegular.barcode,
                  ton: Ton.neutre,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        t.codeBarres,
                        style: TextStyle(
                          fontWeight: FontWeight.w700,
                          color: p.texte,
                        ),
                      ),
                      Text(
                        article.codeBarre,
                        style: TextStyle(
                          color: p.texteSecondaire,
                          fontFeatures: const [FontFeature.tabularFigures()],
                        ),
                      ),
                    ],
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
