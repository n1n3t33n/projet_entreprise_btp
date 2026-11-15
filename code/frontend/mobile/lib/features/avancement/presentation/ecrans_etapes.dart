import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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
import '../../stock/presentation/elements_stock.dart' show ZoneAction, notifier;
import '../application/etat_avancement.dart';
import '../data/depot_avancement.dart';
import '../data/donnees_demo.dart';
import '../domain/modeles.dart';
import 'ecrans_suivi.dart';
import 'elements_avancement.dart';

enum _FiltreEtape { toutes, enCours, aFaire, bloquees }

/// Fiche de route (écran 11) : progression du jour et interventions ordonnées.
class EcranFicheRoute extends ConsumerStatefulWidget {
  const EcranFicheRoute({this.racine = false, super.key});

  final bool racine;

  @override
  ConsumerState<EcranFicheRoute> createState() => _EcranFicheRouteState();
}

class _EcranFicheRouteState extends ConsumerState<EcranFicheRoute> {
  _FiltreEtape _filtre = _FiltreEtape.toutes;

  bool _correspond(EtapeTravaux e, _FiltreEtape filtre) => switch (filtre) {
    _FiltreEtape.toutes => true,
    _FiltreEtape.enCours => e.statut == StatutEtape.enCours,
    _FiltreEtape.aFaire => e.statut == StatutEtape.aFaire,
    _FiltreEtape.bloquees => e.statut == StatutEtape.bloquee,
  };

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final etapes = ref.watch(etapesProvider);
    final terminees = etapes
        .where(
          (e) =>
              e.statut == StatutEtape.validee ||
              e.statut == StatutEtape.termineeDeclaree,
        )
        .length;
    final visibles = etapes.where((e) => _correspond(e, _filtre)).toList();
    int compte(StatutEtape s) => etapes.where((e) => e.statut == s).length;

    return Scaffold(
      appBar: BarreEcran(titre: t.ficheRouteTitre, sousTitre: lotDemo),
      body: ListView(
        padding: EdgeInsets.fromLTRB(
          Jetons.margeMobile,
          Jetons.margeMobile,
          Jetons.margeMobile,
          widget.racine ? espaceBarreBasse : 24,
        ),
        children: [
          Carte(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        t.progressionJour,
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w700,
                          color: p.sombre ? p.texte : Jetons.marine,
                        ),
                      ),
                    ),
                    Text(
                      '${etapes.isEmpty ? 0 : (terminees * 100 / etapes.length).round()} %',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w800,
                        color: p.sombre ? p.texte : Jetons.marine,
                      ),
                    ),
                  ],
                ),
                Text(
                  t.etapesTerminees(terminees, etapes.length),
                  style: TextStyle(color: p.texteSecondaire, fontSize: 13),
                ),
                const SizedBox(height: 10),
                BarreProgression(
                  valeur: etapes.isEmpty ? 0 : terminees / etapes.length,
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _Compteur(
                        compte(StatutEtape.enCours),
                        t.etapeEnCours,
                        Ton.info,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _Compteur(
                        compte(StatutEtape.bloquee),
                        t.etapeBloquee,
                        Ton.danger,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _Compteur(
                        compte(StatutEtape.termineeDeclaree),
                        t.etapeADeclaree,
                        Ton.alerte,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                for (final (filtre, libelle, ton) in [
                  (_FiltreEtape.toutes, t.filtreToutes, Ton.marine),
                  (_FiltreEtape.enCours, t.etapeEnCours, Ton.info),
                  (_FiltreEtape.aFaire, t.etapeAFaire, Ton.neutre),
                  (_FiltreEtape.bloquees, t.etapeBloquee, Ton.danger),
                ]) ...[
                  PuceChoix(
                    libelle: libelle,
                    ton: ton,
                    compteur: etapes
                        .where((e) => _correspond(e, filtre))
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
              icone: PhosphorIconsRegular.clipboardText,
              titre: t.aucuneEtape,
              texte: t.aucuneEtapeAide,
            ),
          for (final (rang, etape) in visibles.indexed) ...[
            Apparition(
              key: ValueKey(etape.id),
              rang: rang,
              child: CarteEtape(
                etape,
                onTap: () =>
                    ouvrirEcran<void>(context, EcranEtape(id: etape.id)),
              ),
            ),
            const SizedBox(height: 10),
          ],
        ],
      ),
    );
  }
}

class _Compteur extends StatelessWidget {
  const _Compteur(this.valeur, this.libelle, this.ton);

  final int valeur;
  final String libelle;
  final Ton ton;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Bloc(
      couleur: valeur > 0 ? ton.fond(p) : null,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
      child: Column(
        children: [
          Text(
            '$valeur',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w800,
              color: ton.texte(p),
            ),
          ),
          Text(
            libelle,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: p.texteSecondaire,
              fontSize: 11.5,
              height: 1.2,
            ),
          ),
        ],
      ),
    );
  }
}

/// Détail d'une étape et pointage (écran 12) : chronomètre, métré, contrôles
/// de la gamme opératoire, puis déclaration de fin.
class EcranEtape extends ConsumerStatefulWidget {
  const EcranEtape({required this.id, super.key});

  final String id;

  @override
  ConsumerState<EcranEtape> createState() => _EcranEtapeState();
}

class _EcranEtapeState extends ConsumerState<EcranEtape> {
  num? _metre;
  List<bool>? _controles;
  bool _enCours = false;

  Future<void> _agir(
    Future<void> Function(DepotAvancement depot) action, {
    String? message,
  }) async {
    setState(() => _enCours = true);
    try {
      await action(ref.read(depotAvancementProvider));
      rafraichirAvancement(ref);
      HapticFeedback.selectionClick();
      if (mounted && message != null) notifier(context, message);
    } on TransitionInterditeException {
      if (mounted) notifier(context, context.t.actionImpossible);
    } finally {
      if (mounted) {
        setState(() {
          _enCours = false;
          _metre = null;
          _controles = null;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final operateur = ref.watch(operateurProvider);
    final etape =
        (ref.watch(toutesEtapesProvider).valueOrNull ?? const <EtapeTravaux>[])
            .where((e) => e.id == widget.id)
            .firstOrNull;
    if (etape == null || operateur == null) {
      return Scaffold(
        appBar: BarreEcran(titre: t.etapeTitre(widget.id)),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    final role = operateur.role;
    final auteur = operateur.profil;
    final execute = role.peutExecuterEtapes;
    final enCours = etape.statut == StatutEtape.enCours;
    final metre = _metre ?? etape.metreFait;
    final controles = _controles ?? etape.controlesFaits;
    final modifie =
        metre != etape.metreFait ||
        !_identiques(controles, etape.controlesFaits);

    Widget? action;
    String? mention;
    if (execute && etape.statut == StatutEtape.aFaire) {
      action = BoutonPrincipal(
        libelle: t.demarrerEtape,
        icone: PhosphorIconsBold.play,
        enChargement: _enCours,
        onPressed: () => _agir((d) => d.demarrer(etape.id, auteur)),
      );
    } else if (execute && enCours && modifie) {
      action = BoutonPrincipal(
        libelle: t.validerPointage('$metre / ${etape.metreCible}'),
        icone: PhosphorIconsBold.checkCircle,
        enChargement: _enCours,
        onPressed: () => _agir(
          (d) => d.pointer(
            etape.id,
            metreFait: metre,
            controlesFaits: controles,
            auteur: auteur,
          ),
          message: t.pointageEnregistre,
        ),
      );
    } else if (execute && enCours) {
      action = BoutonPrincipal(
        libelle: t.terminerEtape,
        icone: PhosphorIconsBold.flagCheckered,
        enChargement: _enCours,
        onPressed: etape.peutEtreTerminee
            ? () => _agir(
                (d) => d.terminer(etape.id, auteur),
                message: t.etapeDeclaree,
              )
            : null,
      );
      mention = etape.peutEtreTerminee
          ? t.terminerMention
          : t.terminerConditions;
    } else if (execute && etape.statut == StatutEtape.bloquee) {
      action = BoutonPrincipal(
        libelle: t.leverBlocage,
        icone: PhosphorIconsBold.lockOpen,
        enChargement: _enCours,
        onPressed: () => _agir((d) => d.leverBlocage(etape.id, auteur)),
      );
    }

    return Scaffold(
      appBar: BarreEcran(
        titre: t.etapeTitre(etape.id),
        sousTitre: etape.corpsEtat,
        actions: [
          BoutonIcone(
            icone: PhosphorIconsRegular.clockCounterClockwise,
            libelle: t.journalEtapeTitre,
            onPressed: () => ouvrirEcran<void>(
              context,
              EcranJournalEtape(idEtape: etape.id),
            ),
          ),
        ],
      ),
      bottomNavigationBar: action == null
          ? null
          : ZoneAction(mention: mention, child: action),
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
                          etape.libelle,
                          style: TextStyle(
                            fontSize: 19,
                            fontWeight: FontWeight.w800,
                            height: 1.2,
                            color: p.sombre ? p.texte : Jetons.marine,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      PastilleEtape(etape.statut),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    etape.detail,
                    style: TextStyle(color: p.texteSecondaire, height: 1.35),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _Info(
                          PhosphorIconsRegular.mapPin,
                          t.localisation,
                          etape.zone,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _Info(
                          PhosphorIconsRegular.usersThree,
                          etape.equipe,
                          etape.nomResponsable,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          if (etape.statut == StatutEtape.bloquee && etape.blocage != null) ...[
            const SizedBox(height: 12),
            Bloc(
              couleur: p.dangerFond,
              bordure: p.danger.withValues(alpha: 0.3),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(iconeNature(etape.blocage!.nature), color: p.danger),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      [
                        libelleNature(t, etape.blocage!.nature),
                        libelleGravite(t, etape.blocage!.gravite),
                        if (etape.blocage!.designationArticle != null)
                          etape.blocage!.designationArticle!,
                        if (etape.blocage!.observations != null)
                          etape.blocage!.observations!,
                      ].join(' · '),
                      style: TextStyle(
                        color: p.danger,
                        fontWeight: FontWeight.w600,
                        height: 1.35,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
          if (etape.statut != StatutEtape.aFaire) ...[
            const SizedBox(height: 12),
            Apparition(
              rang: 1,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(Jetons.rayonCarte),
                child: FondFacade(
                  rayonBas: Jetons.rayonCarte,
                  child: Padding(
                    padding: const EdgeInsets.all(Jetons.espace3),
                    child: Column(
                      children: [
                        Text(
                          etape.pointageActif
                              ? t.pointageActif
                              : t.pointageArrete,
                          style: const TextStyle(
                            color: Jetons.ciel,
                            fontWeight: FontWeight.w700,
                            fontSize: 12.5,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Chrono(
                          etape: etape,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 40,
                            fontWeight: FontWeight.w800,
                            height: 1.1,
                          ),
                        ),
                        if (execute && enCours) ...[
                          const SizedBox(height: 12),
                          BoutonSecondaire(
                            libelle: etape.pointageActif
                                ? t.mettreEnPause
                                : t.reprendre,
                            icone: etape.pointageActif
                                ? PhosphorIconsBold.pause
                                : PhosphorIconsBold.play,
                            ton: Ton.neutre,
                            compact: true,
                            onPressed: _enCours
                                ? null
                                : () => _agir(
                                    (d) => d.basculerPointage(etape.id, auteur),
                                  ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
          const SizedBox(height: 12),
          Apparition(
            rang: 2,
            child: Carte(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TitreSection(
                    t.avancementMetre,
                    icone: PhosphorIconsRegular.ruler,
                    complement: Pastille(
                      libelle: t.cible(
                        '${etape.metreCible} ${etape.uniteMetre}',
                      ),
                      ton: Ton.info,
                    ),
                  ),
                  const SizedBox(height: 12),
                  BarreProgression(
                    valeur: etape.metreCible <= 0
                        ? 0
                        : metre / etape.metreCible,
                    ton: tonStatutEtape(etape.statut),
                  ),
                  const SizedBox(height: 12),
                  if (execute && enCours)
                    SelecteurQuantite(
                      valeur: metre,
                      onChange: (v) => setState(() => _metre = v),
                      unite: etape.uniteMetre,
                      max: etape.metreCible,
                      mention: t.surCible('${etape.metreCible}'),
                      raccourcis: const [1, 2],
                      libelleMax: t.solde,
                    )
                  else
                    Text(
                      '${etape.metreFait} / ${etape.metreCible} ${etape.uniteMetre}',
                      style: TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 18,
                        color: p.texte,
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Apparition(
            rang: 3,
            child: Carte(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TitreSection(
                    t.gammeSecurite,
                    icone: PhosphorIconsRegular.shieldCheck,
                  ),
                  const SizedBox(height: 10),
                  for (final (i, controle) in etape.controles.indexed) ...[
                    Semantics(
                      checked: controles[i],
                      child: Appui(
                        onTap: execute && enCours
                            ? () => setState(
                                () => _controles = [
                                  for (final (j, v) in controles.indexed)
                                    j == i ? !v : v,
                                ],
                              )
                            : null,
                        echelle: 0.985,
                        child: Bloc(
                          couleur: controles[i] ? p.succesFond : null,
                          padding: const EdgeInsets.all(12),
                          child: Row(
                            children: [
                              Icon(
                                controles[i]
                                    ? PhosphorIconsFill.checkCircle
                                    : PhosphorIconsRegular.circle,
                                color: controles[i] ? p.succes : p.texteAttenue,
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  controle,
                                  style: TextStyle(
                                    fontWeight: FontWeight.w600,
                                    color: p.texte,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                  ],
                ],
              ),
            ),
          ),
          if (execute &&
              (etape.statut == StatutEtape.enCours ||
                  etape.statut == StatutEtape.aFaire)) ...[
            const SizedBox(height: 12),
            BoutonSecondaire(
              libelle: t.declarerBlocage,
              icone: PhosphorIconsRegular.warningOctagon,
              ton: Ton.danger,
              contour: true,
              onPressed: () =>
                  ouvrirEcran<void>(context, EcranBlocage(idEtape: etape.id)),
            ),
          ],
          if (role.peutReaffecter && etape.statut != StatutEtape.validee) ...[
            const SizedBox(height: 10),
            BoutonSecondaire(
              libelle: t.reaffecterEtape,
              icone: PhosphorIconsRegular.usersThree,
              onPressed: () => ouvrirEcran<void>(
                context,
                EcranReaffectation(idEtape: etape.id),
              ),
            ),
          ],
        ],
      ),
    );
  }

  bool _identiques(List<bool> a, List<bool> b) {
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}

class _Info extends StatelessWidget {
  const _Info(this.icone, this.libelle, this.valeur);

  final IconData icone;
  final String libelle;
  final String valeur;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Bloc(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          Icon(icone, size: 20, color: p.accent),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  libelle,
                  style: TextStyle(color: p.texteSecondaire, fontSize: 12),
                ),
                Text(
                  valeur,
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                    color: p.texte,
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
