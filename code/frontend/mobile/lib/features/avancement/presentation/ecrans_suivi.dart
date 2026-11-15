import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
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
import '../../stock/application/etat_stock.dart';
import '../../stock/data/depot_stock.dart';
import '../../stock/domain/modeles.dart' show ArticleStock;
import '../../stock/presentation/elements_stock.dart';
import '../application/etat_avancement.dart';
import '../data/depot_avancement.dart';
import '../data/donnees_demo.dart';
import '../domain/modeles.dart';
import 'ecrans_etapes.dart';
import 'elements_avancement.dart';

/// Déclaration d'un blocage de terrain (écran 13). Une rupture de matériau
/// impose de désigner l'article manquant.
class EcranBlocage extends ConsumerStatefulWidget {
  const EcranBlocage({required this.idEtape, super.key});

  final String idEtape;

  @override
  ConsumerState<EcranBlocage> createState() => _EcranBlocageState();
}

class _EcranBlocageState extends ConsumerState<EcranBlocage> {
  NatureBlocage? _nature;
  GraviteBlocage _gravite = GraviteBlocage.arretTotal;
  RetardEstime _retard = RetardEstime.deuxHeures;
  ArticleStock? _article;
  bool _enCours = false;
  final _observations = TextEditingController();

  @override
  void dispose() {
    _observations.dispose();
    super.dispose();
  }

  bool get _complet =>
      _nature != null &&
      (_nature != NatureBlocage.ruptureMateriau || _article != null);

  Future<void> _transmettre() async {
    final operateur = ref.read(operateurProvider);
    final nature = _nature;
    if (operateur == null || nature == null || !_complet) return;
    setState(() => _enCours = true);
    final observations = _observations.text.trim();
    try {
      await ref
          .read(depotAvancementProvider)
          .declarerBlocage(
            widget.idEtape,
            Blocage(
              nature: nature,
              gravite: _gravite,
              retard: _retard,
              date: DateTime.now(),
              observations: observations.isEmpty ? null : observations,
              codeArticle: _article?.code,
              designationArticle: _article?.designation,
            ),
            operateur.profil,
          );
      rafraichirAvancement(ref);
      HapticFeedback.heavyImpact();
      if (!mounted) return;
      notifier(context, context.t.blocageTransmis);
      Navigator.of(context).pop();
    } on TransitionInterditeException {
      if (mounted) {
        setState(() => _enCours = false);
        notifier(context, context.t.actionImpossible);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final etape =
        (ref.watch(toutesEtapesProvider).valueOrNull ?? const <EtapeTravaux>[])
            .where((e) => e.id == widget.idEtape)
            .firstOrNull;

    return Scaffold(
      appBar: BarreEcran(titre: t.blocageTitre, sousTitre: t.saisieSousTitre),
      bottomNavigationBar: ZoneAction(
        mention: _complet ? t.blocageMention : t.saisieIncomplete,
        child: BoutonPrincipal(
          libelle: t.transmettreBlocage,
          icone: PhosphorIconsBold.warningOctagon,
          ton: Ton.danger,
          enChargement: _enCours,
          onPressed: _complet ? _transmettre : null,
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(Jetons.margeMobile),
        children: [
          if (etape != null) CarteEtape(etape),
          const SizedBox(height: 12),
          SectionEtape(
            numero: 1,
            titre: t.blocageNature,
            child: Column(
              children: [
                for (final nature in NatureBlocage.values) ...[
                  CarteOption(
                    titre: libelleNature(t, nature),
                    icone: iconeNature(nature),
                    ton: Ton.danger,
                    selectionnee: _nature == nature,
                    onTap: () => setState(() => _nature = nature),
                  ),
                  const SizedBox(height: 8),
                ],
                if (_nature == NatureBlocage.ruptureMateriau) ...[
                  const SizedBox(height: 4),
                  if (_article == null)
                    BoutonSecondaire(
                      libelle: t.blocageArticle,
                      icone: PhosphorIconsRegular.magnifyingGlass,
                      onPressed: _choisirArticle,
                    )
                  else
                    ResumeArticle(_article!, onChanger: _choisirArticle),
                ],
              ],
            ),
          ),
          const SizedBox(height: 12),
          SectionEtape(
            numero: 2,
            titre: t.blocageGravite,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final gravite in GraviteBlocage.values)
                  PuceChoix(
                    libelle: libelleGravite(t, gravite),
                    ton: gravite == GraviteBlocage.arretTotal
                        ? Ton.danger
                        : Ton.alerte,
                    selectionnee: _gravite == gravite,
                    onTap: () => setState(() => _gravite = gravite),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          SectionEtape(
            numero: 3,
            titre: t.blocageRetard,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final retard in RetardEstime.values)
                  PuceChoix(
                    libelle: libelleRetard(t, retard),
                    selectionnee: _retard == retard,
                    onTap: () => setState(() => _retard = retard),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          SectionEtape(
            numero: 4,
            titre: t.observations,
            complement: Pastille(libelle: t.facultatif),
            child: TextField(
              controller: _observations,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: t.blocageObservationsExemple,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _choisirArticle() async {
    final articles = await ref.read(articlesProvider.future);
    if (!mounted) return;
    final choisi = await choisirArticle(context, articles);
    if (choisi != null) setState(() => _article = choisi);
  }
}

/// Contrôles et réception (écran 14) : validation des étapes déclarées
/// terminées, signée par code PIN. Le déclarant ne peut pas valider.
class EcranControles extends ConsumerStatefulWidget {
  const EcranControles({this.racine = false, super.key});

  final bool racine;

  @override
  ConsumerState<EcranControles> createState() => _EcranControlesState();
}

class _EcranControlesState extends ConsumerState<EcranControles> {
  bool _validees = false;

  Future<void> _decider(EtapeTravaux etape, {required bool accepte}) async {
    final t = context.t;
    final operateur = ref.read(operateurProvider);
    if (operateur == null) return;
    if (accepte) {
      final signe = await demanderSignaturePin(
        context,
        objet: t.signatureEtape(etape.id, etape.libelle),
      );
      if (!signe || !mounted) return;
    }
    try {
      await ref
          .read(depotAvancementProvider)
          .decider(etape.id, accepte: accepte, validateur: operateur.profil);
      rafraichirAvancement(ref);
      HapticFeedback.mediumImpact();
      if (mounted) {
        notifier(
          context,
          accepte ? t.etapeValideeMessage : t.etapeRefuseeMessage,
        );
      }
    } on SeparationFonctionsException {
      if (mounted) notifier(context, t.separationFonctions);
    } on TransitionInterditeException {
      if (mounted) notifier(context, t.actionImpossible);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final operateur = ref.watch(operateurProvider);
    final toutes =
        ref.watch(toutesEtapesProvider).valueOrNull ?? const <EtapeTravaux>[];
    final aValider = ref.watch(etapesAValiderProvider);
    final validees = toutes
        .where((e) => e.statut == StatutEtape.validee)
        .toList();
    final peutValider = operateur?.role.peutValiderEtapes ?? false;

    return Scaffold(
      appBar: BarreEcran(
        titre: t.controlesTitre,
        sousTitre: t.controlesSousTitre,
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
                  libelle: t.statutAValider,
                  compteur: aValider.length,
                  ton: Ton.alerte,
                  selectionnee: !_validees,
                  onTap: () => setState(() => _validees = false),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: PuceChoix(
                  libelle: t.etapeValidee,
                  compteur: validees.length,
                  ton: Ton.succes,
                  selectionnee: _validees,
                  onTap: () => setState(() => _validees = true),
                ),
              ),
            ],
          ),
          const SizedBox(height: Jetons.espace3),
          if (_validees)
            for (final (rang, etape) in validees.indexed) ...[
              Apparition(
                key: ValueKey(etape.id),
                rang: rang,
                child: CarteEtape(
                  etape,
                  onTap: () => ouvrirEcran<void>(
                    context,
                    EcranJournalEtape(idEtape: etape.id),
                  ),
                ),
              ),
              const SizedBox(height: 10),
            ]
          else ...[
            if (aValider.isEmpty)
              EtatVide(
                icone: PhosphorIconsRegular.sealCheck,
                titre: t.aucunControle,
                texte: t.aucunControleAide,
              ),
            for (final (rang, etape) in aValider.indexed) ...[
              Apparition(
                key: ValueKey(etape.id),
                rang: rang,
                child: CarteEtape(
                  etape,
                  onTap: () =>
                      ouvrirEcran<void>(context, EcranEtape(id: etape.id)),
                  pied: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        t.declarePar(
                          etape.nomAuteurDeclaration ?? etape.nomResponsable,
                        ),
                        style: TextStyle(
                          color: p.texteSecondaire,
                          fontSize: 13,
                        ),
                      ),
                      const SizedBox(height: 8),
                      for (final controle in etape.controles)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: Row(
                            children: [
                              Icon(
                                PhosphorIconsFill.checkCircle,
                                size: 18,
                                color: p.succes,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  controle,
                                  style: TextStyle(
                                    fontSize: 13.5,
                                    color: p.texte,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      const SizedBox(height: 6),
                      if (!peutValider)
                        const SizedBox.shrink()
                      else if (etape.idAuteurDeclaration ==
                          operateur?.profil.idUtilisateur)
                        Bloc(
                          padding: const EdgeInsets.all(12),
                          child: Text(
                            t.separationFonctions,
                            style: TextStyle(
                              color: p.texteSecondaire,
                              fontSize: 13,
                              height: 1.35,
                            ),
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
                                onPressed: () =>
                                    _decider(etape, accepte: false),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 3,
                              child: BoutonPrincipal(
                                libelle: t.validerEtape,
                                icone: PhosphorIconsBold.sealCheck,
                                onPressed: () => _decider(etape, accepte: true),
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
            ],
          ],
        ],
      ),
    );
  }
}

/// Réaffectation d'une étape à une autre équipe (écran 15).
class EcranReaffectation extends ConsumerStatefulWidget {
  const EcranReaffectation({required this.idEtape, super.key});

  final String idEtape;

  @override
  ConsumerState<EcranReaffectation> createState() => _EcranReaffectationState();
}

class _EcranReaffectationState extends ConsumerState<EcranReaffectation> {
  String? _motif;
  Equipe? _equipe;
  bool _enCours = false;
  final _consigne = TextEditingController();

  @override
  void dispose() {
    _consigne.dispose();
    super.dispose();
  }

  Future<void> _confirmer() async {
    final operateur = ref.read(operateurProvider);
    final equipe = _equipe;
    final motif = _motif;
    if (operateur == null || equipe == null || motif == null) return;
    setState(() => _enCours = true);
    await ref
        .read(depotAvancementProvider)
        .reaffecter(
          widget.idEtape,
          equipe: equipe,
          motif: motif,
          auteur: operateur.profil,
          consigne: _consigne.text.trim(),
        );
    rafraichirAvancement(ref);
    if (!mounted) return;
    notifier(context, context.t.reaffectationFaite(equipe.nom));
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final etape =
        (ref.watch(toutesEtapesProvider).valueOrNull ?? const <EtapeTravaux>[])
            .where((e) => e.id == widget.idEtape)
            .firstOrNull;
    final complet = _motif != null && _equipe != null;
    final equipes = equipesDemo.where((e) => e.nom != etape?.equipe).toList();

    return Scaffold(
      appBar: BarreEcran(titre: t.reaffectationTitre, sousTitre: lotDemo),
      bottomNavigationBar: ZoneAction(
        mention: complet ? t.reaffectationMention : t.saisieIncomplete,
        child: BoutonPrincipal(
          libelle: t.confirmerReaffectation,
          iconeFin: PhosphorIconsBold.arrowRight,
          enChargement: _enCours,
          onPressed: complet ? _confirmer : null,
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(Jetons.margeMobile),
        children: [
          if (etape != null) CarteEtape(etape),
          const SizedBox(height: 12),
          SectionEtape(
            numero: 1,
            titre: t.reaffectationMotif,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final motif in [
                  t.motifRetardPlanning,
                  t.motifAbsence,
                  t.motifCompetence,
                  t.motifSurcroit,
                ])
                  PuceChoix(
                    libelle: motif,
                    selectionnee: _motif == motif,
                    onTap: () => setState(() => _motif = motif),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          SectionEtape(
            numero: 2,
            titre: t.reaffectationEquipe,
            child: Column(
              children: [
                for (final equipe in equipes) ...[
                  Appui(
                    onTap: () => setState(() => _equipe = equipe),
                    echelle: 0.985,
                    child: AnimatedContainer(
                      duration: Jetons.dureeMicro,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: _equipe == equipe ? p.accentFond : p.surface,
                        borderRadius: BorderRadius.circular(Jetons.rayonBloc),
                        border: Border.all(
                          color: _equipe == equipe ? p.accent : p.bordure,
                          width: _equipe == equipe ? 2 : 1.5,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              AvatarInitiales(equipe.nomChef, taille: 40),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      equipe.nom,
                                      style: TextStyle(
                                        fontWeight: FontWeight.w700,
                                        color: p.texte,
                                      ),
                                    ),
                                    Text(
                                      t.equipeDetail(
                                        equipe.nomChef,
                                        equipe.effectif,
                                      ),
                                      style: TextStyle(
                                        color: p.texteSecondaire,
                                        fontSize: 12.5,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Icon(
                                _equipe == equipe
                                    ? PhosphorIconsFill.checkCircle
                                    : PhosphorIconsRegular.circle,
                                color: _equipe == equipe
                                    ? p.accent
                                    : p.texteAttenue,
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Row(
                            children: [
                              Text(
                                t.chargeActuelle,
                                style: TextStyle(
                                  color: p.texteSecondaire,
                                  fontSize: 12.5,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: BarreProgression(
                                  valeur: equipe.charge,
                                  ton: equipe.charge > 0.7
                                      ? Ton.alerte
                                      : Ton.info,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                '${(equipe.charge * 100).round()} %',
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: p.texte,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
              ],
            ),
          ),
          const SizedBox(height: 12),
          SectionEtape(
            numero: 3,
            titre: t.reaffectationConsigne,
            complement: Pastille(libelle: t.facultatif),
            child: TextField(
              controller: _consigne,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: t.reaffectationConsigneExemple,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Journal d'une étape (écran 16) : frise horodatée des événements, en
/// lecture seule. Sans étape précisée, montre toute l'activité visible.
class EcranJournalEtape extends ConsumerWidget {
  const EcranJournalEtape({this.idEtape, this.racine = false, super.key});

  final String? idEtape;
  final bool racine;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final langue = Localizations.localeOf(context).toLanguageTag();
    final visibles = ref.watch(etapesProvider).map((e) => e.id).toSet();
    final evenements =
        (ref.watch(evenementsProvider).valueOrNull ?? const <EvenementEtape>[])
            .where(
              (e) => idEtape == null
                  ? visibles.contains(e.idEtape)
                  : e.idEtape == idEtape,
            )
            .toList();
    final etape =
        (ref.watch(toutesEtapesProvider).valueOrNull ?? const <EtapeTravaux>[])
            .where((e) => e.id == idEtape)
            .firstOrNull;

    return Scaffold(
      appBar: BarreEcran(
        titre: t.journalEtapeTitre,
        sousTitre: etape == null
            ? t.journalEtapeSousTitre
            : t.etapeTitre(etape.id),
      ),
      body: ListView(
        padding: EdgeInsets.fromLTRB(
          Jetons.margeMobile,
          Jetons.margeMobile,
          Jetons.margeMobile,
          racine ? espaceBarreBasse : 24,
        ),
        children: [
          if (etape != null) ...[
            CarteEtape(etape),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _Chiffre(
                    icone: PhosphorIconsRegular.clock,
                    valeur: formaterDuree(etape.dureePointee(DateTime.now())),
                    libelle: t.dureePointee,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _Chiffre(
                    icone: PhosphorIconsRegular.listChecks,
                    valeur: '${evenements.length}',
                    libelle: t.evenementsTraces,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
          ],
          if (evenements.isEmpty)
            EtatVide(
              icone: PhosphorIconsRegular.clockCounterClockwise,
              titre: t.aucunEvenement,
              texte: t.aucunEvenementAide,
            )
          else
            Carte(
              child: Column(
                children: [
                  for (final (rang, evenement) in evenements.indexed)
                    Apparition(
                      rang: rang,
                      child: IntrinsicHeight(
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Column(
                              children: [
                                Container(
                                  width: 12,
                                  height: 12,
                                  margin: const EdgeInsets.only(top: 4),
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: tonEvenement(
                                      evenement.type,
                                    ).texte(p),
                                  ),
                                ),
                                if (rang < evenements.length - 1)
                                  Expanded(
                                    child: Container(
                                      width: 2,
                                      color: p.bordure,
                                    ),
                                  ),
                              ],
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Padding(
                                padding: const EdgeInsets.only(bottom: 16),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Text(
                                          DateFormat.MMMd(
                                            langue,
                                          ).add_Hm().format(evenement.date),
                                          style: TextStyle(
                                            color: p.texteSecondaire,
                                            fontSize: 12.5,
                                            fontFeatures: const [
                                              FontFeature.tabularFigures(),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Pastille(
                                          libelle: libelleEvenement(
                                            t,
                                            evenement.type,
                                          ),
                                          ton: tonEvenement(evenement.type),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 4),
                                    if (idEtape == null)
                                      Text(
                                        '#${evenement.idEtape} · ${evenement.libelleEtape}',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w700,
                                          color: p.texte,
                                          height: 1.3,
                                        ),
                                      ),
                                    Text(
                                      [
                                        evenement.nomAuteur,
                                        if (evenement.detail != null)
                                          evenement.detail!,
                                      ].join(' · '),
                                      style: TextStyle(
                                        color: p.texteSecondaire,
                                        fontSize: 13,
                                        height: 1.35,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          if (evenements.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              t.journalNonModifiable,
              textAlign: TextAlign.center,
              style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
            ),
          ],
        ],
      ),
    );
  }
}

class _Chiffre extends StatelessWidget {
  const _Chiffre({
    required this.icone,
    required this.valeur,
    required this.libelle,
  });

  final IconData icone;
  final String valeur;
  final String libelle;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Carte(
      padding: const EdgeInsets.all(14),
      rayon: Jetons.rayonBloc,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icone, size: 20, color: p.accent),
          const SizedBox(height: 6),
          Text(
            valeur,
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w800,
              color: p.sombre ? p.texte : Jetons.marine,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
          Text(
            libelle,
            style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
          ),
        ],
      ),
    );
  }
}
