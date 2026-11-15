import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/surfaces.dart';
import '../../../l10n/traductions.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../domain/modeles.dart';

// Éléments d'interface partagés par les écrans du stock : libellés traduits,
// pastille de niveau, jauge de seuils, carte de mouvement, choix d'article.

String libelleNiveau(Traductions t, NiveauStock niveau) => switch (niveau) {
  NiveauStock.vide => t.niveauVide,
  NiveauStock.critique => t.niveauCritique,
  NiveauStock.mini => t.niveauMini,
  NiveauStock.plein => t.niveauPlein,
};

Ton tonNiveau(NiveauStock niveau) => switch (niveau) {
  NiveauStock.vide => Ton.danger,
  NiveauStock.critique => Ton.danger,
  NiveauStock.mini => Ton.alerte,
  NiveauStock.plein => Ton.succes,
};

IconData iconeNiveau(NiveauStock niveau) => switch (niveau) {
  NiveauStock.vide => PhosphorIconsRegular.prohibit,
  NiveauStock.critique => PhosphorIconsRegular.warningCircle,
  NiveauStock.mini => PhosphorIconsRegular.warning,
  NiveauStock.plein => PhosphorIconsRegular.checkCircle,
};

String libelleType(Traductions t, TypeMouvement type) => switch (type) {
  TypeMouvement.reception => t.typeReception,
  TypeMouvement.sortieLogement => t.typeSortie,
  TypeMouvement.retour => t.typeRetour,
  TypeMouvement.perte => t.typePerte,
  TypeMouvement.ajustement => t.typeAjustement,
};

IconData iconeType(TypeMouvement type) => switch (type) {
  TypeMouvement.reception => PhosphorIconsRegular.truck,
  TypeMouvement.sortieLogement => PhosphorIconsRegular.signOut,
  TypeMouvement.retour => PhosphorIconsRegular.arrowUUpLeft,
  TypeMouvement.perte => PhosphorIconsRegular.trashSimple,
  TypeMouvement.ajustement => PhosphorIconsRegular.listChecks,
};

String libelleStatut(Traductions t, StatutMouvement statut) => switch (statut) {
  StatutMouvement.enregistre => t.statutEnregistre,
  StatutMouvement.aValider => t.statutAValider,
  StatutMouvement.valide => t.statutValide,
  StatutMouvement.rejete => t.statutRejete,
};

Ton tonStatut(StatutMouvement statut) => switch (statut) {
  StatutMouvement.enregistre => Ton.neutre,
  StatutMouvement.aValider => Ton.alerte,
  StatutMouvement.valide => Ton.succes,
  StatutMouvement.rejete => Ton.danger,
};

/// « À l'instant », « il y a 15 min », « il y a 3 h », puis la date.
String tempsRelatif(BuildContext context, DateTime date) {
  final t = context.t;
  final ecart = DateTime.now().difference(date);
  if (ecart.inMinutes < 1) return t.aLInstant;
  if (ecart.inMinutes < 60) return t.ilYAMinutes(ecart.inMinutes);
  if (ecart.inHours < 24) return t.ilYAHeures(ecart.inHours);
  final langue = Localizations.localeOf(context).toLanguageTag();
  return DateFormat.MMMd(langue).add_Hm().format(date);
}

/// Message bref en bas d'écran, après une action réussie ou refusée.
void notifier(BuildContext context, String message) {
  ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(SnackBar(content: Text(message)));
}

/// Pastille de niveau de stock : icône + libellé, jamais la couleur seule.
class PastilleNiveau extends StatelessWidget {
  const PastilleNiveau(this.article, {super.key});

  final ArticleStock article;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    if (article.estNegatif) {
      return Pastille(
        libelle: t.stockNegatif,
        icone: PhosphorIconsRegular.warningOctagon,
        ton: Ton.danger,
        pleine: true,
      );
    }
    return Pastille(
      libelle: libelleNiveau(t, article.niveau),
      icone: iconeNiveau(article.niveau),
      ton: tonNiveau(article.niveau),
    );
  }
}

/// Jauge de seuils à quatre niveaux (charte § 6) : Vide / Critique / Mini /
/// Plein, avec la position du stock réel. Un stock négatif est dit en clair.
class JaugeSeuils extends StatelessWidget {
  const JaugeSeuils(this.article, {super.key});

  final ArticleStock article;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final capacite = article.capacite <= 0 ? 1 : article.capacite;
    double part(num valeur) => (valeur / capacite).clamp(0.0, 1.0).toDouble();
    final critique = part(article.seuilCritique);
    final mini = part(article.seuilMinimal);
    final ton = tonNiveau(article.niveau);

    Widget repere(String valeur, String libelle, TextAlign alignement) =>
        Expanded(
          child: Column(
            crossAxisAlignment: switch (alignement) {
              TextAlign.left => CrossAxisAlignment.start,
              TextAlign.right => CrossAxisAlignment.end,
              _ => CrossAxisAlignment.center,
            },
            children: [
              Text(
                valeur,
                style: TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 12.5,
                  color: p.texte,
                ),
              ),
              Text(
                libelle,
                style: TextStyle(fontSize: 11.5, color: p.texteSecondaire),
              ),
            ],
          ),
        );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: SizedBox(
            height: 14,
            child: Stack(
              fit: StackFit.expand,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(
                      flex: (critique * 1000).round().clamp(1, 1000),
                      child: ColoredBox(color: p.dangerFond),
                    ),
                    Expanded(
                      flex: ((mini - critique) * 1000).round().clamp(1, 1000),
                      child: ColoredBox(color: p.orFond),
                    ),
                    Expanded(
                      flex: ((1 - mini) * 1000).round().clamp(1, 1000),
                      child: ColoredBox(color: p.accentFond),
                    ),
                  ],
                ),
                TweenAnimationBuilder<double>(
                  tween: Tween<double>(end: part(article.quantite)),
                  duration: context.animationsReduites
                      ? Duration.zero
                      : const Duration(milliseconds: 420),
                  curve: Jetons.courbe,
                  builder: (_, v, _) => Transform.scale(
                    scaleX: v,
                    alignment: Alignment.centerLeft,
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        color: ton.texte(p),
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            repere('0', t.niveauVide, TextAlign.left),
            repere(
              formaterQuantite(article.seuilCritique),
              t.niveauCritique,
              TextAlign.center,
            ),
            repere(
              formaterQuantite(article.seuilMinimal),
              t.niveauMini,
              TextAlign.center,
            ),
            repere(
              formaterQuantite(article.capacite),
              t.jaugeCapacite,
              TextAlign.right,
            ),
          ],
        ),
        if (article.estNegatif) ...[
          const SizedBox(height: 10),
          Bloc(
            couleur: p.dangerFond,
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Icon(
                  PhosphorIconsRegular.warningOctagon,
                  color: p.danger,
                  size: 20,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    t.stockNegatifExplication,
                    style: TextStyle(
                      color: p.danger,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}

/// Rappel de l'article concerné par une saisie, avec son stock actuel.
class ResumeArticle extends StatelessWidget {
  const ResumeArticle(this.article, {this.onChanger, super.key});

  final ArticleStock article;
  final VoidCallback? onChanger;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    return Bloc(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          TuileIcone(
            icone: PhosphorIconsRegular.package,
            ton: tonNiveau(article.niveau),
            taille: 46,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  article.designation,
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 15,
                    color: p.texte,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '${article.code} · ${t.stockActuel(formaterQuantite(article.quantite, article.unite))}',
                  style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                ),
              ],
            ),
          ),
          if (onChanger != null)
            TextButton(onPressed: onChanger, child: Text(t.changer)),
        ],
      ),
    );
  }
}

/// Carte d'un mouvement dans un journal : sens, bon, quantité signée, état.
class CarteMouvement extends StatelessWidget {
  const CarteMouvement(
    this.mouvement, {
    this.afficherArticle = true,
    super.key,
  });

  final MouvementStock mouvement;
  final bool afficherArticle;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final sortie = mouvement.sens == SensMouvement.sortie;
    final couleur = sortie ? p.danger : p.succes;
    final detail = [
      if (mouvement.destination != null) mouvement.destination!,
      if (mouvement.reference != null) mouvement.reference!,
      if (mouvement.motif != null) mouvement.motif!,
    ].join(' · ');

    return Carte(
      padding: const EdgeInsets.all(14),
      child: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TuileIcone(
                icone: iconeType(mouvement.type),
                ton: sortie ? Ton.danger : Ton.succes,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${libelleType(t, mouvement.type)} · ${mouvement.numero}',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: p.texte,
                      ),
                    ),
                    if (afficherArticle)
                      Text(
                        mouvement.designation,
                        style: TextStyle(
                          color: p.texteSecondaire,
                          fontSize: 13,
                          height: 1.3,
                        ),
                      ),
                    if (detail.isNotEmpty)
                      Text(
                        detail,
                        style: TextStyle(
                          color: p.texteSecondaire,
                          fontSize: 12.5,
                          height: 1.3,
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '${sortie ? '−' : '+'}${formaterQuantite(mouvement.quantite, mouvement.unite)}',
                style: TextStyle(
                  color: couleur,
                  fontWeight: FontWeight.w800,
                  fontSize: 16,
                  fontFeatures: const [FontFeature.tabularFigures()],
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Divider(color: p.bordure),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(PhosphorIconsRegular.user, size: 14, color: p.texteAttenue),
              const SizedBox(width: 5),
              Expanded(
                child: Text(
                  '${mouvement.nomAuteur} · ${tempsRelatif(context, mouvement.date)}',
                  style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                ),
              ),
              Pastille(
                libelle: libelleStatut(t, mouvement.statut),
                ton: tonStatut(mouvement.statut),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Zone d'action collée en bas d'un écran de saisie (bouton principal).
class ZoneAction extends StatelessWidget {
  const ZoneAction({required this.child, this.mention, super.key});

  final Widget child;
  final String? mention;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Container(
      decoration: BoxDecoration(
        color: p.surface,
        border: Border(top: BorderSide(color: p.bordure)),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(
            Jetons.espace3,
            12,
            Jetons.espace3,
            12,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              child,
              if (mention != null) ...[
                const SizedBox(height: 8),
                Text(
                  mention!,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: p.texteSecondaire, fontSize: 12),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Feuille de choix d'un article, avec recherche par nom ou par code.
Future<ArticleStock?> choisirArticle(
  BuildContext context,
  List<ArticleStock> articles,
) {
  return showModalBottomSheet<ArticleStock>(
    context: context,
    isScrollControlled: true,
    builder: (_) => _FeuilleArticles(articles),
  );
}

class _FeuilleArticles extends StatefulWidget {
  const _FeuilleArticles(this.articles);

  final List<ArticleStock> articles;

  @override
  State<_FeuilleArticles> createState() => _FeuilleArticlesState();
}

class _FeuilleArticlesState extends State<_FeuilleArticles> {
  String _recherche = '';

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final filtre = _recherche.toLowerCase();
    final resultats = widget.articles
        .where(
          (a) =>
              a.designation.toLowerCase().contains(filtre) ||
              a.code.toLowerCase().contains(filtre),
        )
        .toList();

    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.viewInsetsOf(context).bottom),
      child: SizedBox(
        height: MediaQuery.sizeOf(context).height * 0.72,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: Jetons.espace3),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                t.choisirArticleTitre,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: p.sombre ? p.texte : Jetons.marine,
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                autofocus: false,
                onChanged: (v) => setState(() => _recherche = v),
                decoration: InputDecoration(
                  hintText: t.rechercherArticle,
                  prefixIcon: const Icon(PhosphorIconsRegular.magnifyingGlass),
                ),
              ),
              const SizedBox(height: 12),
              Expanded(
                child: resultats.isEmpty
                    ? EtatVide(
                        icone: PhosphorIconsRegular.magnifyingGlass,
                        titre: t.aucunResultat,
                      )
                    : ListView.separated(
                        itemCount: resultats.length,
                        separatorBuilder: (_, _) => const SizedBox(height: 8),
                        itemBuilder: (_, i) {
                          final article = resultats[i];
                          return Appui(
                            onTap: () => Navigator.of(context).pop(article),
                            echelle: 0.985,
                            child: Bloc(
                              padding: const EdgeInsets.all(12),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          article.designation,
                                          style: TextStyle(
                                            fontWeight: FontWeight.w700,
                                            color: p.texte,
                                          ),
                                        ),
                                        Text(
                                          '${article.code} · ${formaterQuantite(article.quantite, article.unite)}',
                                          style: TextStyle(
                                            color: p.texteSecondaire,
                                            fontSize: 12.5,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  PastilleNiveau(article),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
