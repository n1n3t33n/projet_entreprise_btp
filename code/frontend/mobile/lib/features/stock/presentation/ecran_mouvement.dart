import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/boutons.dart';
import '../../../components/en_tetes.dart';
import '../../../components/saisie.dart';
import '../../../components/surfaces.dart';
import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../application/etat_stock.dart';
import '../data/donnees_demo.dart';
import '../domain/modeles.dart';
import 'elements_stock.dart';

/// Nature de la saisie : sortie rapide (écran 5), réception d'un bon de
/// livraison (écran 6), retour, casse ou perte (écran 7).
enum ModeSaisie { sortie, reception, retour }

enum _NatureRetour { retour, casse, perte }

/// Saisie d'un mouvement de stock, en étapes numérotées et à gros boutons :
/// pensée pour être faite en moins de trente secondes, gants aux mains.
class EcranMouvement extends ConsumerStatefulWidget {
  const EcranMouvement({required this.mode, this.article, super.key});

  final ModeSaisie mode;
  final ArticleStock? article;

  @override
  ConsumerState<EcranMouvement> createState() => _EcranMouvementState();
}

class _EcranMouvementState extends ConsumerState<EcranMouvement> {
  late ArticleStock? _article = widget.article;
  num _quantite = 1;
  String? _destination;
  String? _corpsEtat;
  String? _equipe;
  String? _fournisseur;
  String? _motif;
  bool _conforme = true;
  _NatureRetour _nature = _NatureRetour.retour;
  bool _enCours = false;
  final _bon = TextEditingController();
  final _observations = TextEditingController();

  @override
  void initState() {
    super.initState();
    _bon.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _bon.dispose();
    _observations.dispose();
    super.dispose();
  }

  bool get _complet {
    if (_article == null || _quantite <= 0) return false;
    return switch (widget.mode) {
      ModeSaisie.sortie => _destination != null,
      ModeSaisie.reception =>
        _bon.text.trim().isNotEmpty && _fournisseur != null,
      ModeSaisie.retour => _motif != null,
    };
  }

  Future<void> _changerArticle() async {
    final articles = await ref.read(articlesProvider.future);
    if (!mounted) return;
    final choisi = await choisirArticle(context, articles);
    if (choisi != null) setState(() => _article = choisi);
  }

  Future<void> _valider() async {
    final article = _article;
    final operateur = ref.read(operateurProvider);
    if (article == null || operateur == null || !_complet) return;
    setState(() => _enCours = true);

    final observations = _observations.text.trim();
    final (type, sens, destination, reference, motif) = switch (widget.mode) {
      ModeSaisie.sortie => (
        TypeMouvement.sortieLogement,
        SensMouvement.sortie,
        [_destination, _corpsEtat].nonNulls.join(' · '),
        null,
        _equipe,
      ),
      ModeSaisie.reception => (
        TypeMouvement.reception,
        SensMouvement.entree,
        _fournisseur,
        _bon.text.trim(),
        [
          if (!_conforme) context.t.receptionReserves,
          if (observations.isNotEmpty) observations,
        ].join(' — '),
      ),
      ModeSaisie.retour => (
        _nature == _NatureRetour.retour
            ? TypeMouvement.retour
            : TypeMouvement.perte,
        _nature == _NatureRetour.retour
            ? SensMouvement.entree
            : SensMouvement.sortie,
        null,
        null,
        [
          _motif,
          if (observations.isNotEmpty) observations,
        ].nonNulls.join(' — '),
      ),
    };

    await ref
        .read(depotStockProvider)
        .enregistrer(
          article: article,
          type: type,
          sens: sens,
          quantite: _quantite,
          auteur: operateur.profil,
          destination: destination,
          reference: reference,
          motif: motif == null || motif.isEmpty ? null : motif,
        );
    rafraichirStock(ref);
    HapticFeedback.mediumImpact();
    if (!mounted) return;
    notifier(context, context.t.mouvementEnregistre);
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final article = _article;
    final titre = switch (widget.mode) {
      ModeSaisie.sortie => t.sortieTitre,
      ModeSaisie.reception => t.receptionTitre,
      ModeSaisie.retour => t.retourTitre,
    };
    final quantite = article == null
        ? ''
        : formaterQuantite(_quantite, article.unite);
    final action = switch (widget.mode) {
      ModeSaisie.sortie => t.validerSortie(quantite),
      ModeSaisie.reception => t.enregistrerReception(quantite),
      ModeSaisie.retour => t.validerDeclaration(quantite),
    };

    final sections = <Widget>[
      if (widget.mode == ModeSaisie.retour) _sectionNature(),
      _sectionArticle(),
      if (article != null) _sectionQuantite(article),
      if (article != null && widget.mode == ModeSaisie.sortie) ...[
        _sectionDestination(),
        _sectionEquipe(),
      ],
      if (article != null && widget.mode == ModeSaisie.reception) ...[
        _sectionTracabilite(),
        _sectionEtat(),
      ],
      if (article != null && widget.mode == ModeSaisie.retour) _sectionMotif(),
      if (article != null && _complet)
        _Recapitulatif(article: article, variation: _variation(article)),
    ];

    return Scaffold(
      appBar: BarreEcran(titre: titre, sousTitre: t.saisieSousTitre),
      body: ListView.separated(
        padding: const EdgeInsets.all(Jetons.margeMobile),
        itemCount: sections.length,
        separatorBuilder: (_, _) => const SizedBox(height: 12),
        itemBuilder: (_, i) => Apparition(rang: i, child: sections[i]),
      ),
      bottomNavigationBar: ZoneAction(
        mention: _complet ? t.saisieMention : t.saisieIncomplete,
        child: BoutonPrincipal(
          libelle: action,
          icone: PhosphorIconsBold.checkCircle,
          enChargement: _enCours,
          onPressed: _complet ? _valider : null,
        ),
      ),
    );
  }

  num _variation(ArticleStock article) {
    final sortie =
        widget.mode == ModeSaisie.sortie ||
        (widget.mode == ModeSaisie.retour && _nature != _NatureRetour.retour);
    return sortie ? -_quantite : _quantite;
  }

  int _numero(int rang) => widget.mode == ModeSaisie.retour ? rang + 1 : rang;

  Widget _sectionNature() {
    final t = context.t;
    return SectionEtape(
      numero: 1,
      titre: t.retourNature,
      child: Column(
        children: [
          for (final (nature, titre, detail, icone) in [
            (
              _NatureRetour.retour,
              t.natureRetour,
              t.natureRetourDetail,
              PhosphorIconsRegular.arrowUUpLeft,
            ),
            (
              _NatureRetour.casse,
              t.natureCasse,
              t.natureCasseDetail,
              PhosphorIconsRegular.hammer,
            ),
            (
              _NatureRetour.perte,
              t.naturePerte,
              t.naturePerteDetail,
              PhosphorIconsRegular.magnifyingGlassMinus,
            ),
          ]) ...[
            CarteOption(
              titre: titre,
              detail: detail,
              icone: icone,
              ton: nature == _NatureRetour.retour ? Ton.info : Ton.alerte,
              selectionnee: _nature == nature,
              onTap: () => setState(() {
                _nature = nature;
                _motif = null;
              }),
            ),
            if (nature != _NatureRetour.perte) const SizedBox(height: 8),
          ],
        ],
      ),
    );
  }

  Widget _sectionArticle() {
    final t = context.t;
    final article = _article;
    return SectionEtape(
      numero: _numero(1),
      titre: t.saisieArticle,
      child: article == null
          ? BoutonSecondaire(
              libelle: t.choisirArticleTitre,
              icone: PhosphorIconsRegular.magnifyingGlass,
              onPressed: _changerArticle,
            )
          : ResumeArticle(article, onChanger: _changerArticle),
    );
  }

  Widget _sectionQuantite(ArticleStock article) {
    final t = context.t;
    final p = context.palette;
    final sortie = widget.mode == ModeSaisie.sortie;
    final disponible = article.quantite > 0 ? article.quantite : null;
    final projete = article.quantite + _variation(article);
    return SectionEtape(
      numero: _numero(2),
      titre: t.saisieQuantite,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SelecteurQuantite(
            valeur: _quantite,
            onChange: (v) => setState(() => _quantite = v),
            unite: article.unite,
            min: 1,
            raccourcis: widget.mode == ModeSaisie.reception
                ? const [10, 50, 100]
                : const [1, 5, 10],
            max: null,
          ),
          if (sortie && disponible != null) ...[
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerLeft,
              child: PuceChoix(
                libelle: t.toutLeStock(formaterQuantite(disponible)),
                selectionnee: _quantite == disponible,
                onTap: () => setState(() => _quantite = disponible),
              ),
            ),
          ],
          const SizedBox(height: 12),
          Bloc(
            couleur: projete < 0 ? p.dangerFond : null,
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Icon(
                  PhosphorIconsRegular.trendUp,
                  size: 20,
                  color: projete < 0 ? p.danger : p.accent,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    t.stockProjete,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: p.texte,
                    ),
                  ),
                ),
                Text(
                  formaterQuantite(projete, article.unite),
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 16,
                    color: projete < 0 ? p.danger : p.accent,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _puces(
    List<String> options,
    String? valeur,
    ValueChanged<String> onChoix,
  ) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final option in options)
          PuceChoix(
            libelle: option,
            selectionnee: valeur == option,
            onTap: () => onChoix(option),
          ),
      ],
    );
  }

  Widget _sectionDestination() {
    final t = context.t;
    return SectionEtape(
      numero: 3,
      titre: t.sortieDestination,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LibelleChamp(t.sortieLogement, requis: true),
          _puces(
            destinationsDemo,
            _destination,
            (v) => setState(() => _destination = v),
          ),
          const SizedBox(height: Jetons.espace3),
          LibelleChamp(t.sortieCorpsEtat),
          _puces(
            corpsEtatDemo,
            _corpsEtat,
            (v) => setState(() => _corpsEtat = v),
          ),
        ],
      ),
    );
  }

  Widget _sectionEquipe() {
    final t = context.t;
    return SectionEtape(
      numero: 4,
      titre: t.sortieBeneficiaire,
      complement: Pastille(libelle: t.facultatif),
      child: Align(
        alignment: Alignment.centerLeft,
        child: _puces(equipesDemo, _equipe, (v) => setState(() => _equipe = v)),
      ),
    );
  }

  Widget _sectionTracabilite() {
    final t = context.t;
    return SectionEtape(
      numero: 3,
      titre: t.receptionTracabilite,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LibelleChamp(t.receptionBon, requis: true),
          TextField(
            controller: _bon,
            textCapitalization: TextCapitalization.characters,
            decoration: InputDecoration(
              hintText: t.receptionBonExemple,
              prefixIcon: const Icon(PhosphorIconsRegular.receipt),
            ),
          ),
          const SizedBox(height: Jetons.espace3),
          LibelleChamp(t.receptionFournisseur, requis: true),
          _puces(
            fournisseursDemo,
            _fournisseur,
            (v) => setState(() => _fournisseur = v),
          ),
        ],
      ),
    );
  }

  Widget _sectionEtat() {
    final t = context.t;
    return SectionEtape(
      numero: 4,
      titre: t.receptionEtat,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: PuceChoix(
                  libelle: t.receptionConforme,
                  icone: PhosphorIconsRegular.checkCircle,
                  ton: Ton.succes,
                  selectionnee: _conforme,
                  onTap: () => setState(() => _conforme = true),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: PuceChoix(
                  libelle: t.receptionReserves,
                  icone: PhosphorIconsRegular.warning,
                  ton: Ton.alerte,
                  selectionnee: !_conforme,
                  onTap: () => setState(() => _conforme = false),
                ),
              ),
            ],
          ),
          const SizedBox(height: Jetons.espace3),
          LibelleChamp(t.observations),
          TextField(
            controller: _observations,
            maxLines: 2,
            decoration: InputDecoration(
              hintText: t.receptionObservationsExemple,
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionMotif() {
    final t = context.t;
    final motifs = _nature == _NatureRetour.retour
        ? [t.motifSurplus, t.motifErreurMetre, t.motifAutre]
        : [t.motifHumidite, t.motifChoc, t.motifIntrouvable, t.motifAutre];
    return SectionEtape(
      numero: 4,
      titre: t.retourMotif,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LibelleChamp(t.retourMotifAide, requis: true),
          _puces(motifs, _motif, (v) => setState(() => _motif = v)),
          const SizedBox(height: Jetons.espace3),
          LibelleChamp(t.observations),
          TextField(
            controller: _observations,
            maxLines: 2,
            decoration: InputDecoration(hintText: t.retourObservationsExemple),
          ),
        ],
      ),
    );
  }
}

/// Contrôle avant validation : effet de la saisie sur le stock et ses seuils.
class _Recapitulatif extends StatelessWidget {
  const _Recapitulatif({required this.article, required this.variation});

  final ArticleStock article;
  final num variation;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final apres = article.avecQuantite(
      article.quantite + variation,
      article.majLe,
    );
    final alerte = variation < 0 && apres.sousSeuil;
    final message = apres.estNegatif
        ? t.avertissementNegatif
        : alerte
        ? t.avertissementSeuil(
            formaterQuantite(apres.quantite, article.unite),
            formaterQuantite(article.seuilMinimal, article.unite),
          )
        : t.controleOk;
    final ton = apres.estNegatif
        ? Ton.danger
        : (alerte ? Ton.alerte : Ton.succes);
    return Bloc(
      couleur: ton.fond(p),
      bordure: ton.texte(p).withValues(alpha: 0.3),
      padding: const EdgeInsets.all(14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            alerte || apres.estNegatif
                ? PhosphorIconsRegular.warning
                : PhosphorIconsRegular.sealCheck,
            color: ton.texte(p),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: TextStyle(
                color: ton.texte(p),
                fontWeight: FontWeight.w600,
                height: 1.35,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
