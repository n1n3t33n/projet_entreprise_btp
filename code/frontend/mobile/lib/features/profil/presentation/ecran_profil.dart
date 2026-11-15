import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/en_tetes.dart';
import '../../../components/logo_schiavone.dart';
import '../../../components/saisie.dart';
import '../../../components/surfaces.dart';
import '../../../core/navigation/onglet_role.dart';
import '../../../core/preferences/preferences.dart';
import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../l10n/traductions.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../../auth/domain/profil_utilisateur.dart';
import '../../shell/presentation/barre_navigation.dart';
import '../../shell/presentation/racines.dart';

/// Profil de l'opérateur : identité, préférences d'affichage (langue, thème),
/// accès à la synchronisation et sécurité de l'appareil.
class EcranProfil extends ConsumerWidget {
  const EcranProfil({required this.profil, required this.role, super.key});

  final ProfilUtilisateur profil;
  final RoleTerrain role;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final p = context.palette;
    final t = context.t;
    final preferences = ref.watch(preferencesProvider);
    final controleur = ref.read(preferencesProvider.notifier);

    return Column(
      children: [
        FondFacade(
          child: SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(
                Jetons.espace3,
                14,
                Jetons.espace3,
                22,
              ),
              child: Row(
                children: [
                  AvatarInitiales(
                    profil.nomComplet,
                    taille: 60,
                    surMarine: true,
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          profil.nomComplet,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${libelleRole(t, role)} · ${profil.perimetre}',
                          style: const TextStyle(
                            color: Color(0xFFC9D9EA),
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
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
              Apparition(
                child: Carte(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      TitreSection(
                        t.profilLangue,
                        icone: PhosphorIconsRegular.translate,
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          for (final langue in languesDisponibles)
                            PuceChoix(
                              libelle: _nomLangue(langue),
                              selectionnee: preferences.langue == langue,
                              onTap: () => controleur.definirLangue(langue),
                            ),
                        ],
                      ),
                      const SizedBox(height: Jetons.espace4),
                      TitreSection(
                        t.profilTheme,
                        icone: PhosphorIconsRegular.circleHalf,
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          for (final mode in ThemeMode.values)
                            PuceChoix(
                              libelle: _nomTheme(t, mode),
                              icone: _iconeTheme(mode),
                              selectionnee: preferences.theme == mode,
                              onTap: () => controleur.definirTheme(mode),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Apparition(
                rang: 1,
                child: Carte(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Column(
                    children: [
                      _Ligne(
                        icone: PhosphorIconsRegular.arrowsClockwise,
                        titre: t.synchroTitre,
                        detail: t.profilSynchroAide,
                        onTap: () => ouvrirSynchronisation(context),
                      ),
                      Divider(color: p.bordure, indent: 68),
                      _Ligne(
                        icone: PhosphorIconsRegular.lock,
                        titre: t.profilVerrouiller,
                        detail: t.profilVerrouillerAide,
                        onTap: () => ref
                            .read(controleurAuthProvider.notifier)
                            .verrouiller(),
                      ),
                      Divider(color: p.bordure, indent: 68),
                      _Ligne(
                        icone: PhosphorIconsRegular.signOut,
                        titre: t.retirerCompteAction,
                        detail: t.profilRetirerAide,
                        ton: Ton.danger,
                        onTap: () => _confirmerRetrait(context, ref),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Apparition(
                rang: 2,
                child: Carte(
                  child: Column(
                    children: [
                      LogoSchiavone(hauteur: 64, surPlaque: p.sombre),
                      const SizedBox(height: 14),
                      Text(
                        'ChantierSync',
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 16,
                          color: p.sombre ? p.texte : Jetons.marine,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        t.profilAPropos(ref.watch(idAppareilProvider)),
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: p.texteSecondaire,
                          fontSize: 12.5,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _nomLangue(Locale langue) => switch (langue.languageCode) {
    'en' => 'English',
    'it' => 'Italiano',
    _ => 'Français',
  };

  String _nomTheme(Traductions t, ThemeMode mode) => switch (mode) {
    ThemeMode.system => t.themeSysteme,
    ThemeMode.light => t.themeClair,
    ThemeMode.dark => t.themeSombre,
  };

  IconData _iconeTheme(ThemeMode mode) => switch (mode) {
    ThemeMode.system => PhosphorIconsRegular.deviceMobile,
    ThemeMode.light => PhosphorIconsRegular.sun,
    ThemeMode.dark => PhosphorIconsRegular.moon,
  };

  Future<void> _confirmerRetrait(BuildContext context, WidgetRef ref) async {
    final t = context.t;
    final enAttente = ref.read(nombreEnAttenteProvider);
    final confirme = await showDialog<bool>(
      context: context,
      builder: (contexte) => AlertDialog(
        title: Text(t.retirerCompteTitre),
        content: Text(
          enAttente > 0
              ? '${t.retirerCompteTexte}\n\n${t.retirerCompteAlerte(enAttente)}'
              : t.retirerCompteTexte,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(contexte).pop(false),
            child: Text(t.annuler),
          ),
          TextButton(
            style: TextButton.styleFrom(
              foregroundColor: contexte.palette.danger,
            ),
            onPressed: () => Navigator.of(contexte).pop(true),
            child: Text(t.retirerCompteAction),
          ),
        ],
      ),
    );
    if (confirme == true) {
      await ref.read(controleurAuthProvider.notifier).revoquer();
    }
  }
}

class _Ligne extends StatelessWidget {
  const _Ligne({
    required this.icone,
    required this.titre,
    required this.detail,
    required this.onTap,
    this.ton = Ton.info,
  });

  final IconData icone;
  final String titre;
  final String detail;
  final VoidCallback onTap;
  final Ton ton;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Semantics(
      button: true,
      child: Appui(
        onTap: onTap,
        echelle: 0.985,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          child: Row(
            children: [
              TuileIcone(icone: icone, ton: ton, taille: 42),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      titre,
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: ton == Ton.danger ? p.danger : p.texte,
                      ),
                    ),
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
              Icon(
                PhosphorIconsRegular.caretRight,
                color: p.texteAttenue,
                size: 18,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
