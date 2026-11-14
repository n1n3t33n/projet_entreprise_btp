import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/boutons.dart';
import '../../../components/en_tetes.dart';
import '../../../components/feuille_pin.dart';
import '../../../components/saisie.dart';
import '../../../components/surfaces.dart';
import '../../../core/navigation/transitions.dart';
import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../shell/presentation/barre_navigation.dart';
import '../application/etat_stock.dart';
import '../data/depot_stock.dart';
import '../domain/modeles.dart';
import 'ecran_inventaire.dart';
import 'ecran_registre.dart';
import 'elements_stock.dart';

/// Validation des sorties et alertes de seuil (écran 9).
///
/// Une approbation se signe par le code PIN. Celui qui a saisi une sortie ne
/// peut pas l'approuver lui-même : la demande reste visible, mais verrouillée.
class EcranValidationStock extends ConsumerStatefulWidget {
  const EcranValidationStock({this.racine = false, super.key});

  final bool racine;

  @override
  ConsumerState<EcranValidationStock> createState() =>
      _EcranValidationStockState();
}

class _EcranValidationStockState extends ConsumerState<EcranValidationStock> {
  bool _alertes = false;

  Future<void> _decider(
    MouvementStock mouvement, {
    required bool accepte,
  }) async {
    final t = context.t;
    final operateur = ref.read(operateurProvider);
    if (operateur == null) return;
    if (accepte) {
      final signe = await demanderSignaturePin(
        context,
        objet: t.signatureSortie(
          mouvement.numero,
          formaterQuantite(mouvement.quantite, mouvement.unite),
        ),
      );
      if (!signe || !mounted) return;
    }
    try {
      await ref
          .read(depotStockProvider)
          .decider(
            mouvement.uuid,
            accepte: accepte,
            validateur: operateur.profil,
          );
      rafraichirStock(ref);
      HapticFeedback.mediumImpact();
      if (mounted) {
        notifier(context, accepte ? t.sortieApprouvee : t.sortieRefusee);
      }
    } on SeparationFonctionsException {
      if (mounted) notifier(context, t.separationFonctions);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final operateur = ref.watch(operateurProvider);
    final demandes = ref.watch(sortiesAValiderProvider);
    final alertes = ref.watch(alertesStockProvider);
    final articles =
        ref.watch(articlesProvider).valueOrNull ?? const <ArticleStock>[];
    final inventaire = ref.watch(inventaireProvider).valueOrNull;

    return Scaffold(
      appBar: BarreEcran(
        titre: t.validationTitre,
        sousTitre: t.validationSousTitre,
      ),
      body: ListView(
        padding: EdgeInsets.fromLTRB(
          Jetons.margeMobile,
          Jetons.margeMobile,
          Jetons.margeMobile,
          widget.racine ? espaceBarreBasse : 24,
        ),
        children: [
          Row(
            children: [
              Expanded(
                child: PuceChoix(
                  libelle: t.ongletDemandes,
                  compteur: demandes.length,
                  selectionnee: !_alertes,
                  onTap: () => setState(() => _alertes = false),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: PuceChoix(
                  libelle: t.ongletAlertes,
                  compteur: alertes.length,
                  ton: Ton.alerte,
                  selectionnee: _alertes,
                  onTap: () => setState(() => _alertes = true),
                ),
              ),
            ],
          ),
          const SizedBox(height: Jetons.espace3),
          if (!_alertes) ...[
            if (inventaire != null &&
                inventaire.statut == StatutInventaire.aValider) ...[
              Carte(
                onTap: () =>
                    ouvrirEcran<void>(context, const EcranInventaire()),
                child: Row(
                  children: [
                    const TuileIcone(
                      icone: PhosphorIconsRegular.listChecks,
                      ton: Ton.alerte,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            t.inventaireAValider,
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          Text(
                            t.inventaireEcarts(inventaire.ecarts.length),
                            style: TextStyle(
                              color: context.palette.texteSecondaire,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      PhosphorIconsRegular.caretRight,
                      color: context.palette.texteAttenue,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],
            if (demandes.isEmpty)
              EtatVide(
                icone: PhosphorIconsRegular.sealCheck,
                titre: t.aucuneDemande,
                texte: t.aucuneDemandeAide,
              ),
            for (final (rang, demande) in demandes.indexed) ...[
              Apparition(
                key: ValueKey(demande.uuid),
                rang: rang,
                child: _CarteDemande(
                  demande: demande,
                  article: articles
                      .where((a) => a.code == demande.codeArticle)
                      .firstOrNull,
                  propre: demande.idAuteur == operateur?.profil.idUtilisateur,
                  onApprouver: () => _decider(demande, accepte: true),
                  onRejeter: () => _decider(demande, accepte: false),
                ),
              ),
              const SizedBox(height: 12),
            ],
          ] else ...[
            if (alertes.isEmpty)
              EtatVide(
                icone: PhosphorIconsRegular.checkCircle,
                titre: t.aucuneAlerte,
                texte: t.aucuneAlerteAide,
              ),
            for (final (rang, article) in alertes.indexed) ...[
              Apparition(
                key: ValueKey(article.code),
                rang: rang,
                child: CarteAlerte(article),
              ),
              const SizedBox(height: 12),
            ],
          ],
        ],
      ),
    );
  }
}

class _CarteDemande extends StatelessWidget {
  const _CarteDemande({
    required this.demande,
    required this.article,
    required this.propre,
    required this.onApprouver,
    required this.onRejeter,
  });

  final MouvementStock demande;
  final ArticleStock? article;

  /// Vrai si l'opérateur est l'auteur de la demande (il ne peut pas décider).
  final bool propre;
  final VoidCallback onApprouver;
  final VoidCallback onRejeter;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final stock = article;
    final sousSeuil = stock != null && stock.sousSeuil;
    return Carte(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${t.typeSortie} ${demande.numero}',
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                        color: p.sombre ? p.texte : Jetons.marine,
                      ),
                    ),
                    Text(
                      tempsRelatif(context, demande.date),
                      style: TextStyle(
                        color: p.texteSecondaire,
                        fontSize: 12.5,
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    formaterQuantite(demande.quantite),
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.w800,
                      height: 1,
                      color: p.sombre ? p.texte : Jetons.marine,
                    ),
                  ),
                  Text(
                    demande.unite,
                    style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          Bloc(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                _Detail(
                  icone: PhosphorIconsRegular.package,
                  libelle: t.materiau,
                  valeur: demande.designation,
                ),
                const SizedBox(height: 8),
                _Detail(
                  icone: PhosphorIconsRegular.user,
                  libelle: t.demandeur,
                  valeur: demande.nomAuteur,
                ),
                if (demande.destination != null) ...[
                  const SizedBox(height: 8),
                  _Detail(
                    icone: PhosphorIconsRegular.houseLine,
                    libelle: t.affectation,
                    valeur: demande.destination!,
                  ),
                ],
              ],
            ),
          ),
          if (sousSeuil) ...[
            const SizedBox(height: 10),
            Bloc(
              couleur: p.orFond,
              padding: const EdgeInsets.all(12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(PhosphorIconsRegular.warning, color: p.or, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      t.avertissementSeuil(
                        formaterQuantite(stock.quantite, stock.unite),
                        formaterQuantite(stock.seuilMinimal, stock.unite),
                      ),
                      style: TextStyle(
                        color: p.or,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                        height: 1.35,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 12),
          if (propre)
            Bloc(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  Icon(
                    PhosphorIconsRegular.lockSimple,
                    color: p.texteSecondaire,
                    size: 20,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      t.separationFonctions,
                      style: TextStyle(
                        color: p.texteSecondaire,
                        fontSize: 13,
                        height: 1.35,
                      ),
                    ),
                  ),
                ],
              ),
            )
          else
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: BoutonSecondaire(
                    libelle: t.rejeter,
                    ton: Ton.danger,
                    contour: true,
                    onPressed: onRejeter,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  flex: 3,
                  child: BoutonPrincipal(
                    libelle: t.approuver,
                    icone: PhosphorIconsBold.sealCheck,
                    onPressed: onApprouver,
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }
}

class _Detail extends StatelessWidget {
  const _Detail({
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
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icone, size: 16, color: p.accent),
        const SizedBox(width: 8),
        Text(
          '$libelle  ',
          style: TextStyle(color: p.texteSecondaire, fontSize: 13),
        ),
        Expanded(
          child: Text(
            valeur,
            textAlign: TextAlign.right,
            style: TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 13,
              color: p.texte,
            ),
          ),
        ),
      ],
    );
  }
}

/// Carte d'alerte de seuil : stock restant, seuil et accès à la fiche.
class CarteAlerte extends StatelessWidget {
  const CarteAlerte(this.article, {super.key});

  final ArticleStock article;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final ton = tonNiveau(article.niveau);
    final part = article.seuilMinimal <= 0
        ? 0.0
        : article.quantite / article.seuilMinimal;
    return Carte(
      onTap: () =>
          ouvrirEcran<void>(context, EcranFicheArticle(code: article.code)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              TuileIcone(icone: iconeNiveau(article.niveau), ton: ton),
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
                    Text(
                      article.emplacement,
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
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Text.rich(
                  TextSpan(
                    text: '${t.stockRestant} ',
                    style: TextStyle(color: p.texteSecondaire, fontSize: 13),
                    children: [
                      TextSpan(
                        text: formaterQuantite(article.quantite, article.unite),
                        style: TextStyle(
                          color: ton.texte(p),
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              Text(
                t.seuilMini(
                  formaterQuantite(article.seuilMinimal, article.unite),
                ),
                style: TextStyle(color: p.texteSecondaire, fontSize: 13),
              ),
            ],
          ),
          const SizedBox(height: 8),
          BarreProgression(valeur: part.toDouble(), ton: ton),
        ],
      ),
    );
  }
}
