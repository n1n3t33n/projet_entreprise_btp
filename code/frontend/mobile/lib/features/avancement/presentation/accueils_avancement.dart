import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/boutons.dart';
import '../../../components/surfaces.dart';
import '../../../core/navigation/onglet_role.dart';
import '../../../core/navigation/transitions.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../auth/domain/profil_utilisateur.dart';
import '../../shell/presentation/coquille.dart';
import '../../stock/application/etat_stock.dart';
import '../../stock/presentation/accueils_stock.dart';
import '../../stock/presentation/ecran_validation_stock.dart';
import '../application/etat_avancement.dart';
import '../data/donnees_demo.dart';
import '../domain/modeles.dart';
import 'ecrans_etapes.dart';
import 'ecrans_suivi.dart';
import 'elements_avancement.dart';

/// Carte d'avancement d'un ensemble d'étapes : pourcentage et répartition.
class _CarteProgression extends StatelessWidget {
  const _CarteProgression({
    required this.titre,
    required this.etapes,
    this.onOuvrir,
  });

  final String titre;
  final List<EtapeTravaux> etapes;
  final VoidCallback? onOuvrir;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    int compte(StatutEtape s) => etapes.where((e) => e.statut == s).length;
    final faites =
        compte(StatutEtape.validee) + compte(StatutEtape.termineeDeclaree);
    final part = etapes.isEmpty ? 0.0 : faites / etapes.length;
    return Carte(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      titre,
                      style: TextStyle(
                        fontSize: 19,
                        fontWeight: FontWeight.w800,
                        color: p.sombre ? p.texte : Jetons.marine,
                      ),
                    ),
                    Text(
                      lotDemo,
                      style: TextStyle(color: p.texteSecondaire, fontSize: 13),
                    ),
                  ],
                ),
              ),
              Pastille(
                libelle: t.pourcentRealise((part * 100).round()),
                ton: Ton.info,
              ),
            ],
          ),
          const SizedBox(height: 12),
          BarreProgression(valeur: part),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: ChiffreCle(
                  valeur: compte(StatutEtape.aFaire),
                  libelle: t.etapeAFaire,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ChiffreCle(
                  valeur: compte(StatutEtape.enCours),
                  libelle: t.etapeEnCours,
                  ton: Ton.info,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ChiffreCle(
                  valeur: faites,
                  libelle: t.etapesFaites,
                  ton: Ton.succes,
                ),
              ),
            ],
          ),
          if (onOuvrir != null) ...[
            const SizedBox(height: 12),
            BoutonPrincipal(
              libelle: t.ouvrirFicheRoute,
              icone: PhosphorIconsRegular.clipboardText,
              iconeFin: PhosphorIconsBold.arrowRight,
              onPressed: onOuvrir,
            ),
          ],
        ],
      ),
    );
  }
}

/// Liste courte d'étapes sous un titre, chacune ouvrant son détail.
class _ListeEtapes extends StatelessWidget {
  const _ListeEtapes({
    required this.titre,
    required this.etapes,
    this.icone,
    this.vide,
  });

  final String titre;
  final IconData? icone;
  final List<EtapeTravaux> etapes;
  final String? vide;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TitreSection(
          titre,
          icone: icone,
          complement: etapes.isEmpty
              ? null
              : Pastille(libelle: '${etapes.length}'),
        ),
        const SizedBox(height: 10),
        if (etapes.isEmpty && vide != null)
          Text(vide!, style: TextStyle(color: p.texteSecondaire)),
        for (final etape in etapes) ...[
          CarteEtape(
            etape,
            onTap: () => ouvrirEcran<void>(context, EcranEtape(id: etape.id)),
          ),
          const SizedBox(height: 10),
        ],
      ],
    );
  }
}

/// Accueil du technicien (maquette A2) : sa fiche de route du jour.
class AccueilTechnicien extends ConsumerWidget {
  const AccueilTechnicien({required this.profil, super.key});

  final ProfilUtilisateur profil;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final etapes = ref.watch(etapesProvider);
    final enCours = etapes
        .where((e) => e.statut == StatutEtape.enCours)
        .firstOrNull;
    final prochaines = etapes
        .where(
          (e) =>
              e.statut == StatutEtape.enCours ||
              e.statut == StatutEtape.aFaire ||
              e.statut == StatutEtape.bloquee,
        )
        .toList();
    final cible = enCours ?? prochaines.firstOrNull;

    return TableauDeBord(
      profil: profil,
      role: RoleTerrain.technicien,
      sousTitre: lotDemo,
      blocs: [
        _CarteProgression(
          titre: t.maFicheDuJour,
          etapes: etapes,
          onOuvrir: () => ouvrirEcran<void>(context, const EcranFicheRoute()),
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: TuileAction(
                icone: PhosphorIconsRegular.timer,
                libelle: t.pointageRapide,
                onTap: cible == null
                    ? null
                    : () =>
                          ouvrirEcran<void>(context, EcranEtape(id: cible.id)),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: TuileAction(
                icone: PhosphorIconsRegular.warningOctagon,
                libelle: t.declarerBlocage,
                ton: Ton.danger,
                onTap: cible == null
                    ? null
                    : () => ouvrirEcran<void>(
                        context,
                        EcranBlocage(idEtape: cible.id),
                      ),
              ),
            ),
          ],
        ),
        _ListeEtapes(
          titre: t.prochainesEtapes,
          icone: PhosphorIconsRegular.listChecks,
          etapes: prochaines,
          vide: t.aucuneEtapeAide,
        ),
      ],
    );
  }
}

/// Accueil du chef de chantier (maquette A3) : ce qui attend sa décision.
class AccueilChef extends ConsumerWidget {
  const AccueilChef({required this.profil, super.key});

  final ProfilUtilisateur profil;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final sorties = ref.watch(sortiesAValiderProvider);
    final etapes = ref.watch(etapesAValiderProvider);
    final toutes = ref.watch(etapesProvider);
    final bloquees = toutes
        .where((e) => e.statut == StatutEtape.bloquee)
        .toList();
    final alertes = ref.watch(alertesStockProvider);

    return TableauDeBord(
      profil: profil,
      role: RoleTerrain.chefChantier,
      sousTitre: lotDemo,
      blocs: [
        Carte(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TitreSection(
                t.aValiderPriorite,
                icone: PhosphorIconsRegular.sealCheck,
                complement: Pastille(
                  libelle: t.nombreActions(sorties.length + etapes.length),
                  ton: sorties.length + etapes.length == 0
                      ? Ton.succes
                      : Ton.alerte,
                ),
              ),
              const SizedBox(height: 12),
              _LigneDecision(
                icone: PhosphorIconsRegular.signOut,
                titre: t.sortiesAValider,
                detail: t.sortiesAValiderDetail,
                nombre: sorties.length,
                onTap: () =>
                    ouvrirEcran<void>(context, const EcranValidationStock()),
              ),
              const SizedBox(height: 8),
              _LigneDecision(
                icone: PhosphorIconsRegular.checkSquare,
                titre: t.etapesAControler,
                detail: t.etapesAControlerDetail,
                nombre: etapes.length,
                onTap: () => ouvrirEcran<void>(context, const EcranControles()),
              ),
            ],
          ),
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Carte(
                onTap: () =>
                    NavigationOnglets.of(context).allerVers(OngletRole.stock),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const TuileIcone(icone: PhosphorIconsRegular.package),
                    const SizedBox(height: 10),
                    Text(
                      t.stockMagasin,
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: p.texte,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Pastille(
                      libelle: '${alertes.length} ${t.sousSeuil}',
                      ton: alertes.isEmpty ? Ton.succes : Ton.alerte,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Carte(
                onTap: () =>
                    NavigationOnglets.of(context).allerVers(OngletRole.fiches),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const TuileIcone(icone: PhosphorIconsRegular.clipboardText),
                    const SizedBox(height: 10),
                    Text(
                      t.ficheRouteTitre,
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: p.texte,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Pastille(
                      libelle: t.nombreEtapes(toutes.length),
                      ton: Ton.info,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
        _ListeEtapes(
          titre: t.blocagesPrioritaires,
          icone: PhosphorIconsRegular.warningOctagon,
          etapes: bloquees,
          vide: t.aucunBlocage,
        ),
      ],
    );
  }
}

class _LigneDecision extends StatelessWidget {
  const _LigneDecision({
    required this.icone,
    required this.titre,
    required this.detail,
    required this.nombre,
    required this.onTap,
  });

  final IconData icone;
  final String titre;
  final String detail;
  final int nombre;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final ton = nombre == 0 ? Ton.succes : Ton.alerte;
    return Appui(
      onTap: onTap,
      echelle: 0.985,
      child: Bloc(
        couleur: ton.fond(p),
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Icon(icone, color: ton.texte(p)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    titre,
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: p.texte,
                    ),
                  ),
                  Text(
                    detail,
                    style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                  ),
                ],
              ),
            ),
            Pastille(libelle: '$nombre', ton: ton, pleine: nombre > 0),
            const SizedBox(width: 4),
            Icon(
              PhosphorIconsRegular.caretRight,
              size: 18,
              color: p.texteAttenue,
            ),
          ],
        ),
      ),
    );
  }
}

/// Accueil du responsable technique (maquette A5) : visas et synthèse, en
/// portée allégée (aucune saisie).
class AccueilResponsable extends ConsumerWidget {
  const AccueilResponsable({required this.profil, super.key});

  final ProfilUtilisateur profil;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final aValider = ref.watch(etapesAValiderProvider);
    final toutes = ref.watch(etapesProvider);
    final corps = {for (final e in toutes) e.corpsEtat}.toList();

    return TableauDeBord(
      profil: profil,
      role: RoleTerrain.responsableTechnique,
      sousTitre: t.supervisionTravaux,
      blocs: [
        Carte(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TitreSection(
                t.visasTechniques,
                icone: PhosphorIconsRegular.sealCheck,
                complement: Pastille(
                  libelle: t.nombreEtapes(aValider.length),
                  ton: aValider.isEmpty ? Ton.succes : Ton.alerte,
                ),
              ),
              const SizedBox(height: 12),
              if (aValider.isEmpty)
                Text(
                  t.aucunControleAide,
                  style: TextStyle(color: p.texteSecondaire),
                ),
              for (final etape in aValider.take(3)) ...[
                Bloc(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      Pastille(libelle: '#${etape.id}', ton: Ton.info),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              etape.libelle,
                              style: TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 13.5,
                                color: p.texte,
                              ),
                            ),
                            Text(
                              etape.zone,
                              style: TextStyle(
                                color: p.texteSecondaire,
                                fontSize: 12.5,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
              ],
              if (aValider.isNotEmpty)
                BoutonPrincipal(
                  libelle: t.examinerEtapes,
                  icone: PhosphorIconsRegular.checkSquare,
                  iconeFin: PhosphorIconsBold.arrowRight,
                  onPressed: () =>
                      ouvrirEcran<void>(context, const EcranControles()),
                ),
            ],
          ),
        ),
        Carte(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TitreSection(
                t.syntheseChantier,
                icone: PhosphorIconsRegular.chartBar,
              ),
              const SizedBox(height: 12),
              for (final nom in corps) ...[
                Builder(
                  builder: (_) {
                    final lot = toutes
                        .where((e) => e.corpsEtat == nom)
                        .toList();
                    final faites = lot
                        .where((e) => e.statut == StatutEtape.validee)
                        .length;
                    final part = lot.isEmpty ? 0.0 : faites / lot.length;
                    return Column(
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                nom,
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: p.texte,
                                ),
                              ),
                            ),
                            Text(
                              '${(part * 100).round()} %',
                              style: TextStyle(
                                fontWeight: FontWeight.w800,
                                color: p.accent,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        BarreProgression(valeur: part),
                        const SizedBox(height: 4),
                        Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            t.etapesValideesSur(faites, lot.length),
                            style: TextStyle(
                              color: p.texteSecondaire,
                              fontSize: 12.5,
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                      ],
                    );
                  },
                ),
              ],
              BoutonSecondaire(
                libelle: t.journalEtapeTitre,
                icone: PhosphorIconsRegular.clockCounterClockwise,
                compact: true,
                onPressed: () =>
                    ouvrirEcran<void>(context, const EcranJournalEtape()),
              ),
            ],
          ),
        ),
        Bloc(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const TuileIcone(
                icone: PhosphorIconsRegular.desktop,
                ton: Ton.neutre,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      t.outilsPosteFixe,
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: p.texte,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      t.outilsPosteFixeAide,
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
        ),
      ],
    );
  }
}
