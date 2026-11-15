import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/boutons.dart';
import '../../../components/en_tetes.dart';
import '../../../components/feuille_pin.dart';
import '../../../components/saisie.dart';
import '../../../components/surfaces.dart';
import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../application/etat_stock.dart';
import '../data/depot_stock.dart';
import '../domain/modeles.dart';
import 'elements_stock.dart';

/// Inventaire tournant (écran 8).
///
/// Le magasinier compte article par article ; tout écart doit être justifié.
/// Le stock n'est ajusté qu'une fois l'inventaire validé par une autre
/// personne : c'est le seul chemin d'ajustement (charte § 10).
class EcranInventaire extends ConsumerStatefulWidget {
  const EcranInventaire({super.key});

  @override
  ConsumerState<EcranInventaire> createState() => _EcranInventaireState();
}

class _EcranInventaireState extends ConsumerState<EcranInventaire> {
  String? _codeActif;
  num? _saisie;
  String? _justification;
  bool _enCours = false;

  LigneInventaire? _ligneActive(Inventaire inventaire) {
    final choisie = inventaire.lignes
        .where((l) => l.codeArticle == _codeActif)
        .firstOrNull;
    return choisie ?? inventaire.lignes.where((l) => !l.estComptee).firstOrNull;
  }

  void _activer(LigneInventaire ligne) => setState(() {
    _codeActif = ligne.codeArticle;
    _saisie = ligne.compte;
    _justification = ligne.justification;
  });

  Future<void> _validerLigne(LigneInventaire ligne) async {
    final operateur = ref.read(operateurProvider);
    if (operateur == null) return;
    final valeur = _saisie ?? ligne.theorique;
    setState(() => _enCours = true);
    await ref
        .read(depotStockProvider)
        .compter(
          ligne.codeArticle,
          valeur,
          compteur: operateur.profil,
          justification: valeur == ligne.theorique ? null : _justification,
        );
    ref.invalidate(inventaireProvider);
    HapticFeedback.selectionClick();
    if (!mounted) return;
    setState(() {
      _enCours = false;
      _codeActif = null;
      _saisie = null;
      _justification = null;
    });
  }

  Future<void> _soumettre() async {
    await ref.read(depotStockProvider).soumettreInventaire();
    rafraichirStock(ref);
    if (mounted) notifier(context, context.t.inventaireSoumis);
  }

  Future<void> _validerInventaire(Inventaire inventaire) async {
    final t = context.t;
    final operateur = ref.read(operateurProvider);
    if (operateur == null) return;
    final signe = await demanderSignaturePin(
      context,
      objet: t.signatureInventaire(inventaire.id, inventaire.ecarts.length),
    );
    if (!signe || !mounted) return;
    try {
      await ref.read(depotStockProvider).validerInventaire(operateur.profil);
      rafraichirStock(ref);
      if (mounted) notifier(context, t.inventaireValide);
    } on SeparationFonctionsException {
      if (mounted) notifier(context, t.separationFonctions);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final role = ref.watch(operateurProvider)?.role;
    final inventaire = ref.watch(inventaireProvider).valueOrNull;

    if (inventaire == null) {
      return Scaffold(
        appBar: BarreEcran(titre: t.inventaireTitre),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    final peutCompter =
        (role?.peutSaisirStock ?? false) &&
        inventaire.statut == StatutInventaire.enCours;
    final peutValider =
        (role?.peutValiderStock ?? false) &&
        inventaire.statut == StatutInventaire.aValider;
    final active = peutCompter ? _ligneActive(inventaire) : null;
    final saisie = active == null
        ? 0
        : (_saisie ?? active.compte ?? active.theorique);
    final ecart = active == null ? 0 : saisie - active.theorique;
    final toutCompte = inventaire.nombreComptees == inventaire.lignes.length;

    final (libelleStatutInv, tonStatutInv) = switch (inventaire.statut) {
      StatutInventaire.enCours => (t.inventaireEnCours, Ton.info),
      StatutInventaire.aValider => (t.statutAValider, Ton.alerte),
      StatutInventaire.valide => (t.statutValide, Ton.succes),
    };

    Widget? action;
    if (active != null) {
      action = BoutonPrincipal(
        libelle: t.validerArticle(formaterQuantite(saisie, active.unite)),
        iconeFin: PhosphorIconsBold.arrowRight,
        enChargement: _enCours,
        onPressed: ecart != 0 && _justification == null
            ? null
            : () => _validerLigne(active),
      );
    } else if (peutCompter && toutCompte) {
      action = BoutonPrincipal(
        libelle: t.soumettreInventaire,
        icone: PhosphorIconsBold.paperPlaneTilt,
        onPressed: _soumettre,
      );
    } else if (peutValider) {
      action = BoutonPrincipal(
        libelle: t.validerInventaire,
        icone: PhosphorIconsBold.sealCheck,
        onPressed: () => _validerInventaire(inventaire),
      );
    }

    return Scaffold(
      appBar: BarreEcran(titre: t.inventaireTitre, sousTitre: inventaire.zone),
      bottomNavigationBar: action == null
          ? null
          : ZoneAction(
              mention: active != null && ecart != 0 && _justification == null
                  ? t.justificationObligatoire
                  : (peutValider ? t.inventaireRegle : null),
              child: action,
            ),
      body: ListView(
        padding: const EdgeInsets.all(Jetons.margeMobile),
        children: [
          Apparition(
            child: Carte(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          inventaire.id,
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w800,
                            color: p.sombre ? p.texte : Jetons.marine,
                          ),
                        ),
                      ),
                      Pastille(libelle: libelleStatutInv, ton: tonStatutInv),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          t.inventaireProgression(
                            inventaire.nombreComptees,
                            inventaire.lignes.length,
                          ),
                          style: TextStyle(
                            color: p.texteSecondaire,
                            fontSize: 13,
                          ),
                        ),
                      ),
                      Text(
                        '${(inventaire.progression * 100).round()} %',
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          color: p.texte,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  BarreProgression(valeur: inventaire.progression),
                ],
              ),
            ),
          ),
          if (active != null) ...[
            const SizedBox(height: 12),
            Apparition(
              key: ValueKey(active.codeArticle),
              rang: 1,
              child: Carte(
                bordure: p.accent,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Pastille(
                          libelle: t.articleEnControle,
                          ton: Ton.info,
                          pleine: true,
                        ),
                        const Spacer(),
                        Text(
                          active.emplacement,
                          style: TextStyle(
                            color: p.texteSecondaire,
                            fontSize: 12.5,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      active.designation,
                      style: TextStyle(
                        fontSize: 19,
                        fontWeight: FontWeight.w800,
                        color: p.sombre ? p.texte : Jetons.marine,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Bloc(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          Icon(
                            PhosphorIconsRegular.stack,
                            size: 18,
                            color: p.accent,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              t.stockTheorique,
                              style: TextStyle(color: p.texteSecondaire),
                            ),
                          ),
                          Text(
                            formaterQuantite(active.theorique, active.unite),
                            style: TextStyle(
                              fontWeight: FontWeight.w800,
                              color: p.texte,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    LibelleChamp(t.quantiteComptee),
                    SelecteurQuantite(
                      valeur: saisie,
                      onChange: (v) => setState(() {
                        _saisie = v;
                        if (v == active.theorique) _justification = null;
                      }),
                      unite: active.unite,
                      raccourcis: const [],
                    ),
                    if (ecart != 0) ...[
                      const SizedBox(height: 12),
                      Bloc(
                        couleur: p.orFond,
                        bordure: p.orBordure,
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  PhosphorIconsRegular.warning,
                                  color: p.or,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    t.ecartDetecte(
                                      '${ecart > 0 ? '+' : '−'}${formaterQuantite(ecart.abs(), active.unite)}',
                                    ),
                                    style: TextStyle(
                                      color: p.or,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                for (final motif in [
                                  t.ecartChutes,
                                  t.ecartRebut,
                                  t.ecartNonDeclare,
                                  t.ecartRecompter,
                                ])
                                  PuceChoix(
                                    libelle: motif,
                                    ton: Ton.alerte,
                                    selectionnee: _justification == motif,
                                    onTap: () =>
                                        setState(() => _justification = motif),
                                  ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
          if (inventaire.statut == StatutInventaire.aValider &&
              !peutValider) ...[
            const SizedBox(height: 12),
            Bloc(
              child: Row(
                children: [
                  Icon(
                    PhosphorIconsRegular.hourglassMedium,
                    color: p.texteSecondaire,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      t.inventaireEnAttenteValidation,
                      style: TextStyle(color: p.texteSecondaire, height: 1.35),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: Jetons.espace4),
          TitreSection(
            t.inventaireArticles,
            icone: PhosphorIconsRegular.listChecks,
          ),
          const SizedBox(height: 10),
          for (final (rang, ligne) in inventaire.lignes.indexed) ...[
            Apparition(
              rang: rang + 2,
              child: _LigneInventaire(
                ligne: ligne,
                active: ligne.codeArticle == active?.codeArticle,
                onTap: peutCompter ? () => _activer(ligne) : null,
              ),
            ),
            const SizedBox(height: 8),
          ],
        ],
      ),
    );
  }
}

class _LigneInventaire extends StatelessWidget {
  const _LigneInventaire({
    required this.ligne,
    required this.active,
    this.onTap,
  });

  final LigneInventaire ligne;
  final bool active;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final (libelle, ton, icone) = !ligne.estComptee
        ? (t.aCompter, Ton.neutre, PhosphorIconsRegular.hourglassMedium)
        : ligne.ecart == 0
        ? (t.conforme, Ton.succes, PhosphorIconsRegular.checkCircle)
        : (
            '${ligne.ecart > 0 ? '+' : '−'}${formaterQuantite(ligne.ecart.abs(), ligne.unite)}',
            Ton.alerte,
            PhosphorIconsRegular.warning,
          );
    return Carte(
      onTap: onTap,
      padding: const EdgeInsets.all(12),
      rayon: Jetons.rayonBloc,
      bordure: active ? p.accent : null,
      avecOmbre: false,
      child: Row(
        children: [
          TuileIcone(icone: icone, ton: ton, taille: 40),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  ligne.designation,
                  style: TextStyle(fontWeight: FontWeight.w700, color: p.texte),
                ),
                Text(
                  [
                    ligne.codeArticle,
                    ligne.emplacement,
                    if (ligne.justification != null) ligne.justification!,
                  ].join(' · '),
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
          Pastille(libelle: libelle, ton: ton),
        ],
      ),
    );
  }
}
