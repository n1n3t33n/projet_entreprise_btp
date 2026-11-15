import 'dart:async';

import 'package:flutter/material.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/surfaces.dart';
import '../../../l10n/traductions.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../domain/modeles.dart';

// Éléments d'interface partagés par les écrans d'avancement.

String libelleStatutEtape(Traductions t, StatutEtape statut) =>
    switch (statut) {
      StatutEtape.aFaire => t.etapeAFaire,
      StatutEtape.enCours => t.etapeEnCours,
      StatutEtape.termineeDeclaree => t.etapeADeclaree,
      StatutEtape.validee => t.etapeValidee,
      StatutEtape.bloquee => t.etapeBloquee,
    };

Ton tonStatutEtape(StatutEtape statut) => switch (statut) {
  StatutEtape.aFaire => Ton.neutre,
  StatutEtape.enCours => Ton.info,
  StatutEtape.termineeDeclaree => Ton.alerte,
  StatutEtape.validee => Ton.succes,
  StatutEtape.bloquee => Ton.danger,
};

IconData iconeStatutEtape(StatutEtape statut) => switch (statut) {
  StatutEtape.aFaire => PhosphorIconsRegular.circleDashed,
  StatutEtape.enCours => PhosphorIconsRegular.playCircle,
  StatutEtape.termineeDeclaree => PhosphorIconsRegular.hourglassMedium,
  StatutEtape.validee => PhosphorIconsRegular.sealCheck,
  StatutEtape.bloquee => PhosphorIconsRegular.warningOctagon,
};

String libelleEvenement(Traductions t, TypeEvenement type) => switch (type) {
  TypeEvenement.demarrage => t.evDemarrage,
  TypeEvenement.pointage => t.evPointage,
  TypeEvenement.pause => t.evPause,
  TypeEvenement.reprise => t.evReprise,
  TypeEvenement.blocage => t.evBlocage,
  TypeEvenement.leveeBlocage => t.evLeveeBlocage,
  TypeEvenement.fin => t.evFin,
  TypeEvenement.validation => t.evValidation,
  TypeEvenement.rejet => t.evRejet,
  TypeEvenement.reaffectation => t.evReaffectation,
};

Ton tonEvenement(TypeEvenement type) => switch (type) {
  TypeEvenement.blocage || TypeEvenement.rejet => Ton.danger,
  TypeEvenement.validation || TypeEvenement.leveeBlocage => Ton.succes,
  TypeEvenement.pause => Ton.neutre,
  TypeEvenement.fin || TypeEvenement.reaffectation => Ton.alerte,
  _ => Ton.info,
};

String libelleNature(Traductions t, NatureBlocage nature) => switch (nature) {
  NatureBlocage.ruptureMateriau => t.blocageRupture,
  NatureBlocage.panneEngin => t.blocagePanne,
  NatureBlocage.intemperies => t.blocageIntemperies,
  NatureBlocage.nonConformite => t.blocageNonConformite,
  NatureBlocage.accesBloque => t.blocageAcces,
};

IconData iconeNature(NatureBlocage nature) => switch (nature) {
  NatureBlocage.ruptureMateriau => PhosphorIconsRegular.package,
  NatureBlocage.panneEngin => PhosphorIconsRegular.wrench,
  NatureBlocage.intemperies => PhosphorIconsRegular.cloudRain,
  NatureBlocage.nonConformite => PhosphorIconsRegular.sealWarning,
  NatureBlocage.accesBloque => PhosphorIconsRegular.barricade,
};

String libelleGravite(Traductions t, GraviteBlocage gravite) =>
    switch (gravite) {
      GraviteBlocage.arretTotal => t.graviteArret,
      GraviteBlocage.ralenti => t.graviteRalenti,
      GraviteBlocage.alerte => t.graviteAlerte,
    };

String libelleRetard(Traductions t, RetardEstime retard) => switch (retard) {
  RetardEstime.deuxHeures => t.retardDeuxHeures,
  RetardEstime.demiJournee => t.retardDemiJournee,
  RetardEstime.unJourEtPlus => t.retardUnJour,
};

/// Durée au format 01:24:18.
String formaterDuree(Duration duree) {
  String deux(int n) => n.toString().padLeft(2, '0');
  return '${deux(duree.inHours)}:${deux(duree.inMinutes % 60)}:${deux(duree.inSeconds % 60)}';
}

class PastilleEtape extends StatelessWidget {
  const PastilleEtape(this.statut, {super.key});

  final StatutEtape statut;

  @override
  Widget build(BuildContext context) => Pastille(
    libelle: libelleStatutEtape(context.t, statut),
    icone: iconeStatutEtape(statut),
    ton: tonStatutEtape(statut),
  );
}

/// Chronomètre du pointage : avance chaque seconde tant que la session est
/// active. Les chiffres sont à chasse fixe pour ne pas faire bouger le texte.
class Chrono extends StatefulWidget {
  const Chrono({required this.etape, required this.style, super.key});

  final EtapeTravaux etape;
  final TextStyle style;

  @override
  State<Chrono> createState() => _ChronoState();
}

class _ChronoState extends State<Chrono> {
  Timer? _minuteur;

  @override
  void initState() {
    super.initState();
    _regler();
  }

  @override
  void didUpdateWidget(Chrono ancien) {
    super.didUpdateWidget(ancien);
    _regler();
  }

  void _regler() {
    _minuteur?.cancel();
    _minuteur = widget.etape.pointageActif
        ? Timer.periodic(const Duration(seconds: 1), (_) => setState(() {}))
        : null;
  }

  @override
  void dispose() {
    _minuteur?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Text(
    formaterDuree(widget.etape.dureePointee(DateTime.now())),
    style: widget.style.copyWith(
      fontFeatures: const [FontFeature.tabularFigures()],
    ),
  );
}

/// Carte d'une étape dans une liste : numéro, titre, zone, statut, avancement.
class CarteEtape extends StatelessWidget {
  const CarteEtape(this.etape, {this.onTap, this.pied, super.key});

  final EtapeTravaux etape;
  final VoidCallback? onTap;

  /// Zone d'actions facultative sous la carte.
  final Widget? pied;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final ton = tonStatutEtape(etape.statut);
    final active = etape.statut == StatutEtape.enCours;
    final bloquee = etape.statut == StatutEtape.bloquee;
    return Carte(
      onTap: onTap,
      bordure: active
          ? p.accent
          : (bloquee ? p.danger.withValues(alpha: 0.5) : null),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Pastille(
                libelle: '#${etape.id}',
                ton: bloquee ? Ton.danger : Ton.neutre,
              ),
              const SizedBox(width: 8),
              if (etape.horaire != null)
                Expanded(
                  child: Text(
                    etape.horaire!,
                    style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                  ),
                )
              else
                const Spacer(),
              PastilleEtape(etape.statut),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            etape.libelle,
            style: TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 16,
              height: 1.25,
              color: p.sombre ? p.texte : Jetons.marine,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '${etape.zone} · ${etape.equipe}',
            style: TextStyle(
              color: p.texteSecondaire,
              fontSize: 13,
              height: 1.3,
            ),
          ),
          if (bloquee && etape.blocage != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  iconeNature(etape.blocage!.nature),
                  size: 16,
                  color: p.danger,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    [
                      libelleNature(t, etape.blocage!.nature),
                      if (etape.blocage!.designationArticle != null)
                        etape.blocage!.designationArticle!,
                    ].join(' · '),
                    style: TextStyle(
                      color: p.danger,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
          ],
          if (etape.statut != StatutEtape.aFaire) ...[
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: BarreProgression(valeur: etape.progression, ton: ton),
                ),
                const SizedBox(width: 10),
                Text(
                  '${etape.metreFait} / ${etape.metreCible} ${etape.uniteMetre}',
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 12.5,
                    color: p.texte,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ],
            ),
          ],
          if (pied != null) ...[const SizedBox(height: 12), pied!],
        ],
      ),
    );
  }
}
