import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/bandeau_synchro.dart';
import '../../../components/boutons.dart';
import '../../../components/en_tetes.dart';
import '../../../components/surfaces.dart';
import '../../../core/navigation/onglet_role.dart';
import '../../../core/navigation/transitions.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../auth/domain/profil_utilisateur.dart';
import '../../shell/presentation/barre_navigation.dart';
import '../../shell/presentation/coquille.dart';
import '../../shell/presentation/racines.dart';
import '../application/etat_stock.dart';
import '../data/donnees_demo.dart';
import '../domain/modeles.dart';
import 'ecran_inventaire.dart';
import 'ecran_mouvement.dart';
import 'ecran_registre.dart';
import 'ecran_validation_stock.dart';
import 'elements_stock.dart';

/// Structure commune des tableaux de bord : en-tête du rôle, bandeau de
/// synchronisation, puis les blocs du métier révélés en cascade.
class TableauDeBord extends StatelessWidget {
  const TableauDeBord({
    required this.profil,
    required this.role,
    required this.blocs,
    this.sousTitre,
    super.key,
  });

  final ProfilUtilisateur profil;
  final RoleTerrain role;
  final String? sousTitre;
  final List<Widget> blocs;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      children: [
        EnTeteRole(
          surTitre: surTitreChantier(profil),
          titre: '${libelleRole(t, role)} · ${profil.nomComplet}',
          sousTitre: sousTitre,
          actions: [
            BoutonIcone(
              icone: PhosphorIconsRegular.user,
              libelle: t.ongletProfil,
              surMarine: true,
              onPressed: () =>
                  NavigationOnglets.of(context).allerVers(OngletRole.profil),
            ),
          ],
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              Jetons.margeMobile,
              Jetons.margeMobile,
              Jetons.margeMobile,
              espaceBarreBasse,
            ),
            children: [
              BandeauSynchro(
                onSynchroniser: () => ouvrirSynchronisation(context),
              ),
              for (final (rang, bloc) in blocs.indexed) ...[
                const SizedBox(height: 12),
                Apparition(rang: rang, child: bloc),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

/// Chiffre clé d'un tableau de bord : grand nombre + libellé.
class ChiffreCle extends StatelessWidget {
  const ChiffreCle({
    required this.valeur,
    required this.libelle,
    this.ton = Ton.marine,
    this.surligne = false,
    super.key,
  });

  final num valeur;
  final String libelle;
  final Ton ton;

  /// Vrai pour un fond teinté (chiffre à surveiller).
  final bool surligne;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Bloc(
      couleur: surligne ? ton.fond(p) : null,
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          NombreAnime(
            valeur: valeur,
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w800,
              height: 1.1,
              color: ton.texte(p),
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
          const SizedBox(height: 2),
          Text(
            libelle,
            style: TextStyle(
              color: p.texteSecondaire,
              fontSize: 12.5,
              height: 1.25,
            ),
          ),
        ],
      ),
    );
  }
}

/// Carte « Alertes & priorités » : les articles les plus urgents.
class CarteAlertesStock extends ConsumerWidget {
  const CarteAlertesStock({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final alertes = ref.watch(alertesStockProvider);
    return Carte(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TitreSection(
            t.alertesPriorites,
            icone: PhosphorIconsRegular.warning,
            complement: alertes.isEmpty
                ? null
                : Pastille(libelle: '${alertes.length}', ton: Ton.danger),
          ),
          const SizedBox(height: 12),
          if (alertes.isEmpty)
            Text(
              t.aucuneAlerteAide,
              style: TextStyle(color: p.texteSecondaire),
            ),
          for (final article in alertes.take(3)) ...[
            Appui(
              onTap: () => ouvrirEcran<void>(
                context,
                EcranFicheArticle(code: article.code),
              ),
              echelle: 0.985,
              child: Bloc(
                couleur: tonNiveau(article.niveau).fond(p),
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            article.designation,
                            style: TextStyle(
                              fontWeight: FontWeight.w700,
                              color: p.texte,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '${t.stockRestant} ${formaterQuantite(article.quantite, article.unite)} · '
                            '${t.seuilMini(formaterQuantite(article.seuilMinimal))}',
                            style: TextStyle(
                              color: p.texteSecondaire,
                              fontSize: 12.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    PastilleNiveau(article),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
          ],
          if (alertes.length > 3)
            TextButton(
              onPressed: () => ouvrirEcran<void>(
                context,
                const EcranRegistre(filtreAlertes: true),
              ),
              child: Text(t.voirToutesAlertes(alertes.length)),
            ),
        ],
      ),
    );
  }
}

/// Accueil du magasinier (maquette A1) : état du magasin, alertes, raccourcis.
class AccueilMagasinier extends ConsumerWidget {
  const AccueilMagasinier({required this.profil, super.key});

  final ProfilUtilisateur profil;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final articles =
        ref.watch(articlesProvider).valueOrNull ?? const <ArticleStock>[];
    final alertes = ref.watch(alertesStockProvider);
    final inventaire = ref.watch(inventaireProvider).valueOrNull;

    void saisir(ModeSaisie mode) =>
        ouvrirEcran<void>(context, EcranMouvement(mode: mode));

    return TableauDeBord(
      profil: profil,
      role: RoleTerrain.magasinier,
      blocs: [
        Carte(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  const TuileIcone(
                    icone: PhosphorIconsRegular.package,
                    taille: 48,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t.stockMagasin,
                          style: TextStyle(
                            fontSize: 19,
                            fontWeight: FontWeight.w800,
                            color: p.sombre ? p.texte : Jetons.marine,
                          ),
                        ),
                        Text(
                          magasinPilote,
                          style: TextStyle(
                            color: p.texteSecondaire,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  Expanded(
                    child: ChiffreCle(
                      valeur: articles.length,
                      libelle: t.references,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ChiffreCle(
                      valeur: alertes.length,
                      libelle: t.sousSeuil,
                      ton: Ton.alerte,
                      surligne: alertes.isNotEmpty,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              BoutonSecondaire(
                libelle: t.consulterStock,
                icone: PhosphorIconsRegular.arrowRight,
                compact: true,
                onPressed: () =>
                    ouvrirEcran<void>(context, const EcranRegistre()),
              ),
            ],
          ),
        ),
        const CarteAlertesStock(),
        Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TitreSection(t.raccourcis),
            const SizedBox(height: 10),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: TuileAction(
                    icone: PhosphorIconsRegular.signOut,
                    libelle: t.sortieTitre,
                    ton: Ton.marine,
                    onTap: () => saisir(ModeSaisie.sortie),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TuileAction(
                    icone: PhosphorIconsRegular.truck,
                    libelle: t.receptionTitre,
                    onTap: () => saisir(ModeSaisie.reception),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TuileAction(
                    icone: PhosphorIconsRegular.listChecks,
                    libelle: t.inventaireTitre,
                    ton: Ton.alerte,
                    onTap: () =>
                        ouvrirEcran<void>(context, const EcranInventaire()),
                  ),
                ),
              ],
            ),
          ],
        ),
        if (inventaire != null && inventaire.statut == StatutInventaire.enCours)
          _CarteInventaire(
            inventaire: inventaire,
            libelleAction: t.reprendreComptage,
          ),
        BoutonPrincipal(
          libelle: t.nouveauMouvement,
          icone: PhosphorIconsBold.plus,
          onPressed: () => ouvrirNouveauMouvement(context),
        ),
      ],
    );
  }
}

/// Accueil du gestionnaire de stock (maquette A4) : visas, inventaire, alertes.
class AccueilGestionnaire extends ConsumerWidget {
  const AccueilGestionnaire({required this.profil, super.key});

  final ProfilUtilisateur profil;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final articles =
        ref.watch(articlesProvider).valueOrNull ?? const <ArticleStock>[];
    final mouvements =
        ref.watch(mouvementsProvider).valueOrNull ?? const <MouvementStock>[];
    final alertes = ref.watch(alertesStockProvider);
    final demandes = ref.watch(sortiesAValiderProvider);
    final inventaire = ref.watch(inventaireProvider).valueOrNull;
    final hier = DateTime.now().subtract(const Duration(hours: 24));

    return TableauDeBord(
      profil: profil,
      role: RoleTerrain.gestionnaireStock,
      blocs: [
        Carte(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                t.stockMagasin,
                style: TextStyle(
                  fontSize: 19,
                  fontWeight: FontWeight.w800,
                  color: p.sombre ? p.texte : Jetons.marine,
                ),
              ),
              Text(
                magasinPilote,
                style: TextStyle(color: p.texteSecondaire, fontSize: 13),
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  Expanded(
                    child: ChiffreCle(
                      valeur: articles.length,
                      libelle: t.references,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ChiffreCle(
                      valeur: mouvements
                          .where((m) => m.date.isAfter(hier))
                          .length,
                      libelle: t.mouvements24h,
                      ton: Ton.info,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ChiffreCle(
                      valeur: alertes.length,
                      libelle: t.sousSeuil,
                      ton: Ton.alerte,
                      surligne: alertes.isNotEmpty,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              BoutonPrincipal(
                libelle: t.consulterRegistre,
                icone: PhosphorIconsRegular.magnifyingGlass,
                iconeFin: PhosphorIconsBold.arrowRight,
                onPressed: () =>
                    ouvrirEcran<void>(context, const EcranRegistre()),
              ),
            ],
          ),
        ),
        Carte(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TitreSection(
                t.sortiesAValider,
                icone: PhosphorIconsRegular.sealCheck,
                complement: Pastille(
                  libelle: t.nombreDemandes(demandes.length),
                  ton: demandes.isEmpty ? Ton.succes : Ton.alerte,
                ),
              ),
              const SizedBox(height: 12),
              if (demandes.isEmpty)
                Text(
                  t.aucuneDemandeAide,
                  style: TextStyle(color: p.texteSecondaire),
                ),
              for (final demande in demandes.take(2)) ...[
                Bloc(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      AvatarInitiales(demande.nomAuteur, taille: 38),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${formaterQuantite(demande.quantite, demande.unite)} · ${demande.designation}',
                              style: TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 13.5,
                                color: p.texte,
                              ),
                            ),
                            Text(
                              '${demande.nomAuteur} · ${tempsRelatif(context, demande.date)}',
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
              if (demandes.isNotEmpty)
                BoutonSecondaire(
                  libelle: t.examinerSorties(demandes.length),
                  icone: PhosphorIconsRegular.sealCheck,
                  ton: Ton.alerte,
                  compact: true,
                  onPressed: () {
                    final ouvert = NavigationOnglets.of(
                      context,
                    ).allerVers(OngletRole.aValider);
                    if (!ouvert) {
                      ouvrirEcran<void>(context, const EcranValidationStock());
                    }
                  },
                ),
            ],
          ),
        ),
        if (inventaire != null)
          _CarteInventaire(
            inventaire: inventaire,
            libelleAction: inventaire.statut == StatutInventaire.aValider
                ? t.validerInventaire
                : t.suivreInventaire,
          ),
        const CarteAlertesStock(),
      ],
    );
  }
}

class _CarteInventaire extends StatelessWidget {
  const _CarteInventaire({
    required this.inventaire,
    required this.libelleAction,
  });

  final Inventaire inventaire;
  final String libelleAction;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    return Carte(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TitreSection(
            t.inventaireTitre,
            icone: PhosphorIconsRegular.listChecks,
          ),
          const SizedBox(height: 4),
          Text(
            inventaire.zone,
            style: TextStyle(color: p.texteSecondaire, fontSize: 13),
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
                  style: TextStyle(color: p.texteSecondaire, fontSize: 13),
                ),
              ),
              Text(
                '${(inventaire.progression * 100).round()} %',
                style: TextStyle(fontWeight: FontWeight.w800, color: p.accent),
              ),
            ],
          ),
          const SizedBox(height: 8),
          BarreProgression(valeur: inventaire.progression),
          const SizedBox(height: 12),
          BoutonSecondaire(
            libelle: libelleAction,
            icone: PhosphorIconsRegular.play,
            compact: true,
            onPressed: () =>
                ouvrirEcran<void>(context, const EcranInventaire()),
          ),
        ],
      ),
    );
  }
}
